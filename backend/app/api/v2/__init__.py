"""
API v2 routes - Complete replacement for v1
"""

from fastapi import APIRouter
from app.api.v1.auth import router as auth_router  # Keep auth for now
from app.api.v1.users import router as users_router  # Keep users for now
from app.api.v1.qbank_v2 import router as qbank_router
from app.api.v1.llm import router as llm_router

# Import new organized routers
from app.api.v2.admin import router as admin_router
from app.api.v2.exams import router as exams_router
from app.api.v2.import_export import router as import_export_router

api_router = APIRouter()

# Core Authentication & User Management
api_router.include_router(
    auth_router, 
    prefix="/auth", 
    tags=["🔐 Authentication"],
    responses={404: {"description": "Not found"}}
)

api_router.include_router(
    users_router, 
    prefix="/users", 
    tags=["👥 User Management"],
    responses={404: {"description": "Not found"}}
) 

# Question Bank Management
api_router.include_router(
    qbank_router, 
    prefix="/qbank", 
    tags=["📚 Question Banks"],
    responses={404: {"description": "Not found"}}
)

# Exam & Practice Sessions
api_router.include_router(
    exams_router, 
    prefix="/exams", 
    tags=["📝 Exams & Practice"],
    responses={404: {"description": "Not found"}}
)

# Import/Export Operations
api_router.include_router(
    import_export_router, 
    prefix="/import-export", 
    tags=["📥📤 Import & Export"],
    responses={404: {"description": "Not found"}}
)

# AI & LLM Features
api_router.include_router(
    llm_router, 
    prefix="/llm", 
    tags=["🤖 LLM & AI Features"],
    responses={404: {"description": "Not found"}}
)

# System Administration & Statistics
api_router.include_router(
    admin_router, 
    prefix="", 
    tags=["🔧 System Administration"],
    responses={404: {"description": "Not found"}}
)