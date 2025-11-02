"""
Admin Panel API Routes
"""

from fastapi import APIRouter, Request, Depends, HTTPException, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, Response, FileResponse
from sqlalchemy.orm import Session
from typing import Optional
import secrets
from datetime import datetime

from app.core.database import get_main_db, get_qbank_db
from app.core.security import verify_password, get_password_hash, get_current_user
from app.models.user_models import User, UserBankPermission, UserRole
from app.models.question_models_v2 import QuestionBankV2, QuestionV2, QuestionOptionV2
from app.models.llm_models import LLMInterface, PromptTemplate
from app.services.question_bank_service import QuestionBankService

router = APIRouter()

# Health and System Status Endpoints
@router.get("/health", tags=["🔧 System Status"])
async def health_check():
    """System health check endpoint"""
    return {"status": "healthy"}


@router.get("/", tags=["🔧 System Status"])
async def root():
    """API root endpoint with system information"""
    from app.core.config import settings
    return {
        "app": "EXAM-MASTER",
        "version": settings.app_version,
        "api_docs": "/api/docs",
        "admin_panel": "/admin",
        "status": "running"
    }


# Statistics and Dashboard Endpoints
@router.get("/stats/overview", tags=["📊 Statistics & Analytics"])
async def get_system_overview(
    main_db: Session = Depends(get_main_db),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Get system overview statistics"""
    total_users = main_db.query(User).count()
    total_banks = qbank_db.query(QuestionBankV2).count()
    total_questions = qbank_db.query(QuestionV2).count()
    
    return {
        "users": total_users,
        "banks": total_banks,
        "questions": total_questions,
        "active_sessions": 0  # Placeholder for session count
    }


@router.get("/stats/users", tags=["📊 Statistics & Analytics"])
async def get_user_statistics(
    main_db: Session = Depends(get_main_db)
):
    """Get detailed user statistics"""
    total_users = main_db.query(User).count()
    active_users = main_db.query(User).filter(User.is_active == True).count()
    admin_users = main_db.query(User).filter(User.role == UserRole.admin).count()
    student_users = main_db.query(User).filter(User.role == UserRole.student).count()
    teacher_users = main_db.query(User).filter(User.role == UserRole.teacher).count()
    
    return {
        "total": total_users,
        "active": active_users,
        "admins": admin_users,
        "students": student_users,
        "teachers": teacher_users
    }


@router.get("/stats/question-banks", tags=["📊 Statistics & Analytics"])
async def get_question_bank_statistics(
    qbank_db: Session = Depends(get_qbank_db)
):
    """Get question bank statistics"""
    total_banks = qbank_db.query(QuestionBankV2).count()
    public_banks = qbank_db.query(QuestionBankV2).filter(QuestionBankV2.is_public == True).count()
    private_banks = total_banks - public_banks
    
    # Get category distribution
    categories = qbank_db.query(QuestionBankV2.category).distinct().all()
    category_stats = {}
    for cat in categories:
        if cat[0]:
            count = qbank_db.query(QuestionBankV2).filter(QuestionBankV2.category == cat[0]).count()
            category_stats[cat[0]] = count
    
    return {
        "total": total_banks,
        "public": public_banks,
        "private": private_banks,
        "categories": category_stats
    }


@router.get("/stats/questions", tags=["📊 Statistics & Analytics"])
async def get_question_statistics(
    qbank_db: Session = Depends(get_qbank_db)
):
    """Get question statistics"""
    from app.models.question_models_v2 import QuestionType
    
    total_questions = qbank_db.query(QuestionV2).count()
    
    # Type distribution
    type_stats = {}
    for q_type in QuestionType:
        count = qbank_db.query(QuestionV2).filter(QuestionV2.type == q_type).count()
        type_stats[q_type.value] = count
    
    # Difficulty distribution
    difficulty_stats = {}
    for diff in ["easy", "medium", "hard", "expert"]:
        count = qbank_db.query(QuestionV2).filter(QuestionV2.difficulty == diff).count()
        difficulty_stats[diff] = count
    
    return {
        "total": total_questions,
        "by_type": type_stats,
        "by_difficulty": difficulty_stats
    }