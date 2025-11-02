"""
Import/Export API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session
from typing import Optional
import os
import tempfile

from app.core.database import get_qbank_db
from app.core.security import get_current_user
from app.models.user_models import User
from app.models.question_models_v2 import QuestionBankV2
from app.services.question_bank_service import QuestionBankService

router = APIRouter()

# Import Operations
@router.post("/import/csv", tags=["📥 Data Import"])
async def import_csv(
    bank_id: str = Form(...),
    file: UploadFile = File(...),
    merge_duplicates: bool = Form(True),
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Import questions from CSV file"""
    # Check file type
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    # Check bank exists and user has permission
    bank = qbank_db.query(QuestionBankV2).filter(QuestionBankV2.id == bank_id).first()
    if not bank:
        raise HTTPException(status_code=404, detail="Question bank not found")
    
    if bank.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        service = QuestionBankService(qbank_db)
        imported_count = service.import_questions(bank_id, tmp_path)
        
        return {
            "success": True,
            "imported_count": imported_count,
            "bank_id": bank_id
        }
    finally:
        # Clean up temp file
        os.unlink(tmp_path)


@router.post("/import/json", tags=["📥 Data Import"])
async def import_json(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Import question bank from JSON file"""
    if not file.filename.lower().endswith('.json'):
        raise HTTPException(status_code=400, detail="Only JSON files are supported")
    
    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        service = QuestionBankService(qbank_db)
        new_bank = service.import_question_bank(tmp_path, current_user.id)
        
        return {
            "success": True,
            "bank_id": new_bank.id,
            "bank_name": new_bank.name,
            "question_count": new_bank.total_questions
        }
    finally:
        # Clean up temp file
        os.unlink(tmp_path)


@router.post("/import/zip", tags=["📥 Data Import"])
async def import_zip(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Import question bank from ZIP archive"""
    if not file.filename.lower().endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only ZIP files are supported")
    
    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        service = QuestionBankService(qbank_db)
        new_bank = service.import_question_bank(tmp_path, current_user.id)
        
        return {
            "success": True,
            "bank_id": new_bank.id,
            "bank_name": new_bank.name,
            "question_count": new_bank.total_questions
        }
    finally:
        # Clean up temp file
        os.unlink(tmp_path)


# Export Operations
@router.get("/export/{bank_id}/csv", tags=["📤 Data Export"])
async def export_csv(
    bank_id: str,
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Export question bank to CSV format"""
    service = QuestionBankService(qbank_db)
    bank = service.get_question_bank(bank_id)
    
    if not bank:
        raise HTTPException(status_code=404, detail="Question bank not found")
    
    # Check permissions
    if not bank.is_public and bank.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    if not bank.allow_download and bank.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Download not allowed")
    
    export_path = service.export_question_bank(bank_id, format="csv")
    
    if not os.path.exists(export_path):
        raise HTTPException(status_code=500, detail="Export failed")
    
    return FileResponse(
        export_path,
        media_type='text/csv',
        filename=f"{bank.name}_export.csv"
    )


@router.get("/export/{bank_id}/json", tags=["📤 Data Export"])
async def export_json(
    bank_id: str,
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Export question bank to JSON format"""
    service = QuestionBankService(qbank_db)
    bank = service.get_question_bank(bank_id)
    
    if not bank:
        raise HTTPException(status_code=404, detail="Question bank not found")
    
    # Check permissions
    if not bank.is_public and bank.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    export_path = service.export_question_bank(bank_id, format="json")
    
    if not os.path.exists(export_path):
        raise HTTPException(status_code=500, detail="Export failed")
    
    return FileResponse(
        export_path,
        media_type='application/json',
        filename=f"{bank.name}_export.json"
    )


@router.get("/export/{bank_id}/zip", tags=["📤 Data Export"])
async def export_zip(
    bank_id: str,
    include_images: bool = Query(True),
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Export question bank to ZIP archive (with images)"""
    service = QuestionBankService(qbank_db)
    bank = service.get_question_bank(bank_id)
    
    if not bank:
        raise HTTPException(status_code=404, detail="Question bank not found")
    
    # Check permissions
    if not bank.is_public and bank.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    if not bank.allow_download and bank.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Download not allowed")
    
    export_path = service.export_question_bank(
        bank_id, 
        format="zip", 
        include_images=include_images
    )
    
    if not os.path.exists(export_path):
        raise HTTPException(status_code=500, detail="Export failed")
    
    return FileResponse(
        export_path,
        media_type='application/zip',
        filename=f"{bank.name}_export.zip"
    )


# Template Downloads
@router.get("/templates/csv", tags=["📋 Templates"])
async def download_csv_template():
    """Download CSV import template"""
    csv_content = """题号,题干,A,B,C,D,E,F,G,H,答案,难度,题型,解析
1,Python中哪个关键字用于定义函数？,def,func,function,define,,,,,A,easy,函数定义,def是Python中定义函数的关键字
2,以下哪些是Python的数据类型？,整数,字符串,函数,列表,字典,,,ABDE,medium,数据类型,Python支持多种数据类型
3,这是一个有多个选项的题目示例,选项A,选项B,选项C,选项D,选项E,选项F,选项G,选项H,ACFH,hard,多选,这个题目展示了超过4个选项的支持

说明：
1. 可以根据需要添加更多选项列（如I、J、K等），只需在表头添加相应列名
2. 未使用的选项列可以留空，导入时会自动忽略
3. 答案列填写正确选项的字母（如A、BC、ABCD等）
4. 难度可选：easy（简单）、medium（中等）、hard（困难）
5. 导出时会根据题库中最多的选项数自动调整列数
"""
    
    return Response(
        content=csv_content.encode('utf-8-sig'),
        media_type='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=question_import_template.csv'
        }
    )