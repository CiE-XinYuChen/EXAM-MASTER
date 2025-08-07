"""
API v1 routes
"""

from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .qbank import banks, questions, options, resources, imports
from .llm import router as llm_router

api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(banks.router, prefix="/qbank/banks", tags=["Question Banks"])
api_router.include_router(questions.router, prefix="/qbank/questions", tags=["Questions"])
api_router.include_router(options.router, prefix="/qbank/options", tags=["Question Options"])
api_router.include_router(resources.router, prefix="/qbank/resources", tags=["Resources"])
api_router.include_router(imports.router, prefix="/qbank/import", tags=["Import/Export"])
api_router.include_router(llm_router, tags=["LLM Management"])