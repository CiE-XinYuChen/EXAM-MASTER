"""
Question Bank management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from app.core.database import get_qbank_db, get_main_db
from app.core.security import get_current_user, get_current_teacher_user
from app.models.question_models import QuestionBank, Question
from app.models.question_models_v2 import QuestionBankV2, QuestionV2
from app.models.user_models import User, UserBankPermission
from app.models.activation import UserBankAccess
from app.schemas.question_schemas import (
    QuestionBankCreate,
    QuestionBankUpdate,
    QuestionBankResponse
)
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


@router.get("/", response_model=List[QuestionBankResponse], tags=["📚 Bank Management"])
async def get_question_banks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[str] = None,
    is_public: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Get list of accessible question banks"""
    # Query from QuestionBankV2 (new table used by activation system)
    query = qbank_db.query(QuestionBankV2)

    # Filter by category if provided
    if category:
        query = query.filter(QuestionBankV2.category == category)

    # Filter by public status if provided
    if is_public is not None:
        query = query.filter(QuestionBankV2.is_public == is_public)

    banks = query.offset(skip).limit(limit).all()

    # Filter banks based on user permissions
    accessible_banks = []
    for bank in banks:
        if bank.is_public or check_bank_permission(bank.id, "read", current_user, main_db):
            # Add question count from V2 table
            bank.question_count = qbank_db.query(QuestionV2).filter(
                QuestionV2.bank_id == bank.id
            ).count()
            # Set metadata fields for compatibility
            if not hasattr(bank, 'metadata') or bank.metadata is None:
                bank.metadata = bank.meta_data
            accessible_banks.append(bank)

    return accessible_banks


@router.post("/", response_model=QuestionBankResponse, status_code=status.HTTP_201_CREATED, tags=["📚 Bank Management"])
async def create_question_bank(
    bank_data: QuestionBankCreate,
    current_user: User = Depends(get_current_teacher_user),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Create a new question bank (teacher/admin only)"""
    # Generate unique ID
    bank_id = str(uuid.uuid4())
    
    # Create question bank
    bank = QuestionBank(
        id=bank_id,
        **bank_data.model_dump(),
        creator_id=current_user.id,
        version="1.0.0"
    )
    
    qbank_db.add(bank)
    qbank_db.commit()
    qbank_db.refresh(bank)
    
    # Grant admin permission to creator
    permission = UserBankPermission(
        user_id=current_user.id,
        bank_id=bank_id,
        permission="admin",
        granted_by=current_user.id
    )
    
    main_db.add(permission)
    main_db.commit()
    
    bank.question_count = 0
    return bank


@router.get("/{bank_id}", response_model=QuestionBankResponse, tags=["📚 Bank Management"])
async def get_question_bank(
    bank_id: str,
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Get question bank details"""
    # Query from QuestionBankV2
    bank = qbank_db.query(QuestionBankV2).filter(QuestionBankV2.id == bank_id).first()

    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question bank not found"
        )

    # Check permission
    if not bank.is_public and not check_bank_permission(bank_id, "read", current_user, main_db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to access this question bank"
        )

    # Add question count from V2 table
    bank.question_count = qbank_db.query(QuestionV2).filter(
        QuestionV2.bank_id == bank_id
    ).count()

    # Set metadata fields for compatibility
    if not hasattr(bank, 'metadata') or bank.metadata is None:
        bank.metadata = bank.meta_data

    return bank


@router.put("/{bank_id}", response_model=QuestionBankResponse, tags=["📚 Bank Management"])
async def update_question_bank(
    bank_id: str,
    bank_update: QuestionBankUpdate,
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Update question bank"""
    bank = qbank_db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
    
    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question bank not found"
        )
    
    # Check permission
    if not check_bank_permission(bank_id, "write", current_user, main_db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to modify this question bank"
        )
    
    # Update fields
    update_data = bank_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bank, field, value)
    
    qbank_db.commit()
    qbank_db.refresh(bank)
    
    # Add question count
    bank.question_count = qbank_db.query(Question).filter(
        Question.bank_id == bank_id
    ).count()
    
    return bank


@router.delete("/{bank_id}", response_model=dict, tags=["📚 Bank Management"])
async def delete_question_bank(
    bank_id: str,
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Delete question bank"""
    bank = qbank_db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
    
    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question bank not found"
        )
    
    # Check permission
    if not check_bank_permission(bank_id, "admin", current_user, main_db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to delete this question bank"
        )
    
    # Delete bank (cascades to questions, options, resources)
    qbank_db.delete(bank)
    qbank_db.commit()
    
    # Delete all permissions for this bank
    main_db.query(UserBankPermission).filter(
        UserBankPermission.bank_id == bank_id
    ).delete()
    main_db.commit()
    
    return {"message": "Question bank deleted successfully"}


@router.post("/{bank_id}/clone", response_model=QuestionBankResponse, status_code=status.HTTP_201_CREATED, tags=["📚 Bank Management"])
async def clone_question_bank(
    bank_id: str,
    new_name: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_teacher_user),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Clone an existing question bank"""
    # Get source bank
    source_bank = qbank_db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
    
    if not source_bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source question bank not found"
        )
    
    # Check permission
    if not source_bank.is_public and not check_bank_permission(bank_id, "read", current_user, main_db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to clone this question bank"
        )
    
    # Create new bank
    new_bank_id = str(uuid.uuid4())
    new_bank = QuestionBank(
        id=new_bank_id,
        name=new_name,
        description=f"Cloned from {source_bank.name}",
        category=source_bank.category,
        is_public=False,
        metadata=source_bank.metadata,
        creator_id=current_user.id,
        version="1.0.0"
    )
    
    qbank_db.add(new_bank)
    
    # Clone questions
    source_questions = qbank_db.query(Question).filter(
        Question.bank_id == bank_id
    ).all()
    
    for source_q in source_questions:
        new_q = Question(
            id=str(uuid.uuid4()),
            bank_id=new_bank_id,
            question_number=source_q.question_number,
            stem=source_q.stem,
            stem_format=source_q.stem_format,
            type=source_q.type,
            difficulty=source_q.difficulty,
            category=source_q.category,
            tags=source_q.tags,
            explanation=source_q.explanation,
            explanation_format=source_q.explanation_format,
            metadata=source_q.metadata
        )
        qbank_db.add(new_q)
    
    qbank_db.commit()
    qbank_db.refresh(new_bank)
    
    # Grant admin permission to creator
    permission = UserBankPermission(
        user_id=current_user.id,
        bank_id=new_bank_id,
        permission="admin",
        granted_by=current_user.id
    )
    
    main_db.add(permission)
    main_db.commit()
    
    new_bank.question_count = len(source_questions)
    return new_bank