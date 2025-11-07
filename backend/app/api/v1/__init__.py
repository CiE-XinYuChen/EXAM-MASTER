"""
API v1 routes
"""

from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .qbank import banks, questions, options, resources, imports
from .llm import router as llm_router
from .practice import router as practice_router
from .statistics import router as statistics_router
from .favorites import router as favorites_router
from .wrong_questions import router as wrong_questions_router
from .activation import router as activation_router
from .ai_chat import router as ai_chat_router

api_router = APIRouter()

# === Core API Routes ===

# Authentication & Users
api_router.include_router(auth_router, prefix="/auth", tags=["🔐 Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["👥 Users"])

# Question Bank Management
api_router.include_router(banks.router, prefix="/qbank/banks", tags=["📚 Question Banks"])
api_router.include_router(questions.router, prefix="/qbank/questions", tags=["❓ Questions"])
api_router.include_router(options.router, prefix="/qbank/options", tags=["⚙️ Question Options"])
api_router.include_router(resources.router, prefix="/qbank/resources", tags=["📁 Resources"])
api_router.include_router(imports.router, prefix="/qbank/import", tags=["📥 Import/Export"])

# Practice & Learning
api_router.include_router(practice_router, prefix="/practice", tags=["✏️ Practice Sessions"])
api_router.include_router(favorites_router, prefix="/favorites", tags=["⭐ Favorites"])
api_router.include_router(wrong_questions_router, prefix="/wrong-questions", tags=["❌ Wrong Questions"])

# Statistics & Analysis
api_router.include_router(statistics_router, prefix="/statistics", tags=["📊 Statistics"])

# AI Features
api_router.include_router(llm_router, prefix="/llm", tags=["🤖 LLM Management"])
api_router.include_router(ai_chat_router, prefix="/ai-chat", tags=["💬 AI Chat"])

# Activation System
api_router.include_router(activation_router, prefix="/activation", tags=["🔑 Activation Codes"])