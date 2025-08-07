"""
API v2 routes - Complete replacement for v1
"""

from fastapi import APIRouter
from app.api.v1.auth import router as auth_router  # Keep auth for now
from app.api.v1.users import router as users_router  # Keep users for now
from app.api.v1.qbank_v2 import router as qbank_router
from app.api.v1.llm import router as llm_router

api_router = APIRouter()

# Include all routers with v2 prefix
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["Users"]) 
api_router.include_router(qbank_router, prefix="/qbank", tags=["Question Bank"])
api_router.include_router(llm_router, prefix="/llm", tags=["LLM Management"])