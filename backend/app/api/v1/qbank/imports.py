"""
Import/Export endpoints for question banks
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
import uuid
import csv
import json
import io
from datetime import datetime
from pathlib import Path
import pandas as pd
from app.core.database import get_qbank_db, get_main_db
from app.core.security import get_current_user, get_current_teacher_user
from app.core.config import settings
from app.models.question_models import Question, QuestionOption, QuestionBank
from app.models.user_models import User, UserBankPermission
from app.schemas.question_schemas import ImportConfig, ImportResult

router = APIRouter()


def check_bank_write_permission(
    bank_id: str,
    user: User,
    main_db: Session
) -> bool:
    """Check if user has write permission for a question bank"""
    if user.role == "admin":
        return True
    
    perm = main_db.query(UserBankPermission).filter(
        UserBankPermission.user_id == user.id,
        UserBankPermission.bank_id == bank_id
    ).first()
    
    return perm and perm.permission in ["write", "admin"]


def parse_csv_question(row: dict, bank_id: str) -> tuple[Question, List[QuestionOption]]:
    """Parse a CSV row into Question and Option objects"""
    # Generate question ID
    question_id = str(uuid.uuid4())
    
    # Determine question type based on answer length
    answer = row.get("答案", "").strip()
    question_type = "single" if len(answer) == 1 else "multiple"
    
    # Create question
    question = Question(
        id=question_id,
        bank_id=bank_id,
        question_number=int(row.get("题号", 0)),
        stem=row.get("题干", ""),
        stem_format="text",
        type=question_type,
        difficulty=row.get("难度", "medium"),
        category=row.get("类别", row.get("题型", "")),
        tags=json.dumps([row.get("题型", "")], ensure_ascii=False) if row.get("题型") else None
    )
    
    # Create options
    options = []
    option_labels = ["A", "B", "C", "D", "E"]
    
    for idx, label in enumerate(option_labels):
        if label in row and row[label] and row[label].strip():
            option = QuestionOption(
                id=str(uuid.uuid4()),
                question_id=question_id,
                option_label=label,
                option_content=row[label].strip(),
                option_format="text",
                is_correct=(label in answer),
                sort_order=idx
            )
            options.append(option)
    
    return question, options


def parse_json_question(data: dict, bank_id: str) -> tuple[Question, List[QuestionOption]]:
    """Parse a JSON object into Question and Option objects"""
    question_id = str(uuid.uuid4())
    
    # Create question
    question = Question(
        id=question_id,
        bank_id=bank_id,
        question_number=data.get("number", 0),
        stem=data.get("stem", ""),
        stem_format=data.get("stem_format", "text"),
        type=data.get("type", "single"),
        difficulty=data.get("difficulty", "medium"),
        category=data.get("category", ""),
        tags=json.dumps(data.get("tags", []), ensure_ascii=False) if data.get("tags") else None,
        explanation=data.get("explanation", ""),
        explanation_format=data.get("explanation_format", "text")
    )
    
    # Create options
    options = []
    for idx, opt_data in enumerate(data.get("options", [])):
        option = QuestionOption(
            id=str(uuid.uuid4()),
            question_id=question_id,
            option_label=opt_data.get("label", chr(65 + idx)),  # A, B, C...
            option_content=opt_data.get("content", ""),
            option_format=opt_data.get("format", "text"),
            is_correct=opt_data.get("is_correct", False),
            sort_order=opt_data.get("sort_order", idx)
        )
        options.append(option)
    
    return question, options


@router.post("/csv", response_model=ImportResult)
async def import_csv(
    file: UploadFile = File(...),
    bank_id: str = Form(...),
    merge_duplicates: bool = Form(True),
    auto_create_bank: bool = Form(False),
    bank_name: Optional[str] = Form(None),
    current_user: User = Depends(get_current_teacher_user),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Import questions from CSV file (compatible with existing format)"""
    # Check file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file"
        )
    
    # Check or create bank
    bank = qbank_db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
    
    if not bank:
        if auto_create_bank and bank_name:
            # Create new bank
            bank = QuestionBank(
                id=bank_id,
                name=bank_name,
                description=f"Imported from {file.filename}",
                creator_id=current_user.id,
                version="1.0.0"
            )
            qbank_db.add(bank)
            
            # Grant admin permission
            permission = UserBankPermission(
                user_id=current_user.id,
                bank_id=bank_id,
                permission="admin",
                granted_by=current_user.id
            )
            main_db.add(permission)
            main_db.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question bank not found"
            )
    else:
        # Check permission
        if not check_bank_write_permission(bank_id, current_user, main_db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No permission to import to this question bank"
            )
    
    # Read CSV file
    try:
        content = await file.read()
        csv_file = io.StringIO(content.decode('utf-8-sig'))  # Handle BOM
        reader = csv.DictReader(csv_file)
        
        imported_count = 0
        failed_count = 0
        errors = []
        warnings = []
        
        for row_num, row in enumerate(reader, start=2):  # Start from 2 (header is 1)
            try:
                # Parse question and options
                question, options = parse_csv_question(row, bank_id)
                
                # Check for duplicates if merge_duplicates is False
                if not merge_duplicates:
                    existing = qbank_db.query(Question).filter(
                        Question.bank_id == bank_id,
                        Question.stem == question.stem
                    ).first()
                    
                    if existing:
                        warnings.append(f"Row {row_num}: Duplicate question skipped")
                        continue
                
                # Add to database
                qbank_db.add(question)
                for option in options:
                    qbank_db.add(option)
                
                imported_count += 1
                
            except Exception as e:
                failed_count += 1
                errors.append(f"Row {row_num}: {str(e)}")
        
        # Commit all changes
        qbank_db.commit()
        
        return ImportResult(
            success=True,
            imported_count=imported_count,
            failed_count=failed_count,
            errors=errors,
            warnings=warnings
        )
        
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File encoding error. Please ensure the file is UTF-8 encoded"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )


@router.post("/json", response_model=ImportResult)
async def import_json(
    file: UploadFile = File(...),
    bank_id: str = Form(...),
    merge_duplicates: bool = Form(True),
    current_user: User = Depends(get_current_teacher_user),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Import questions from JSON file"""
    # Check file type
    if not file.filename.endswith('.json'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a JSON file"
        )
    
    # Check bank and permission
    bank = qbank_db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question bank not found"
        )
    
    if not check_bank_write_permission(bank_id, current_user, main_db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to import to this question bank"
        )
    
    # Read JSON file
    try:
        content = await file.read()
        data = json.loads(content)
        
        # Support both single question and array of questions
        questions_data = data if isinstance(data, list) else [data]
        
        imported_count = 0
        failed_count = 0
        errors = []
        warnings = []
        
        for idx, q_data in enumerate(questions_data):
            try:
                # Parse question and options
                question, options = parse_json_question(q_data, bank_id)
                
                # Check for duplicates
                if not merge_duplicates:
                    existing = qbank_db.query(Question).filter(
                        Question.bank_id == bank_id,
                        Question.stem == question.stem
                    ).first()
                    
                    if existing:
                        warnings.append(f"Question {idx + 1}: Duplicate skipped")
                        continue
                
                # Add to database
                qbank_db.add(question)
                for option in options:
                    qbank_db.add(option)
                
                imported_count += 1
                
            except Exception as e:
                failed_count += 1
                errors.append(f"Question {idx + 1}: {str(e)}")
        
        # Commit all changes
        qbank_db.commit()
        
        return ImportResult(
            success=True,
            imported_count=imported_count,
            failed_count=failed_count,
            errors=errors,
            warnings=warnings
        )
        
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )


@router.post("/validate", response_model=dict)
async def validate_import_file(
    file: UploadFile = File(...),
    format: str = Form("auto_detect")
):
    """Validate an import file without actually importing"""
    # Detect format
    if format == "auto_detect":
        if file.filename.endswith('.csv'):
            format = "csv"
        elif file.filename.endswith('.json'):
            format = "json"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot detect file format. Please specify format parameter"
            )
    
    try:
        content = await file.read()
        
        if format == "csv":
            csv_file = io.StringIO(content.decode('utf-8-sig'))
            reader = csv.DictReader(csv_file)
            rows = list(reader)
            
            # Check required columns
            required_columns = ["题号", "题干", "答案"]
            missing_columns = [col for col in required_columns if col not in reader.fieldnames]
            
            if missing_columns:
                return {
                    "valid": False,
                    "format": "csv",
                    "errors": [f"Missing required columns: {', '.join(missing_columns)}"],
                    "row_count": 0
                }
            
            # Validate each row
            errors = []
            for idx, row in enumerate(rows, start=2):
                if not row.get("题干"):
                    errors.append(f"Row {idx}: Empty question stem")
                if not row.get("答案"):
                    errors.append(f"Row {idx}: Empty answer")
            
            return {
                "valid": len(errors) == 0,
                "format": "csv",
                "row_count": len(rows),
                "errors": errors[:10]  # Limit errors shown
            }
            
        elif format == "json":
            data = json.loads(content)
            questions_data = data if isinstance(data, list) else [data]
            
            errors = []
            for idx, q in enumerate(questions_data):
                if not q.get("stem"):
                    errors.append(f"Question {idx + 1}: Missing stem")
                if not q.get("options"):
                    errors.append(f"Question {idx + 1}: Missing options")
            
            return {
                "valid": len(errors) == 0,
                "format": "json",
                "question_count": len(questions_data),
                "errors": errors[:10]
            }
            
    except Exception as e:
        return {
            "valid": False,
            "format": format,
            "errors": [str(e)]
        }


@router.get("/export/{bank_id}")
async def export_question_bank(
    bank_id: str,
    format: str = "csv",
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Export question bank to CSV or JSON format"""
    # Check bank exists
    bank = qbank_db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question bank not found"
        )
    
    # Check permission (read permission is enough for export)
    if user.role != "admin":
        perm = main_db.query(UserBankPermission).filter(
            UserBankPermission.user_id == current_user.id,
            UserBankPermission.bank_id == bank_id
        ).first()
        
        if not perm and not bank.is_public:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No permission to export this question bank"
            )
    
    # Get all questions with options
    questions = qbank_db.query(Question).filter(
        Question.bank_id == bank_id
    ).order_by(Question.question_number).all()
    
    if format == "csv":
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(["题号", "题干", "A", "B", "C", "D", "E", "答案", "难度", "题型"])
        
        # Write questions
        for question in questions:
            options_dict = {opt.option_label: opt.option_content for opt in question.options}
            answer = "".join([opt.option_label for opt in question.options if opt.is_correct])
            
            writer.writerow([
                question.question_number,
                question.stem,
                options_dict.get("A", ""),
                options_dict.get("B", ""),
                options_dict.get("C", ""),
                options_dict.get("D", ""),
                options_dict.get("E", ""),
                answer,
                question.difficulty or "无",
                question.type or "未分类"
            ])
        
        # Return as downloadable file
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={bank.name}_export.csv"
            }
        )
        
    elif format == "json":
        # Create JSON structure
        export_data = {
            "bank_info": {
                "id": bank.id,
                "name": bank.name,
                "description": bank.description,
                "version": bank.version,
                "exported_at": datetime.now().isoformat()
            },
            "questions": []
        }
        
        for question in questions:
            q_data = {
                "number": question.question_number,
                "stem": question.stem,
                "stem_format": question.stem_format,
                "type": question.type,
                "difficulty": question.difficulty,
                "category": question.category,
                "tags": json.loads(question.tags) if question.tags else [],
                "explanation": question.explanation,
                "explanation_format": question.explanation_format,
                "options": [
                    {
                        "label": opt.option_label,
                        "content": opt.option_content,
                        "format": opt.option_format,
                        "is_correct": opt.is_correct,
                        "sort_order": opt.sort_order
                    }
                    for opt in sorted(question.options, key=lambda x: x.sort_order)
                ]
            }
            export_data["questions"].append(q_data)
        
        # Return as downloadable file
        return StreamingResponse(
            io.BytesIO(json.dumps(export_data, ensure_ascii=False, indent=2).encode('utf-8')),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={bank.name}_export.json"
            }
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid export format. Supported formats: csv, json"
        )