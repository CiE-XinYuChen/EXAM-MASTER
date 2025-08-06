"""
Question options management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from app.core.database import get_qbank_db, get_main_db
from app.core.security import get_current_user
from app.models.question_models import Question, QuestionOption
from app.models.user_models import User, UserBankPermission
from app.schemas.question_schemas import (
    QuestionOptionResponse,
    QuestionOptionUpdate
)

router = APIRouter()


def check_question_permission(
    question_id: str,
    permission: str,
    user: User,
    qbank_db: Session,
    main_db: Session
) -> Question:
    """Check if user has permission for a question and return it"""
    question = qbank_db.query(Question).filter(Question.id == question_id).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Admin always has permission
    if user.role == "admin":
        return question
    
    # Check bank permission
    perm = main_db.query(UserBankPermission).filter(
        UserBankPermission.user_id == user.id,
        UserBankPermission.bank_id == question.bank_id
    ).first()
    
    if not perm:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No permission to {permission} this question"
        )
    
    if permission == "read":
        if perm.permission not in ["read", "write", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No permission to read this question"
            )
    elif permission == "write":
        if perm.permission not in ["write", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No permission to modify this question"
            )
    
    return question


@router.get("/{option_id}", response_model=QuestionOptionResponse)
async def get_option(
    option_id: str,
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Get option details"""
    option = qbank_db.query(QuestionOption).filter(QuestionOption.id == option_id).first()
    
    if not option:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Option not found"
        )
    
    # Check permission through question
    check_question_permission(option.question_id, "read", current_user, qbank_db, main_db)
    
    return option


@router.put("/{option_id}", response_model=QuestionOptionResponse)
async def update_option(
    option_id: str,
    option_update: QuestionOptionUpdate,
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Update option"""
    option = qbank_db.query(QuestionOption).filter(QuestionOption.id == option_id).first()
    
    if not option:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Option not found"
        )
    
    # Check permission through question
    check_question_permission(option.question_id, "write", current_user, qbank_db, main_db)
    
    # Update fields
    update_data = option_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(option, field, value)
    
    qbank_db.commit()
    qbank_db.refresh(option)
    
    return option


@router.delete("/{option_id}", response_model=dict)
async def delete_option(
    option_id: str,
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Delete option"""
    option = qbank_db.query(QuestionOption).filter(QuestionOption.id == option_id).first()
    
    if not option:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Option not found"
        )
    
    # Check permission through question
    question = check_question_permission(option.question_id, "write", current_user, qbank_db, main_db)
    
    # Check if this is the last option
    option_count = qbank_db.query(QuestionOption).filter(
        QuestionOption.question_id == option.question_id
    ).count()
    
    if option_count <= 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete option. Question must have at least 2 options"
        )
    
    # Check if this is the only correct option for single choice questions
    if question.type == "single" and option.is_correct:
        other_correct = qbank_db.query(QuestionOption).filter(
            QuestionOption.question_id == option.question_id,
            QuestionOption.id != option_id,
            QuestionOption.is_correct == True
        ).first()
        
        if not other_correct:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the only correct option for a single choice question"
            )
    
    # Delete option
    qbank_db.delete(option)
    qbank_db.commit()
    
    return {"message": "Option deleted successfully"}


@router.post("/{option_id}/reorder", response_model=dict)
async def reorder_options(
    question_id: str,
    new_order: List[str],  # List of option IDs in new order
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Reorder options for a question"""
    # Check permission
    check_question_permission(question_id, "write", current_user, qbank_db, main_db)
    
    # Get all options for the question
    options = qbank_db.query(QuestionOption).filter(
        QuestionOption.question_id == question_id
    ).all()
    
    # Verify all option IDs are present
    option_ids = {opt.id for opt in options}
    new_order_set = set(new_order)
    
    if option_ids != new_order_set:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid option order. All option IDs must be present"
        )
    
    # Update sort order
    for idx, option_id in enumerate(new_order):
        option = next(opt for opt in options if opt.id == option_id)
        option.sort_order = idx
    
    qbank_db.commit()
    
    return {"message": "Options reordered successfully"}


@router.post("/batch-update", response_model=dict)
async def batch_update_options(
    updates: List[dict],  # List of {option_id, updates}
    current_user: User = Depends(get_current_user),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Batch update multiple options"""
    updated_count = 0
    errors = []
    
    for update_item in updates:
        option_id = update_item.get("option_id")
        update_data = update_item.get("updates", {})
        
        if not option_id:
            errors.append("Missing option_id in update item")
            continue
        
        try:
            option = qbank_db.query(QuestionOption).filter(
                QuestionOption.id == option_id
            ).first()
            
            if not option:
                errors.append(f"Option {option_id} not found")
                continue
            
            # Check permission (only once per question)
            check_question_permission(option.question_id, "write", current_user, qbank_db, main_db)
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(option, field):
                    setattr(option, field, value)
            
            updated_count += 1
            
        except HTTPException as e:
            errors.append(f"Option {option_id}: {e.detail}")
        except Exception as e:
            errors.append(f"Option {option_id}: {str(e)}")
    
    qbank_db.commit()
    
    return {
        "message": f"Updated {updated_count} options",
        "updated_count": updated_count,
        "errors": errors
    }