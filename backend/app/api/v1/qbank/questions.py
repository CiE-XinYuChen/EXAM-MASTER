"""
Question management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from app.core.database import get_qbank_db, get_main_db
from app.core.security import get_current_user
from app.models.question_models import Question, QuestionOption, QuestionBank, QuestionVersion
from app.models.question_models_v2 import QuestionV2, QuestionBankV2
from app.models.user_models import User, UserBankPermission
from app.models.activation import UserBankAccess
from app.schemas.question_schemas import (
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    QuestionOptionCreate
)
import json
from datetime import datetime

router = APIRouter()


def check_bank_permission(
    bank_id: str,
    permission: str,
    user: User,
    db: Session
) -> bool:
    """Check if user has permission for a question bank"""
    if user.role == "admin":
        return True

    # Check UserBankPermission (legacy)
    perm = db.query(UserBankPermission).filter(
        UserBankPermission.user_id == user.id,
        UserBankPermission.bank_id == bank_id
    ).first()

    if perm:
        if permission == "read":
            return perm.permission in ["read", "write", "admin"]
        elif permission == "write":
            return perm.permission in ["write", "admin"]
        elif permission == "admin":
            return perm.permission == "admin"

    # Check UserBankAccess (new activation system)
    access = db.query(UserBankAccess).filter(
        UserBankAccess.user_id == user.id,
        UserBankAccess.bank_id == bank_id,
        UserBankAccess.is_active == True
    ).first()

    if access:
        # Check if not expired
        if access.expire_at is None or access.expire_at > datetime.utcnow():
            # UserBankAccess grants read permission
            if permission == "read":
                return True

    return False


@router.get("/", response_model=List[QuestionResponse], tags=["❓ Question Management"])
async def get_questions(
    bank_id: Optional[str] = None,
    type: Optional[str] = None,
    difficulty: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Get list of questions with filters"""
    # Query from QuestionV2 (new table)
    query = qbank_db.query(QuestionV2)

    # Filter by bank_id if provided
    if bank_id:
        # Check permission for the bank using V2 model
        bank = qbank_db.query(QuestionBankV2).filter(QuestionBankV2.id == bank_id).first()
        if not bank:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question bank not found"
            )

        # Ensure is_public has a default value
        if bank.is_public is None:
            bank.is_public = False

        if not bank.is_public and not check_bank_permission(bank_id, "read", current_user, main_db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No permission to access this question bank"
            )

        query = query.filter(QuestionV2.bank_id == bank_id)

    # Apply filters
    if type:
        query = query.filter(QuestionV2.type == type)
    if difficulty:
        query = query.filter(QuestionV2.difficulty == difficulty)
    if category:
        query = query.filter(QuestionV2.category == category)
    if search:
        query = query.filter(QuestionV2.stem.contains(search))

    # TODO: Filter by tags (requires JSON search)

    questions = query.offset(skip).limit(limit).all()

    # Filter questions based on bank permissions
    accessible_questions = []
    for question in questions:
        bank = qbank_db.query(QuestionBankV2).filter(QuestionBankV2.id == question.bank_id).first()
        if bank:
            if bank.is_public is None:
                bank.is_public = False
            if bank.is_public or check_bank_permission(question.bank_id, "read", current_user, main_db):
                accessible_questions.append(question)

    return accessible_questions


@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED, tags=["❓ Question Management"])
async def create_question(
    question_data: QuestionCreate,
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Create a new question with options"""
    # Check bank exists and user has write permission
    bank = qbank_db.query(QuestionBank).filter(QuestionBank.id == question_data.bank_id).first()
    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question bank not found"
        )
    
    if not check_bank_permission(question_data.bank_id, "write", current_user, main_db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to add questions to this bank"
        )
    
    # Generate question ID
    question_id = str(uuid.uuid4())
    
    # Get next question number
    max_number = qbank_db.query(Question).filter(
        Question.bank_id == question_data.bank_id
    ).count()
    
    # Create question
    question_dict = question_data.model_dump(exclude={"options"})
    question = Question(
        id=question_id,
        question_number=max_number + 1,
        **question_dict
    )
    
    qbank_db.add(question)
    
    # Create options
    for idx, option_data in enumerate(question_data.options):
        option = QuestionOption(
            id=str(uuid.uuid4()),
            question_id=question_id,
            option_label=option_data.option_label,
            option_content=option_data.option_content,
            option_format=option_data.option_format,
            is_correct=option_data.is_correct,
            sort_order=option_data.sort_order if option_data.sort_order else idx
        )
        qbank_db.add(option)
    
    # Create version record
    version = QuestionVersion(
        id=str(uuid.uuid4()),
        question_id=question_id,
        version_number=1,
        change_type="create",
        change_data=json.dumps(question_data.model_dump(), ensure_ascii=False),
        changed_by=current_user.id
    )
    qbank_db.add(version)
    
    qbank_db.commit()
    qbank_db.refresh(question)
    
    return question


@router.get("/{question_id}", response_model=QuestionResponse, tags=["❓ Question Management"])
async def get_question(
    question_id: str,
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Get question details"""
    question = qbank_db.query(Question).filter(Question.id == question_id).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Check bank permission
    bank = qbank_db.query(QuestionBank).filter(QuestionBank.id == question.bank_id).first()
    if not bank.is_public and not check_bank_permission(question.bank_id, "read", current_user, main_db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to access this question"
        )
    
    return question


@router.put("/{question_id}", response_model=QuestionResponse, tags=["❓ Question Management"])
async def update_question(
    question_id: str,
    question_update: QuestionUpdate,
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Update question"""
    question = qbank_db.query(Question).filter(Question.id == question_id).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Check permission
    if not check_bank_permission(question.bank_id, "write", current_user, main_db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to modify this question"
        )
    
    # Store old data for version history
    old_data = {
        "stem": question.stem,
        "stem_format": question.stem_format,
        "type": question.type,
        "difficulty": question.difficulty,
        "category": question.category,
        "tags": question.tags,
        "explanation": question.explanation,
        "explanation_format": question.explanation_format,
        "metadata": question.meta_data
    }
    
    # Update fields
    update_data = question_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(question, field, value)
    
    # Create version record
    version_count = qbank_db.query(QuestionVersion).filter(
        QuestionVersion.question_id == question_id
    ).count()
    
    version = QuestionVersion(
        id=str(uuid.uuid4()),
        question_id=question_id,
        version_number=version_count + 1,
        change_type="update",
        change_data=json.dumps({
            "old": old_data,
            "new": update_data
        }, ensure_ascii=False),
        changed_by=current_user.id
    )
    qbank_db.add(version)
    
    qbank_db.commit()
    qbank_db.refresh(question)
    
    return question


@router.delete("/{question_id}", response_model=dict, tags=["❓ Question Management"])
async def delete_question(
    question_id: str,
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Delete question"""
    question = qbank_db.query(Question).filter(Question.id == question_id).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Check permission
    if not check_bank_permission(question.bank_id, "write", current_user, main_db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to delete this question"
        )
    
    # Delete question (cascades to options, resources, versions)
    qbank_db.delete(question)
    qbank_db.commit()
    
    return {"message": "Question deleted successfully"}


@router.post("/{question_id}/options", response_model=dict, status_code=status.HTTP_201_CREATED, tags=["❓ Question Management"])
async def add_option(
    question_id: str,
    option_data: QuestionOptionCreate,
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Add a new option to an existing question"""
    question = qbank_db.query(Question).filter(Question.id == question_id).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Check permission
    if not check_bank_permission(question.bank_id, "write", current_user, main_db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to modify this question"
        )
    
    # Generate next option label if not provided
    if not option_data.option_label:
        existing_options = qbank_db.query(QuestionOption).filter(
            QuestionOption.question_id == question_id
        ).order_by(QuestionOption.sort_order).all()
        
        # Generate next label (A, B, C, ... Z, AA, AB, ...)
        if not existing_options:
            option_data.option_label = "A"
        else:
            last_label = existing_options[-1].option_label
            if last_label == "Z":
                option_data.option_label = "AA"
            elif len(last_label) == 2 and last_label[1] == "Z":
                option_data.option_label = chr(ord(last_label[0]) + 1) + "A"
            elif len(last_label) == 2:
                option_data.option_label = last_label[0] + chr(ord(last_label[1]) + 1)
            else:
                option_data.option_label = chr(ord(last_label) + 1)
    
    # Create option
    option = QuestionOption(
        id=str(uuid.uuid4()),
        question_id=question_id,
        **option_data.model_dump()
    )
    
    qbank_db.add(option)
    qbank_db.commit()
    
    return {"message": "Option added successfully", "option_id": option.id}


@router.post("/{question_id}/duplicate", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED, tags=["❓ Question Management"])
async def duplicate_question(
    question_id: str,
    target_bank_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Duplicate a question to the same or different bank"""
    # Get source question
    source_question = qbank_db.query(Question).filter(Question.id == question_id).first()
    
    if not source_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source question not found"
        )
    
    # Check read permission on source
    source_bank = qbank_db.query(QuestionBank).filter(
        QuestionBank.id == source_question.bank_id
    ).first()
    
    if not source_bank.is_public and not check_bank_permission(
        source_question.bank_id, "read", current_user, main_db
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to access source question"
        )
    
    # Determine target bank
    target_bank_id = target_bank_id or source_question.bank_id
    
    # Check write permission on target
    if not check_bank_permission(target_bank_id, "write", current_user, main_db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to add questions to target bank"
        )
    
    # Create new question
    new_question_id = str(uuid.uuid4())
    new_question = Question(
        id=new_question_id,
        bank_id=target_bank_id,
        question_number=qbank_db.query(Question).filter(
            Question.bank_id == target_bank_id
        ).count() + 1,
        stem=source_question.stem + " (Copy)",
        stem_format=source_question.stem_format,
        type=source_question.type,
        difficulty=source_question.difficulty,
        category=source_question.category,
        tags=source_question.tags,
        explanation=source_question.explanation,
        explanation_format=source_question.explanation_format,
        meta_data=source_question.meta_data
    )
    
    qbank_db.add(new_question)
    
    # Duplicate options
    source_options = qbank_db.query(QuestionOption).filter(
        QuestionOption.question_id == question_id
    ).all()
    
    for source_option in source_options:
        new_option = QuestionOption(
            id=str(uuid.uuid4()),
            question_id=new_question_id,
            option_label=source_option.option_label,
            option_content=source_option.option_content,
            option_format=source_option.option_format,
            is_correct=source_option.is_correct,
            sort_order=source_option.sort_order
        )
        qbank_db.add(new_option)
    
    qbank_db.commit()
    qbank_db.refresh(new_question)
    
    return new_question