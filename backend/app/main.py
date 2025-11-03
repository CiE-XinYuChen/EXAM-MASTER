"""
Main FastAPI application with integrated admin panel
"""

from fastapi import FastAPI, Request, Depends, HTTPException, Form, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from typing import Optional
import secrets

from app.core.config import settings
from app.core.database import init_databases, get_main_db, get_qbank_db
from app.core.security import verify_password, get_password_hash, create_access_token, get_current_user
from app.models.user_models import User, UserBankPermission, UserRole
from datetime import datetime as datetime
from app.models.question_models_v2 import QuestionBankV2, QuestionV2, QuestionOptionV2
from app.models.llm_models import LLMInterface, PromptTemplate, LLMParseLog
from app.services.question_bank_service import QuestionBankService
from app.api.v1 import api_router as v1_api_router
from app.api.v2 import api_router
from app.api.mcp.router import router as mcp_router


# Session storage for admin panel (in production, use Redis or database)
admin_sessions = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("Starting up...")
    init_databases()
    yield
    # Shutdown
    print("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/api/docs",  # Changed from settings.docs_url
    redoc_url="/api/redoc",  # Changed from settings.redoc_url
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include V1 API routes (for resources and other endpoints)
app.include_router(v1_api_router, prefix="/api/v1")

# Include V2 API routes
app.include_router(api_router, prefix="/api/v2")

# Include MCP routes
app.include_router(mcp_router, prefix="/api/mcp")


# Admin authentication helper
def get_admin_user(request: Request) -> Optional[dict]:
    """Get current admin user from session"""
    session_id = request.cookies.get("admin_session")
    if session_id and session_id in admin_sessions:
        return admin_sessions[session_id]
    return None


def admin_required(request: Request):
    """Dependency to require admin login"""
    user = get_admin_user(request)
    if not user:
        raise HTTPException(status_code=303, detail="Login required", 
                          headers={"Location": "/admin/login"})
    return user


# Admin Panel Routes
@app.get("/admin", response_class=HTMLResponse, tags=["🖥️ Admin Dashboard"])
async def admin_dashboard(
    request: Request,
    current_admin = Depends(admin_required),
    main_db: Session = Depends(get_main_db),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Admin dashboard"""
    from app.models.ai_models import AIConfig, ChatSession

    # Get statistics using V2 models only
    total_users = main_db.query(User).count()
    total_banks = qbank_db.query(QuestionBankV2).count()
    total_questions = qbank_db.query(QuestionV2).count()

    # Get AI statistics
    total_ai_configs = main_db.query(AIConfig).count()
    total_ai_sessions = main_db.query(ChatSession).count()

    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "current_user": current_admin,
        "stats": {
            "users": total_users,
            "banks": total_banks,
            "questions": total_questions,
            "active": 0,
            "ai_configs": total_ai_configs,
            "ai_sessions": total_ai_sessions
        }
    })


@app.get("/admin/login", response_class=HTMLResponse, tags=["🖥️ Admin Dashboard"])
async def admin_login_page(request: Request):
    """Admin login page"""
    return templates.TemplateResponse("admin/login.html", {"request": request})


@app.post("/admin/login", tags=["🖥️ Admin Dashboard"])
async def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_main_db)
):
    """Admin login handler"""
    # Find user
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()
    
    # Verify password and admin role
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse("admin/login.html", {
            "request": request,
            "error": "用户名或密码错误"
        })
    
    if user.role != UserRole.admin:
        return templates.TemplateResponse("admin/login.html", {
            "request": request,
            "error": "需要管理员权限"
        })
    
    # Create session
    session_id = secrets.token_urlsafe(32)
    admin_sessions[session_id] = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value
    }
    
    # Redirect to dashboard
    response = RedirectResponse(url="/admin", status_code=303)
    response.set_cookie(key="admin_session", value=session_id, httponly=True)
    return response


@app.get("/admin/logout", tags=["🖥️ Admin Dashboard"])
async def admin_logout(request: Request):
    """Admin logout"""
    session_id = request.cookies.get("admin_session")
    if session_id and session_id in admin_sessions:
        del admin_sessions[session_id]
    
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie(key="admin_session")
    return response


@app.get("/admin/users", response_class=HTMLResponse, tags=["🖥️ Admin User Management"])
async def admin_users(
    request: Request,
    current_admin = Depends(admin_required),
    db: Session = Depends(get_main_db),
    page: int = 1,
    role: Optional[str] = None
):
    """User management page"""
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    
    per_page = 20
    skip = (page - 1) * per_page
    users = query.offset(skip).limit(per_page).all()
    
    return templates.TemplateResponse("admin/users.html", {
        "request": request,
        "current_user": current_admin,
        "users": users,
        "page": page,
        "role_filter": role
    })


@app.get("/admin/users/create", response_class=HTMLResponse, tags=["🖥️ Admin User Management"])
async def admin_users_create_form(
    request: Request,
    current_admin = Depends(admin_required)
):
    """Show create user form"""
    return templates.TemplateResponse("admin/user_form.html", {
        "request": request,
        "current_user": current_admin,
        "user": None,
        "action": "create"
    })


@app.post("/admin/users/create", tags=["🖥️ Admin User Management"])
async def admin_users_create(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    role: str = Form(...),
    is_active: bool = Form(False),
    current_admin = Depends(admin_required),
    db: Session = Depends(get_main_db)
):
    """Create new user"""
    # Validate passwords match
    if password != confirm_password:
        return templates.TemplateResponse("admin/user_form.html", {
            "request": request,
            "current_user": current_admin,
            "user": None,
            "action": "create",
            "error": "密码不匹配"
        })
    
    # Check if username exists
    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse("admin/user_form.html", {
            "request": request,
            "current_user": current_admin,
            "user": None,
            "action": "create",
            "error": "用户名已存在"
        })
    
    # Check if email exists
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse("admin/user_form.html", {
            "request": request,
            "current_user": current_admin,
            "user": None,
            "action": "create",
            "error": "邮箱已被注册"
        })
    
    # Create new user
    user = User(
        username=username,
        email=email,
        password_hash=get_password_hash(password),
        role=role,
        is_active=is_active
    )
    
    db.add(user)
    db.commit()
    
    return RedirectResponse(url="/admin/users", status_code=303)


@app.get("/admin/users/{user_id}/edit", response_class=HTMLResponse, tags=["🖥️ Admin User Management"])
async def admin_users_edit_form(
    request: Request,
    user_id: int,
    current_admin = Depends(admin_required),
    db: Session = Depends(get_main_db)
):
    """Show edit user form"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return templates.TemplateResponse("admin/user_form.html", {
        "request": request,
        "current_user": current_admin,
        "user": user,
        "action": "edit"
    })


@app.post("/admin/users/{user_id}/edit", tags=["🖥️ Admin User Management"])
async def admin_users_edit(
    request: Request,
    user_id: int,
    email: str = Form(...),
    role: str = Form(...),
    is_active: bool = Form(False),
    current_admin = Depends(admin_required),
    db: Session = Depends(get_main_db)
):
    """Update user information"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # Check if email is taken by another user
    existing_user = db.query(User).filter(
        User.email == email,
        User.id != user_id
    ).first()
    
    if existing_user:
        return templates.TemplateResponse("admin/user_form.html", {
            "request": request,
            "current_user": current_admin,
            "user": user,
            "action": "edit",
            "error": "邮箱已被其他用户使用"
        })
    
    # Prevent removing the last admin
    if user.role == UserRole.admin and role != "admin":
        admin_count = db.query(User).filter(User.role == UserRole.admin).count()
        if admin_count == 1:
            return templates.TemplateResponse("admin/user_form.html", {
                "request": request,
                "current_user": current_admin,
                "user": user,
                "action": "edit",
                "error": "不能移除最后一个管理员"
            })
    
    # Update user
    user.email = email
    user.role = role
    user.is_active = is_active
    user.updated_at = datetime.utcnow()
    
    db.commit()
    
    return RedirectResponse(url="/admin/users", status_code=303)


@app.get("/admin/users/{user_id}/password", response_class=HTMLResponse, tags=["🖥️ Admin User Management"])
async def admin_users_password_form(
    request: Request,
    user_id: int,
    current_admin = Depends(admin_required),
    db: Session = Depends(get_main_db)
):
    """Show change password form"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return templates.TemplateResponse("admin/user_password.html", {
        "request": request,
        "current_user": current_admin,
        "user": user
    })


@app.post("/admin/users/{user_id}/password", tags=["🖥️ Admin User Management"])
async def admin_users_change_password(
    request: Request,
    user_id: int,
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    current_admin = Depends(admin_required),
    db: Session = Depends(get_main_db)
):
    """Change user password"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # Validate passwords match
    if new_password != confirm_password:
        return templates.TemplateResponse("admin/user_password.html", {
            "request": request,
            "current_user": current_admin,
            "user": user,
            "error": "两次输入的密码不一致"
        })
    
    # Update password
    user.password_hash = get_password_hash(new_password)
    user.updated_at = datetime.utcnow()
    
    db.commit()
    
    return templates.TemplateResponse("admin/user_password.html", {
        "request": request,
        "current_user": current_admin,
        "user": user,
        "success": "密码修改成功"
    })


@app.post("/admin/users/{user_id}/delete", tags=["🖥️ Admin User Management"])
async def admin_users_delete(
    user_id: int,
    current_admin = Depends(admin_required),
    db: Session = Depends(get_main_db)
):
    """Delete user"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # Prevent deleting yourself
    if user.id == current_admin["id"]:
        raise HTTPException(status_code=400, detail="不能删除自己的账户")
    
    # Prevent deleting the last admin
    if user.role == UserRole.admin:
        admin_count = db.query(User).filter(User.role == UserRole.admin).count()
        if admin_count == 1:
            raise HTTPException(status_code=400, detail="不能删除最后一个管理员账户")
    
    # Delete user (cascades to related records)
    db.delete(user)
    db.commit()
    
    return RedirectResponse(url="/admin/users", status_code=303)


@app.get("/admin/users/{user_id}/statistics", response_class=HTMLResponse, tags=["🖥️ Admin User Management"])
async def admin_user_statistics(
    user_id: int,
    request: Request,
    current_admin = Depends(admin_required),
    main_db: Session = Depends(get_main_db),
    qbank_db: Session = Depends(get_qbank_db)
):
    """View user statistics"""
    from app.models.user_statistics import UserBankStatistics
    from app.models.activation import UserBankAccess
    from app.models.question_models_v2 import QuestionBankV2
    from app.models.user_practice import UserFavorite, UserWrongQuestion, PracticeSession

    # Get user
    user = main_db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # Get bank statistics
    bank_stats_list = qbank_db.query(UserBankStatistics).filter(
        UserBankStatistics.user_id == user_id
    ).all()

    # Get bank names
    bank_ids = [s.bank_id for s in bank_stats_list]
    banks = qbank_db.query(QuestionBankV2).filter(
        QuestionBankV2.id.in_(bank_ids)
    ).all()
    bank_names = {b.id: b.name for b in banks}

    # Add bank names to stats
    for stat in bank_stats_list:
        stat.bank_name = bank_names.get(stat.bank_id)

    # Calculate overview statistics
    total_banks_accessed = len(bank_stats_list)
    total_questions_practiced = sum(s.practiced_questions for s in bank_stats_list)
    total_correct = sum(s.correct_count for s in bank_stats_list)
    total_wrong = sum(s.wrong_count for s in bank_stats_list)
    total_time_spent = sum(s.total_time_spent for s in bank_stats_list)
    overall_accuracy_rate = (total_correct / (total_correct + total_wrong) * 100) if (total_correct + total_wrong) > 0 else 0.0

    from sqlalchemy import func
    total_favorites = qbank_db.query(func.count(UserFavorite.id)).filter(
        UserFavorite.user_id == user_id
    ).scalar() or 0

    total_wrong_questions = qbank_db.query(func.count(UserWrongQuestion.id)).filter(
        UserWrongQuestion.user_id == user_id
    ).scalar() or 0

    total_sessions = qbank_db.query(func.count(PracticeSession.id)).filter(
        PracticeSession.user_id == user_id
    ).scalar() or 0

    overview = {
        "total_banks_accessed": total_banks_accessed,
        "total_questions_practiced": total_questions_practiced,
        "total_correct": total_correct,
        "total_wrong": total_wrong,
        "overall_accuracy_rate": overall_accuracy_rate,
        "total_time_spent": total_time_spent,
        "total_sessions": total_sessions,
        "total_favorites": total_favorites,
        "total_wrong_questions": total_wrong_questions,
        "consecutive_days": 0,  # Simplified for now
        "total_practice_days": 0
    }

    # Get access list
    access_list = qbank_db.query(UserBankAccess).filter(
        UserBankAccess.user_id == user_id
    ).all()

    # Add bank names and expired status to access list
    for access in access_list:
        access.bank_name = bank_names.get(access.bank_id)
        access.is_expired = access.is_expired()

    return templates.TemplateResponse("admin/user_statistics.html", {
        "request": request,
        "user": user,
        "overview": overview,
        "bank_stats": bank_stats_list,
        "access_list": access_list,
        "current_user": current_admin
    })


@app.get("/admin/activation-codes", response_class=HTMLResponse, tags=["🖥️ Admin Activation"])
async def admin_activation_codes(
    request: Request,
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Activation code management page"""
    from app.models.question_models_v2 import QuestionBankV2

    # Get all banks for the dropdown
    banks = qbank_db.query(QuestionBankV2).order_by(QuestionBankV2.name).all()

    return templates.TemplateResponse("admin/activation_codes.html", {
        "request": request,
        "banks": banks,
        "current_user": current_admin
    })


@app.get("/admin/qbanks", response_class=HTMLResponse, tags=["🖥️ Admin Question Banks"])
async def admin_qbanks(
    request: Request,
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db),
    page: int = 1
):
    """Question banks management page using V2 API"""
    per_page = 20
    skip = (page - 1) * per_page
    
    # Get total count from V2 models
    total_count = qbank_db.query(QuestionBankV2).count()
    total_pages = max(1, (total_count + per_page - 1) // per_page)
    
    # Ensure page is within valid range
    page = max(1, min(page, total_pages))
    skip = (page - 1) * per_page
    
    banks = qbank_db.query(QuestionBankV2).offset(skip).limit(per_page).all()
    
    # Add question count using V2
    for bank in banks:
        bank.question_count = bank.total_questions
    
    return templates.TemplateResponse("admin/qbanks.html", {
        "request": request,
        "current_user": current_admin,
        "banks": banks,
        "page": page,
        "total_pages": total_pages,
        "total_count": total_count
    })


@app.get("/admin/qbanks/create", response_class=HTMLResponse, tags=["🖥️ Admin Question Banks"])
async def admin_qbanks_create_form(
    request: Request,
    current_admin = Depends(admin_required)
):
    """Show create question bank form"""
    return templates.TemplateResponse("admin/qbank_form.html", {
        "request": request,
        "current_user": current_admin,
        "bank": None,
        "action": "create"
    })


@app.post("/admin/qbanks/create", tags=["🖥️ Admin Question Banks"])
async def admin_qbanks_create(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    category: str = Form(""),
    is_public: bool = Form(False),
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Create new question bank using V2 service"""
    service = QuestionBankService(qbank_db)
    
    # Create question bank using service
    bank = service.create_question_bank(
        name=name,
        description=description,
        category=category,
        is_public=is_public,
        creator_id=current_admin["id"]
    )
    
    # Grant admin permission to creator
    permission = UserBankPermission(
        user_id=current_admin["id"],
        bank_id=bank.id,
        permission="admin",
        granted_by=current_admin["id"]
    )
    
    main_db.add(permission)
    main_db.commit()
    
    return RedirectResponse(url="/admin/qbanks", status_code=303)


@app.get("/admin/qbanks/{bank_id}/edit", response_class=HTMLResponse, tags=["🖥️ Admin Question Banks"])
async def admin_qbanks_edit_form(
    request: Request,
    bank_id: str,
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Show edit question bank form using V2"""
    bank = qbank_db.query(QuestionBankV2).filter(QuestionBankV2.id == bank_id).first()
    
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")
    
    return templates.TemplateResponse("admin/qbank_form.html", {
        "request": request,
        "current_user": current_admin,
        "bank": bank,
        "action": "edit"
    })


@app.post("/admin/qbanks/{bank_id}/edit", tags=["🖥️ Admin Question Banks"])
async def admin_qbanks_edit(
    request: Request,
    bank_id: str,
    name: str = Form(...),
    description: str = Form(""),
    category: str = Form(""),
    is_public: bool = Form(False),
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Update question bank using V2"""
    service = QuestionBankService(qbank_db)
    
    bank = service.update_question_bank(
        bank_id=bank_id,
        name=name,
        description=description,
        category=category,
        is_public=is_public
    )
    
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")
    
    return RedirectResponse(url="/admin/qbanks", status_code=303)


@app.post("/admin/qbanks/{bank_id}/delete", tags=["🖥️ Admin Question Banks"])
async def admin_qbanks_delete(
    bank_id: str,
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Delete question bank using V2 service"""
    service = QuestionBankService(qbank_db)
    
    # Delete bank using service (handles folder cleanup)
    success = service.delete_question_bank(bank_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="题库不存在")
    
    # Delete all permissions for this bank
    main_db.query(UserBankPermission).filter(
        UserBankPermission.bank_id == bank_id
    ).delete()
    main_db.commit()
    
    return RedirectResponse(url="/admin/qbanks", status_code=303)


@app.get("/admin/questions", response_class=HTMLResponse, tags=["🖥️ Admin Questions"])
async def admin_questions(
    request: Request,
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db),
    page: int = 1,
    bank_id: Optional[str] = None
):
    """Questions management page"""
    import math
    
    query = qbank_db.query(QuestionV2)
    
    if bank_id:
        query = query.filter(QuestionV2.bank_id == bank_id)
    
    # Get total count for pagination
    total_count = query.count()
    per_page = 20
    total_pages = math.ceil(total_count / per_page) if total_count > 0 else 1
    
    # Ensure page is within valid range
    page = max(1, min(page, total_pages))
    
    skip = (page - 1) * per_page
    questions = query.offset(skip).limit(per_page).all()
    
    # Get banks for filter
    banks = qbank_db.query(QuestionBankV2).limit(100).all()
    
    return templates.TemplateResponse("admin/questions.html", {
        "request": request,
        "current_user": current_admin,
        "questions": questions,
        "banks": banks,
        "page": page,
        "total_pages": total_pages,
        "total_count": total_count,
        "per_page": per_page,
        "bank_filter": bank_id
    })


@app.get("/admin/questions/create", response_class=HTMLResponse, tags=["🖥️ Admin Questions"])
async def admin_questions_create_form(
    request: Request,
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db),
    bank_id: Optional[str] = None
):
    """Show create question form"""
    banks = qbank_db.query(QuestionBankV2).limit(100).all()
    
    return templates.TemplateResponse("admin/question_create.html", {
        "request": request,
        "current_user": current_admin,
        "question": None,
        "banks": banks,
        "bank_id": bank_id,
        "action": "create"
    })


@app.post("/admin/questions/create", tags=["🖥️ Admin Questions"])
async def admin_questions_create(
    request: Request,
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Create new question - supports all question types"""
    import uuid
    import json
    
    # Get JSON data from request
    try:
        data = await request.json()
    except:
        # Fallback to form data for backward compatibility
        form_data = await request.form()
        data = {
            "bank_id": form_data.get("bank_id"),
            "type": form_data.get("type"),
            "stem": form_data.get("stem"),
            "difficulty": form_data.get("difficulty", "medium"),
            "category": form_data.get("category", ""),
            "tags": form_data.get("tags", "").split(",") if form_data.get("tags") else [],
            "explanation": form_data.get("explanation", ""),
            "meta_data": {}
        }
    
    # Create question
    question_id = str(uuid.uuid4())
    question = QuestionV2(
        id=question_id,
        bank_id=data["bank_id"],
        question_number=data.get("question_number", 0),
        stem=data["stem"],
        type=data["type"],
        difficulty=data.get("difficulty", "medium"),
        category=data.get("category", ""),
        tags=data.get("tags", []),
        explanation=data.get("explanation", ""),
        stem_format="text",
        explanation_format="text",
        meta_data=data.get("meta_data", {})
    )
    
    qbank_db.add(question)
    
    # Handle different question types
    if data["type"] in ["single", "multiple"]:
        # Choice questions with options
        if "options" in data:
            for i, opt_data in enumerate(data["options"]):
                option = QuestionOptionV2(
                    id=str(uuid.uuid4()),
                    question_id=question_id,
                    option_label=opt_data["label"],
                    option_content=opt_data["content"],
                    option_format="text",
                    is_correct=opt_data.get("is_correct", False),
                    sort_order=i
                )
                qbank_db.add(option)
        else:
            # Legacy form data handling
            form_data = await request.form()
            for key in form_data:
                if key.startswith("option_content_"):
                    idx = int(key.replace("option_content_", ""))
                    label = String.fromCharCode(65 + idx)
                    is_correct = False
                    
                    if data["type"] == "single":
                        correct_option = form_data.get("correct_option")
                        is_correct = (str(idx) == correct_option)
                    else:  # multiple
                        correct_options = form_data.getlist("correct_options")
                        is_correct = (str(idx) in correct_options)
                    
                    option = QuestionOptionV2(
                        id=str(uuid.uuid4()),
                        question_id=question_id,
                        option_label=chr(65 + idx),
                        option_content=form_data[key],
                        option_format="text",
                        is_correct=is_correct,
                        sort_order=idx
                    )
                    qbank_db.add(option)
    
    elif data["type"] == "judge":
        # Judge questions store answer in meta_data
        form_data = await request.form() if not data.get("meta_data") else None
        if form_data:
            judge_answer = form_data.get("judge_answer")
            question.meta_data = {"answer": judge_answer == "true"}
    
    elif data["type"] == "fill":
        # Fill questions store blanks in meta_data
        form_data = await request.form() if not data.get("meta_data") else None
        if form_data:
            blanks = []
            i = 0
            while f"blank_answer_{i}" in form_data:
                blanks.append({
                    "position": i,
                    "answer": form_data.get(f"blank_answer_{i}"),
                    "alternatives": [form_data.get(f"blank_alt_{i}")] if form_data.get(f"blank_alt_{i}") else []
                })
                i += 1
            question.meta_data = {"blanks": blanks}
    
    elif data["type"] == "essay":
        # Essay questions store reference answer in meta_data
        form_data = await request.form() if not data.get("meta_data") else None
        if form_data:
            question.meta_data = {
                "reference_answer": form_data.get("reference_answer", ""),
                "keywords": form_data.get("keywords", "").split(",") if form_data.get("keywords") else []
            }
    
    qbank_db.commit()
    
    # Check if this is an AJAX request or should continue adding
    if "continue" in data or (await request.form()).get("continue"):
        return JSONResponse({"success": True, "question_id": question_id})
    
    return RedirectResponse(url=f"/admin/questions?bank_id={data['bank_id']}", status_code=303)


@app.get("/admin/questions/{question_id}/preview", response_class=HTMLResponse, tags=["🖥️ Admin Questions"])
async def admin_questions_preview(
    request: Request,
    question_id: str,
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Preview question with all details"""
    
    question = qbank_db.query(QuestionV2).filter(QuestionV2.id == question_id).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    # Get options for choice questions
    if question.type in ["single", "multiple"]:
        question.options = qbank_db.query(QuestionOptionV2).filter(
            QuestionOptionV2.question_id == question_id
        ).order_by(QuestionOptionV2.sort_order).all()
    
    return templates.TemplateResponse("admin/question_preview.html", {
        "request": request,
        "current_user": current_admin,
        "question": question
    })


@app.get("/admin/questions/{question_id}/edit", response_class=HTMLResponse, tags=["🖥️ Admin Questions"])
async def admin_questions_edit_form(
    request: Request,
    question_id: str,
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Show edit question form"""
    
    question = qbank_db.query(QuestionV2).filter(QuestionV2.id == question_id).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    # Get banks for dropdown
    banks = qbank_db.query(QuestionBankV2).limit(100).all()
    
    # Get existing options for choice questions
    options = []
    if question.type in ["single", "multiple"]:
        options = qbank_db.query(QuestionOptionV2).filter(
            QuestionOptionV2.question_id == question_id
        ).order_by(QuestionOptionV2.sort_order).all()
    
    # Add options to question object for template
    question.options = options
    
    return templates.TemplateResponse("admin/question_edit.html", {
        "request": request,
        "current_user": current_admin,
        "question": question,
        "banks": banks,
        "action": "edit"
    })


@app.post("/admin/questions/{question_id}/edit", tags=["🖥️ Admin Questions"])
async def admin_questions_edit(
    request: Request,
    question_id: str,
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Update question - supports all question types"""
    import uuid
    import json
    
    question = qbank_db.query(QuestionV2).filter(QuestionV2.id == question_id).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    # Get JSON or form data
    try:
        data = await request.json()
    except:
        # Fallback to form data
        form_data = await request.form()
        data = {
            "bank_id": form_data.get("bank_id"),
            "type": form_data.get("type"),
            "stem": form_data.get("stem"),
            "difficulty": form_data.get("difficulty", "medium"),
            "category": form_data.get("category", ""),
            "tags": form_data.get("tags", "").split(",") if form_data.get("tags") else [],
            "explanation": form_data.get("explanation", ""),
            "meta_data": {}
        }
    
    # Update question fields
    question.bank_id = data.get("bank_id", question.bank_id)
    question.stem = data.get("stem", question.stem)
    question.type = data.get("type", question.type)
    question.difficulty = data.get("difficulty", question.difficulty)
    question.category = data.get("category", question.category)
    question.tags = data.get("tags", question.tags)
    question.explanation = data.get("explanation", question.explanation)
    
    # Update meta_data based on question type
    if data.get("meta_data"):
        question.meta_data = data["meta_data"]
    
    # Handle different question types
    if question.type in ["single", "multiple"]:
        # Delete existing options
        qbank_db.query(QuestionOptionV2).filter(
            QuestionOptionV2.question_id == question_id
        ).delete()
        
        # Add new options
        if "options" in data:
            for i, opt_data in enumerate(data["options"]):
                option = QuestionOptionV2(
                    id=str(uuid.uuid4()),
                    question_id=question_id,
                    option_label=opt_data["label"],
                    option_content=opt_data["content"],
                    option_format="text",
                    is_correct=opt_data.get("is_correct", False),
                    sort_order=i
                )
                qbank_db.add(option)
        else:
            # Legacy form data handling
            form_data = await request.form()
            option_contents = []
            correct_options = []

            for key in form_data:
                if key.startswith("option_content_"):
                    idx = int(key.replace("option_content_", ""))
                    option_contents.append((idx, form_data[key]))
                elif key == "option_correct_single":
                    # Single choice - radio button
                    correct_options = [int(form_data[key])]
                elif key.startswith("option_correct_"):
                    # Multiple choice - checkboxes
                    if key != "option_correct_single":
                        idx = int(key.replace("option_correct_", ""))
                        correct_options.append(idx)

            option_contents.sort(key=lambda x: x[0])

            for i, (idx, content) in enumerate(option_contents):
                if content:
                    option = QuestionOptionV2(
                        id=str(uuid.uuid4()),
                        question_id=question_id,
                        option_label=chr(65 + i),
                        option_content=content,
                        option_format="text",
                        is_correct=(idx in correct_options),
                        sort_order=i
                    )
                    qbank_db.add(option)
    
    elif question.type == "judge":
        # Handle judge questions
        if not data.get("meta_data"):
            form_data = await request.form()
            judge_answer = form_data.get("judge_answer")
            question.meta_data = {"answer": judge_answer == "true"}
    
    elif question.type == "fill":
        # Handle fill questions
        if not data.get("meta_data"):
            form_data = await request.form()
            blanks = []
            i = 0
            while f"blank_answer_{i}" in form_data:
                blanks.append({
                    "position": i,
                    "answer": form_data.get(f"blank_answer_{i}"),
                    "alternatives": [form_data.get(f"blank_alt_{i}")] if form_data.get(f"blank_alt_{i}") else []
                })
                i += 1
            question.meta_data = {"blanks": blanks}
    
    elif question.type == "essay":
        # Handle essay questions
        if not data.get("meta_data"):
            form_data = await request.form()
            question.meta_data = {
                "reference_answer": form_data.get("reference_answer", ""),
                "keywords": form_data.get("keywords", "").split(",") if form_data.get("keywords") else []
            }
    
    qbank_db.commit()
    
    # Return appropriate response
    if "application/json" in request.headers.get("content-type", ""):
        return JSONResponse({"success": True, "question_id": question_id})
    
    return RedirectResponse(url=f"/admin/questions?bank_id={question.bank_id}", status_code=303)


@app.post("/admin/questions/{question_id}/delete", tags=["🖥️ Admin Questions"])
async def admin_questions_delete(
    question_id: str,
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Delete question"""
    question = qbank_db.query(QuestionV2).filter(QuestionV2.id == question_id).first()

    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    bank_id = question.bank_id

    # Delete question (cascades to options)
    qbank_db.delete(question)
    qbank_db.commit()

    return RedirectResponse(url=f"/admin/questions?bank_id={bank_id}", status_code=303)


@app.post("/admin/questions/{question_id}/resources/upload", tags=["🖥️ Admin Questions"])
async def admin_upload_resource(
    question_id: str,
    file: UploadFile = File(...),
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Upload resource for a question (images, videos, audio)"""
    import uuid
    import shutil
    from pathlib import Path
    import mimetypes
    from app.models.question_models import QuestionResource

    # Validate file type
    ALLOWED_EXTENSIONS = {
        'image': {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.bmp'},
        'video': {'.mp4', '.webm', '.avi', '.mov', '.mkv'},
        'audio': {'.mp3', '.wav', '.ogg', '.m4a', '.flac'},
        'document': {'.pdf', '.doc', '.docx', '.txt', '.tex', '.md'}
    }

    MAX_FILE_SIZES = {
        'image': 10 * 1024 * 1024,      # 10MB
        'video': 100 * 1024 * 1024,     # 100MB
        'audio': 20 * 1024 * 1024,      # 20MB
        'document': 20 * 1024 * 1024    # 20MB
    }

    # Get file type from extension
    file_ext = Path(file.filename).suffix.lower()
    file_type = None
    for ftype, extensions in ALLOWED_EXTENSIONS.items():
        if file_ext in extensions:
            file_type = ftype
            break

    if not file_type:
        return JSONResponse(
            status_code=400,
            content={"error": f"不支持的文件类型: {file_ext}"}
        )

    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZES[file_type]:
        max_size_mb = MAX_FILE_SIZES[file_type] / (1024 * 1024)
        return JSONResponse(
            status_code=400,
            content={"error": f"文件太大，{file_type}类型最大{max_size_mb}MB"}
        )

    # Check question exists
    question = qbank_db.query(QuestionV2).filter(QuestionV2.id == question_id).first()
    if not question:
        return JSONResponse(status_code=404, content={"error": "题目不存在"})

    # Generate unique filename
    resource_id = str(uuid.uuid4())
    safe_filename = f"{resource_id}{file_ext}"

    # Create directory structure
    base_storage = Path("storage")
    resource_dir = base_storage / file_type / question.bank_id
    resource_dir.mkdir(parents=True, exist_ok=True)

    # Save file
    file_path = resource_dir / safe_filename
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"文件保存失败: {str(e)}"}
        )

    # Get MIME type
    mime_type, _ = mimetypes.guess_type(str(file_path))

    # Create database record
    resource = QuestionResource(
        id=resource_id,
        question_id=question_id,
        resource_type=file_type,
        file_path=str(file_path.relative_to(base_storage)),
        file_name=file.filename,
        file_size=file_size,
        mime_type=mime_type
    )

    qbank_db.add(resource)
    qbank_db.commit()
    qbank_db.refresh(resource)

    # Return response matching ResourceResponse schema
    return JSONResponse(content={
        "id": resource.id,
        "resource_type": resource.resource_type,
        "file_name": resource.file_name,
        "file_path": resource.file_path,
        "file_size": resource.file_size,
        "mime_type": resource.mime_type,
        "url": f"/resources/{resource.id}",  # 使用公开访问路径
        "created_at": resource.created_at.isoformat() if resource.created_at else None
    })


@app.get("/admin/questions/{question_id}/resources/{resource_id}/download", tags=["🖥️ Admin Questions"])
async def admin_download_resource(
    question_id: str,
    resource_id: str,
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db)
):
    """管理后台资源下载端点"""
    from fastapi.responses import FileResponse
    from pathlib import Path
    from app.models.question_models import QuestionResource

    # 获取资源记录
    resource = qbank_db.query(QuestionResource).filter(
        QuestionResource.id == resource_id,
        QuestionResource.question_id == question_id
    ).first()

    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")

    # 构建文件路径
    base_storage = Path("storage")
    file_path = base_storage / resource.file_path

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="资源文件不存在")

    # 返回文件
    return FileResponse(
        path=str(file_path),
        filename=resource.file_name,
        media_type=resource.mime_type or "application/octet-stream"
    )


@app.get("/admin/llm", response_class=HTMLResponse)
async def admin_llm(
    request: Request,
    current_admin = Depends(admin_required),
    main_db: Session = Depends(get_main_db),
    qbank_db: Session = Depends(get_qbank_db)
):
    """LLM Configuration page"""
    # 获取接口配置
    interfaces = qbank_db.query(LLMInterface).filter_by(user_id=current_admin['id']).all()
    
    # 获取模板
    prompt_templates = qbank_db.query(PromptTemplate).filter(
        (PromptTemplate.user_id == current_admin['id']) | 
        (PromptTemplate.is_public == True) |
        (PromptTemplate.is_system == True)
    ).all()
    
    # 获取题库列表
    question_banks = qbank_db.query(QuestionBankV2).limit(100).all()
    
    return templates.TemplateResponse("admin/llm.html", {
        "request": request,
        "current_user": current_admin,
        "interfaces": interfaces,
        "templates": prompt_templates,
        "question_banks": question_banks
    })


@app.get("/admin/imports", response_class=HTMLResponse)
async def admin_imports(
    request: Request,
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Import/Export page"""
    banks = qbank_db.query(QuestionBankV2).limit(100).all()
    
    for bank in banks:
        bank.question_count = qbank_db.query(QuestionV2).filter(
            QuestionV2.bank_id == bank.id
        ).count()
    
    return templates.TemplateResponse("admin/imports.html", {
        "request": request,
        "current_user": current_admin,
        "banks": banks
    })


# ==================== AI Configuration Management Routes ====================

@app.get("/admin/ai-configs", response_class=HTMLResponse, tags=["🤖 AI Configuration"])
async def admin_ai_configs(
    request: Request,
    current_admin = Depends(admin_required),
    main_db: Session = Depends(get_main_db)
):
    """AI configurations management page"""
    from app.models.ai_models import AIConfig, ChatSession, ChatMessage
    from sqlalchemy import func, desc

    # Get all AI configs
    configs = main_db.query(AIConfig).order_by(desc(AIConfig.created_at)).all()

    # Get statistics
    total_configs = main_db.query(AIConfig).count()
    total_sessions = main_db.query(ChatSession).count()
    total_messages = main_db.query(ChatMessage).count()
    total_tokens = main_db.query(func.sum(ChatSession.total_tokens)).scalar() or 0

    # Get recent sessions
    recent_sessions = main_db.query(ChatSession).order_by(
        desc(ChatSession.last_activity_at)
    ).limit(10).all()

    return templates.TemplateResponse("admin/ai_configs.html", {
        "request": request,
        "current_user": current_admin,
        "configs": configs,
        "total_configs": total_configs,
        "total_sessions": total_sessions,
        "total_messages": total_messages,
        "total_tokens": total_tokens,
        "recent_sessions": recent_sessions
    })


@app.get("/admin/ai-configs/create", response_class=HTMLResponse, tags=["🤖 AI Configuration"])
async def admin_ai_configs_create_form(
    request: Request,
    current_admin = Depends(admin_required)
):
    """Show create AI config form"""
    return templates.TemplateResponse("admin/ai_config_form.html", {
        "request": request,
        "current_user": current_admin,
        "config": None
    })


@app.post("/admin/ai-configs/create", tags=["🤖 AI Configuration"])
async def admin_ai_configs_create(
    request: Request,
    name: str = Form(...),
    provider: str = Form(...),
    model_name: str = Form(...),
    api_key: str = Form(...),
    base_url: Optional[str] = Form(None),
    temperature: float = Form(0.7),
    max_tokens: int = Form(2000),
    top_p: float = Form(1.0),
    is_default: bool = Form(False),
    description: Optional[str] = Form(None),
    current_admin = Depends(admin_required),
    main_db: Session = Depends(get_main_db)
):
    """Create new AI config"""
    from app.models.ai_models import AIConfig
    import uuid

    try:
        # If setting as default, unset other defaults for this user
        if is_default:
            main_db.query(AIConfig).filter(
                AIConfig.user_id == current_admin["id"],
                AIConfig.is_default == True
            ).update({"is_default": False})

        # Create config
        config = AIConfig(
            id=str(uuid.uuid4()),
            user_id=current_admin["id"],
            name=name,
            provider=provider,
            model_name=model_name,
            api_key=api_key,  # TODO: Encrypt this
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            is_default=is_default,
            description=description
        )

        main_db.add(config)
        main_db.commit()

        return RedirectResponse(url="/admin/ai-configs", status_code=303)

    except Exception as e:
        main_db.rollback()
        return templates.TemplateResponse("admin/ai_config_form.html", {
            "request": request,
            "current_user": current_admin,
            "config": None,
            "error": f"创建失败: {str(e)}"
        })


@app.get("/admin/ai-configs/{config_id}/edit", response_class=HTMLResponse, tags=["🤖 AI Configuration"])
async def admin_ai_configs_edit_form(
    request: Request,
    config_id: str,
    current_admin = Depends(admin_required),
    main_db: Session = Depends(get_main_db)
):
    """Show edit AI config form"""
    from app.models.ai_models import AIConfig

    config = main_db.query(AIConfig).filter(AIConfig.id == config_id).first()

    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    return templates.TemplateResponse("admin/ai_config_form.html", {
        "request": request,
        "current_user": current_admin,
        "config": config
    })


@app.post("/admin/ai-configs/{config_id}/edit", tags=["🤖 AI Configuration"])
async def admin_ai_configs_edit(
    request: Request,
    config_id: str,
    name: str = Form(...),
    model_name: str = Form(...),
    api_key: Optional[str] = Form(None),
    base_url: Optional[str] = Form(None),
    temperature: float = Form(0.7),
    max_tokens: int = Form(2000),
    top_p: float = Form(1.0),
    is_default: bool = Form(False),
    description: Optional[str] = Form(None),
    current_admin = Depends(admin_required),
    main_db: Session = Depends(get_main_db)
):
    """Update AI config"""
    from app.models.ai_models import AIConfig
    from datetime import datetime

    config = main_db.query(AIConfig).filter(AIConfig.id == config_id).first()

    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    try:
        # If setting as default, unset other defaults for this user
        if is_default and not config.is_default:
            main_db.query(AIConfig).filter(
                AIConfig.user_id == config.user_id,
                AIConfig.is_default == True,
                AIConfig.id != config_id
            ).update({"is_default": False})

        # Update config
        config.name = name
        config.model_name = model_name
        if api_key and api_key != "••••••••":
            config.api_key = api_key  # TODO: Encrypt this
        config.base_url = base_url
        config.temperature = temperature
        config.max_tokens = max_tokens
        config.top_p = top_p
        config.is_default = is_default
        config.description = description
        config.updated_at = datetime.utcnow()

        main_db.commit()

        return RedirectResponse(url="/admin/ai-configs", status_code=303)

    except Exception as e:
        main_db.rollback()
        return templates.TemplateResponse("admin/ai_config_form.html", {
            "request": request,
            "current_user": current_admin,
            "config": config,
            "error": f"更新失败: {str(e)}"
        })


@app.post("/admin/ai-configs/{config_id}/delete", tags=["🤖 AI Configuration"])
async def admin_ai_configs_delete(
    config_id: str,
    current_admin = Depends(admin_required),
    main_db: Session = Depends(get_main_db)
):
    """Delete AI config"""
    from app.models.ai_models import AIConfig

    config = main_db.query(AIConfig).filter(AIConfig.id == config_id).first()

    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    # Delete config (cascades to sessions and messages)
    main_db.delete(config)
    main_db.commit()

    return RedirectResponse(url="/admin/ai-configs", status_code=303)


@app.get("/admin/ai-sessions/{session_id}", response_class=HTMLResponse, tags=["🤖 AI Configuration"])
async def admin_ai_session_detail(
    request: Request,
    session_id: str,
    current_admin = Depends(admin_required),
    main_db: Session = Depends(get_main_db)
):
    """AI session detail page"""
    from app.models.ai_models import ChatSession, ChatMessage

    session = main_db.query(ChatSession).filter(ChatSession.id == session_id).first()

    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    # Get messages
    messages = main_db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()

    return templates.TemplateResponse("admin/ai_session_detail.html", {
        "request": request,
        "current_user": current_admin,
        "session": session,
        "messages": messages
    })


@app.post("/admin/ai-sessions/{session_id}/delete", tags=["🤖 AI Configuration"])
async def admin_ai_session_delete(
    session_id: str,
    current_admin = Depends(admin_required),
    main_db: Session = Depends(get_main_db)
):
    """Delete AI session"""
    from app.models.ai_models import ChatSession

    session = main_db.query(ChatSession).filter(ChatSession.id == session_id).first()

    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    # Delete session (cascades to messages)
    main_db.delete(session)
    main_db.commit()

    return RedirectResponse(url="/admin/ai-configs", status_code=303)


@app.post("/admin/ai-configs/test-api", tags=["🤖 AI Configuration"])
async def test_ai_api_connection(request: Request):
    """Test AI API connection"""
    import time
    from app.services.ai.base import AIModelConfig, Message, MessageRole
    from app.services.ai.openai_service import OpenAIService
    from app.services.ai.claude_service import ClaudeService
    from app.services.ai.zhipu_service import ZhipuService
    import logging

    logger = logging.getLogger(__name__)

    try:
        data = await request.json()

        # 详细日志：接收到的数据
        logger.info("=" * 70)
        logger.info("API测试请求")
        logger.info(f"Provider: {data.get('provider')}")
        logger.info(f"Model: {data.get('model_name')}")
        logger.info(f"API Key: {data.get('api_key', '')[:15]}...{data.get('api_key', '')[-4:]}")
        logger.info(f"Base URL: {data.get('base_url')}")
        logger.info(f"Temperature: {data.get('temperature', 0.7)}")
        logger.info(f"Max Tokens: {data.get('max_tokens', 2000)}")
        logger.info("=" * 70)

        # Create AI config
        ai_config = AIModelConfig(
            model_name=data['model_name'],
            api_key=data['api_key'],
            base_url=data.get('base_url'),
            temperature=data.get('temperature', 0.7),
            max_tokens=data.get('max_tokens', 2000),
            top_p=data.get('top_p', 1.0)
        )

        logger.info(f"创建的AI配置 - Base URL: {ai_config.base_url}")

        # Select service based on provider
        provider = data['provider']
        logger.info(f"选择服务提供商: {provider}")

        if provider == 'openai':
            service = OpenAIService(ai_config)
        elif provider == 'claude':
            service = ClaudeService(ai_config)
        elif provider == 'zhipu':
            service = ZhipuService(ai_config)
        else:  # custom
            # Try OpenAI format first (most compatible)
            service = OpenAIService(ai_config)

        logger.info(f"服务创建完成 - Service Base URL: {service.base_url}")
        logger.info(f"服务创建完成 - Service API Key: {service.api_key[:15]}...{service.api_key[-4:]}")

        # Test with a simple message
        test_messages = [
            Message(role=MessageRole.user, content="Hello! Please respond with 'OK' if you can read this.")
        ]

        logger.info("开始发送测试消息...")
        start_time = time.time()

        try:
            response = await service.chat(test_messages)
            response_time = f"{(time.time() - start_time):.2f}s"

            logger.info(f"✅ API测试成功!")
            logger.info(f"响应时间: {response_time}")
            logger.info(f"响应内容: {response.content[:100]}")
            logger.info("=" * 70)

            return JSONResponse({
                "success": True,
                "response_time": response_time,
                "model": data['model_name']
            })
        except Exception as api_error:
            logger.error(f"❌ API调用失败: {str(api_error)}")
            logger.error(f"错误类型: {type(api_error).__name__}")
            logger.error("=" * 70)
            raise

    except Exception as e:
        logger.error(f"❌ 测试路由异常: {str(e)}")
        logger.error(f"异常类型: {type(e).__name__}")
        import traceback
        logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
        logger.error("=" * 70)

        return JSONResponse({
            "success": False,
            "error": str(e)
        })


@app.post("/admin/ai-configs/test-chat", tags=["🤖 AI Configuration"])
async def test_ai_chat(request: Request):
    """Test AI chat conversation"""
    from app.services.ai.base import AIModelConfig, Message, MessageRole
    from app.services.ai.openai_service import OpenAIService
    from app.services.ai.claude_service import ClaudeService
    from app.services.ai.zhipu_service import ZhipuService

    try:
        data = await request.json()
        config_data = data['config']
        user_message = data['message']

        # Create AI config
        ai_config = AIModelConfig(
            model_name=config_data['model_name'],
            api_key=config_data['api_key'],
            base_url=config_data.get('base_url'),
            temperature=config_data.get('temperature', 0.7),
            max_tokens=config_data.get('max_tokens', 2000),
            top_p=config_data.get('top_p', 1.0)
        )

        # Select service based on provider
        provider = config_data['provider']
        if provider == 'openai':
            service = OpenAIService(ai_config)
        elif provider == 'claude':
            service = ClaudeService(ai_config)
        elif provider == 'zhipu':
            service = ZhipuService(ai_config)
        else:  # custom
            service = OpenAIService(ai_config)

        # Send user message
        messages = [
            Message(role=MessageRole.user, content=user_message)
        ]

        response = await service.chat(messages)

        return JSONResponse({
            "success": True,
            "content": response.content
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        })


# ==================== Question Import/Export Routes ====================

@app.post("/admin/imports/csv")
async def admin_import_csv(
    request: Request,
    bank_id: str = Form(...),
    file: UploadFile = File(...),
    merge_duplicates: bool = Form(True),
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Import questions from CSV, JSON, or ZIP file (with multimedia)"""
    import csv
    import io
    import json
    import uuid
    import shutil
    from pathlib import Path
    from app.models.question_models import QuestionResource
    
    # Check file type and handle accordingly
    filename = file.filename.lower()

    if filename.endswith('.zip'):
        # Handle ZIP import (with multimedia resources)
        try:
            import tempfile
            import os

            # Create temporary directory for extraction
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, file.filename)

            # Save uploaded ZIP file
            content = await file.read()
            with open(zip_path, 'wb') as f:
                f.write(content)

            # Extract ZIP
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(temp_dir)

            # Read questions.json
            questions_json_path = os.path.join(temp_dir, 'questions.json')
            if not os.path.exists(questions_json_path):
                raise HTTPException(status_code=400, detail="ZIP文件中缺少questions.json")

            with open(questions_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            imported_count = 0
            resources_dir = os.path.join(temp_dir, 'resources')

            for q_data in data.get('questions', []):
                question_id = str(uuid.uuid4())

                # Determine question type
                q_type = q_data.get('type', 'single')

                # Get meta_data
                meta_data = q_data.get('meta_data')

                question = QuestionV2(
                    id=question_id,
                    bank_id=bank_id,
                    question_number=q_data.get('number'),
                    stem=q_data.get('stem', ''),
                    stem_format='text',
                    type=q_type,
                    difficulty=q_data.get('difficulty', 'medium'),
                    category=q_data.get('category', ''),
                    explanation=q_data.get('explanation', ''),
                    meta_data=meta_data if meta_data else None
                )
                qbank_db.add(question)

                # Add options for choice questions
                if q_type in ['single', 'multiple']:
                    for i, opt_data in enumerate(q_data.get('options', [])):
                        option = QuestionOptionV2(
                            id=str(uuid.uuid4()),
                            question_id=question_id,
                            option_label=opt_data.get('label', chr(65 + i)),
                            option_content=opt_data.get('content', ''),
                            option_format='text',
                            is_correct=opt_data.get('is_correct', False),
                            sort_order=i
                        )
                        qbank_db.add(option)

                # Import resources
                for res_data in q_data.get('resources', []):
                    old_resource_id = res_data.get('id')
                    new_resource_id = str(uuid.uuid4())

                    # Find resource file in extracted ZIP
                    resource_file_pattern = f"{old_resource_id}_{res_data.get('file_name')}"
                    resource_file_path = os.path.join(resources_dir, resource_file_pattern)

                    if os.path.exists(resource_file_path):
                        # Determine storage path based on resource type
                        resource_type = res_data.get('resource_type', 'image')
                        storage_base = Path("storage") / "question_banks" / bank_id / resource_type
                        storage_base.mkdir(parents=True, exist_ok=True)

                        # Copy file to storage
                        file_ext = Path(res_data.get('file_name')).suffix
                        new_file_name = f"{new_resource_id}{file_ext}"
                        new_file_path = storage_base / new_file_name

                        shutil.copy2(resource_file_path, new_file_path)

                        # Update stem and options to use new resource ID
                        old_url_pattern = f"/resources/{old_resource_id}"
                        new_url = f"/resources/{new_resource_id}"

                        # Update question stem
                        if old_url_pattern in question.stem:
                            question.stem = question.stem.replace(old_url_pattern, new_url)

                        # Update question explanation
                        if question.explanation and old_url_pattern in question.explanation:
                            question.explanation = question.explanation.replace(old_url_pattern, new_url)

                        # Update options content
                        if q_type in ['single', 'multiple']:
                            options = qbank_db.query(QuestionOptionV2).filter(
                                QuestionOptionV2.question_id == question_id
                            ).all()
                            for opt in options:
                                if old_url_pattern in opt.option_content:
                                    opt.option_content = opt.option_content.replace(old_url_pattern, new_url)

                        # Create resource record
                        relative_path = str(new_file_path.relative_to(Path("storage")))

                        # Build meta_data with width, height, duration
                        meta_data = {}
                        if res_data.get('width'):
                            meta_data['width'] = res_data.get('width')
                        if res_data.get('height'):
                            meta_data['height'] = res_data.get('height')
                        if res_data.get('duration'):
                            meta_data['duration'] = res_data.get('duration')

                        resource = QuestionResource(
                            id=new_resource_id,
                            question_id=question_id,
                            file_name=res_data.get('file_name'),
                            file_path=relative_path,
                            file_size=res_data.get('file_size', 0),
                            mime_type=res_data.get('mime_type'),
                            resource_type=resource_type,
                            meta_data=meta_data if meta_data else None
                        )
                        qbank_db.add(resource)

                imported_count += 1

            qbank_db.commit()

            # Clean up temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)

            return RedirectResponse(
                url=f"/admin/imports?success=imported_{imported_count}_questions_with_resources",
                status_code=303
            )

        except Exception as e:
            qbank_db.rollback()
            if 'temp_dir' in locals():
                shutil.rmtree(temp_dir, ignore_errors=True)
            return RedirectResponse(
                url=f"/admin/imports?error={str(e)}",
                status_code=303
            )

    elif filename.endswith('.json'):
        # Handle JSON import
        try:
            content = await file.read()
            data = json.loads(content.decode('utf-8'))
            
            # Check if bank_id matches or create new bank
            if 'bank_info' in data:
                # If JSON contains bank info, use it
                json_bank_id = data['bank_info'].get('id')
                if json_bank_id and json_bank_id != bank_id:
                    # Check if we should use the JSON bank or the selected one
                    pass  # For now, use the selected bank_id
            
            imported_count = 0
            
            for q_data in data.get('questions', []):
                question_id = str(uuid.uuid4())
                
                # Determine question type
                q_type = q_data.get('type', 'single')
                
                # Create meta_data for special question types
                meta_data = {}
                if q_type == 'fill':
                    # Extract blanks from stem
                    import re
                    blanks = re.findall(r'____+', q_data.get('stem', ''))
                    meta_data['blanks'] = [
                        {'position': i, 'answer': '', 'alternatives': []}
                        for i in range(len(blanks))
                    ]
                elif q_type == 'judge':
                    # Try to determine answer from various possible fields
                    # Check for 'answer' field directly
                    if 'answer' in q_data:
                        meta_data['answer'] = q_data['answer']
                    # Check if answer is in meta_data
                    elif 'meta_data' in q_data and 'answer' in q_data['meta_data']:
                        meta_data['answer'] = q_data['meta_data']['answer']
                    # Check explanation for hints (if contains "正确" or "错误")
                    elif '正确' in q_data.get('explanation', ''):
                        meta_data['answer'] = True
                    elif '错误' in q_data.get('explanation', ''):
                        meta_data['answer'] = False
                    else:
                        # Default to False if can't determine
                        meta_data['answer'] = False
                elif q_type == 'essay':
                    # Handle essay questions
                    if 'meta_data' in q_data:
                        meta_data = q_data['meta_data']
                    else:
                        meta_data['reference_answer'] = q_data.get('explanation', '')
                
                question = QuestionV2(
                    id=question_id,
                    bank_id=bank_id,
                    question_number=q_data.get('number'),
                    stem=q_data.get('stem', ''),
                    stem_format='text',
                    type=q_type,
                    difficulty=q_data.get('difficulty', 'medium'),
                    category=q_data.get('category', ''),
                    explanation=q_data.get('explanation', ''),
                    meta_data=meta_data if meta_data else None
                )
                qbank_db.add(question)
                
                # Add options for choice questions
                if q_type in ['single', 'multiple']:
                    for i, opt_data in enumerate(q_data.get('options', [])):
                        option = QuestionOptionV2(
                            id=str(uuid.uuid4()),
                            question_id=question_id,
                            option_label=opt_data.get('label', chr(65 + i)),
                            option_content=opt_data.get('content', ''),
                            option_format='text',
                            is_correct=opt_data.get('is_correct', False),
                            sort_order=i
                        )
                        qbank_db.add(option)
                
                imported_count += 1
            
            qbank_db.commit()
            
            return RedirectResponse(
                url=f"/admin/imports?success=imported_{imported_count}_questions",
                status_code=303
            )
            
        except Exception as e:
            qbank_db.rollback()
            return RedirectResponse(
                url=f"/admin/imports?error={str(e)}",
                status_code=303
            )
    
    elif not filename.endswith('.csv'):
        return RedirectResponse(url="/admin/imports?error=invalid_file", status_code=303)
    
    # Check bank exists
    bank = qbank_db.query(QuestionBankV2).filter(QuestionBankV2.id == bank_id).first()
    if not bank:
        return RedirectResponse(url="/admin/imports?error=bank_not_found", status_code=303)
    
    try:
        # Read CSV file
        content = await file.read()
        csv_file = io.StringIO(content.decode('utf-8-sig'))  # Handle BOM
        reader = csv.DictReader(csv_file)
        
        imported_count = 0
        
        for row in reader:
            # Skip empty rows
            if not row.get('题干'):
                continue
            
            # Create question
            question_id = str(uuid.uuid4())
            question = QuestionV2(
                id=question_id,
                bank_id=bank_id,
                question_number=int(row.get('题号', 0)),
                stem=row.get('题干', ''),
                stem_format='text',
                type='single' if len(row.get('答案', '')) == 1 else 'multiple',
                difficulty=row.get('难度', 'medium'),
                category=row.get('题型', ''),
                explanation=row.get('解析', '')
            )
            qbank_db.add(question)
            
            # Create options dynamically
            answer = row.get('答案', '')
            
            # Detect all option columns in the CSV (A, B, C, D, E, F, G, ...)
            option_labels = []
            for key in row.keys():
                # Check if the key is a single uppercase letter (option label)
                if len(key) == 1 and key.isupper() and ord('A') <= ord(key) <= ord('Z'):
                    option_labels.append(key)
            
            # Sort option labels alphabetically
            option_labels.sort()
            
            # Create options for all detected labels
            for label in option_labels:
                if row.get(label):  # Only create if option content exists
                    option = QuestionOptionV2(
                        id=str(uuid.uuid4()),
                        question_id=question_id,
                        option_label=label,
                        option_content=row[label],
                        option_format='text',
                        is_correct=(label in answer),
                        sort_order=ord(label) - ord('A')
                    )
                    qbank_db.add(option)
            
            imported_count += 1
        
        qbank_db.commit()
        
        return RedirectResponse(
            url=f"/admin/imports?success=imported_{imported_count}_questions",
            status_code=303
        )
        
    except Exception as e:
        qbank_db.rollback()
        return RedirectResponse(
            url=f"/admin/imports?error={str(e)}",
            status_code=303
        )


@app.get("/admin/imports/template")
async def admin_download_template():
    """Download CSV template"""
    from fastapi.responses import Response
    
    # 模板现在支持动态数量的选项，可以添加任意多的选项列
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
            'Content-Disposition': 'attachment; filename=template.csv'
        }
    )


@app.get("/admin/exports/{bank_id}")
async def admin_export_bank(
    bank_id: str,
    format: str = "csv",
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Export question bank to CSV, JSON, or ZIP (with multimedia)"""
    from fastapi.responses import Response, FileResponse
    import csv
    import io
    import json
    import zipfile
    import tempfile
    import shutil
    from pathlib import Path
    from app.models.question_models import QuestionResource

    # Get bank using V2
    bank = qbank_db.query(QuestionBankV2).filter(QuestionBankV2.id == bank_id).first()
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")

    # Get questions with options
    questions = qbank_db.query(QuestionV2).filter(
        QuestionV2.bank_id == bank_id
    ).order_by(QuestionV2.question_number).all()
    
    if format == "csv":
            
        # First pass: determine the maximum number of options in the bank
        max_options = 0
        all_question_options = []
        
        for question in questions:
            options = qbank_db.query(QuestionOptionV2).filter(
                QuestionOptionV2.question_id == question.id
            ).order_by(QuestionOptionV2.sort_order).all()
            all_question_options.append(options)
            max_options = max(max_options, len(options))
        
        # Ensure at least 4 options columns (A, B, C, D)
        max_options = max(max_options, 4)
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Generate dynamic header based on max options
        header = ["题号", "题干"]
        for i in range(max_options):
            # Generate option labels: A, B, C, D, E, F, G, ...
            label = chr(65 + i)  # 65 is ASCII for 'A'
            header.append(label)
        header.extend(["答案", "难度", "题型", "解析"])
        writer.writerow(header)
        
        # Write questions with dynamic options
        for idx, question in enumerate(questions):
            options = all_question_options[idx]
            options_dict = {opt.option_label: opt.option_content for opt in options}
            answer = "".join([opt.option_label for opt in options if opt.is_correct])
            
            row = [
                question.question_number or "",
                question.stem
            ]
            
            # Add options dynamically
            for i in range(max_options):
                label = chr(65 + i)
                row.append(options_dict.get(label, ""))
            
            # Add other fields
            row.extend([
                answer,
                question.difficulty or "",
                question.category or "",
                question.explanation or ""
            ])
            
            writer.writerow(row)
        
        # Return as downloadable file
        content = output.getvalue().encode('utf-8-sig')
        # Use urllib.parse.quote to properly encode Chinese characters in filename
        from urllib.parse import quote
        safe_filename = quote(f"{bank.name}_export.csv")
        return Response(
            content=content,
            media_type='text/csv',
            headers={
                'Content-Disposition': f"attachment; filename*=UTF-8''{safe_filename}"
            }
        )
    
    elif format == "json":
        # Create JSON structure
        export_data = {
            "bank_info": {
                "id": bank.id,
                "name": bank.name,
                "description": bank.description,
                "category": bank.category
            },
            "questions": []
        }
        
        for question in questions:
            options = qbank_db.query(QuestionOptionV2).filter(
                QuestionOptionV2.question_id == question.id
            ).order_by(QuestionOptionV2.sort_order).all()
            
            q_data = {
                "number": question.question_number,
                "stem": question.stem,
                "type": question.type,
                "difficulty": question.difficulty,
                "category": question.category,
                "explanation": question.explanation,
                "options": [
                    {
                        "label": opt.option_label,
                        "content": opt.option_content,
                        "is_correct": opt.is_correct
                    }
                    for opt in options
                ]
            }
            export_data["questions"].append(q_data)
        
        # Return as downloadable file
        content = json.dumps(export_data, ensure_ascii=False, indent=2).encode('utf-8')
        # Use urllib.parse.quote to properly encode Chinese characters in filename
        from urllib.parse import quote
        safe_filename = quote(f"{bank.name}_export.json")
        return Response(
            content=content,
            media_type='application/json',
            headers={
                'Content-Disposition': f"attachment; filename*=UTF-8''{safe_filename}"
            }
        )

    elif format == "zip":
        # Export as ZIP with multimedia resources
        # Create a temporary directory for the ZIP file
        temp_dir = tempfile.mkdtemp()
        zip_path = Path(temp_dir) / f"{bank.name}_export.zip"

        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Create JSON data with resource information
                export_data = {
                    "bank_info": {
                        "id": bank.id,
                        "name": bank.name,
                        "description": bank.description,
                        "category": bank.category
                    },
                    "questions": []
                }

                # Track which resources we've added to avoid duplicates
                added_resources = set()

                for question in questions:
                    # Get question options
                    options = qbank_db.query(QuestionOptionV2).filter(
                        QuestionOptionV2.question_id == question.id
                    ).order_by(QuestionOptionV2.sort_order).all()

                    # Get question resources
                    resources = qbank_db.query(QuestionResource).filter(
                        QuestionResource.question_id == question.id
                    ).all()

                    q_data = {
                        "id": question.id,
                        "number": question.question_number,
                        "stem": question.stem,
                        "type": question.type,
                        "difficulty": question.difficulty,
                        "category": question.category,
                        "explanation": question.explanation,
                        "meta_data": question.meta_data,
                        "options": [
                            {
                                "label": opt.option_label,
                                "content": opt.option_content,
                                "is_correct": opt.is_correct
                            }
                            for opt in options
                        ],
                        "resources": []
                    }

                    # Add resources to ZIP and track them
                    for resource in resources:
                        if resource.id not in added_resources:
                            # Copy resource file to ZIP
                            resource_path = Path("storage") / resource.file_path
                            if resource_path.exists():
                                # Use original filename but keep it unique with resource ID
                                zip_resource_name = f"resources/{resource.id}_{resource.file_name}"
                                zipf.write(resource_path, zip_resource_name)
                                added_resources.add(resource.id)

                        # Add resource metadata to question
                        # Extract width, height, duration from meta_data if available
                        meta = resource.meta_data or {}
                        q_data["resources"].append({
                            "id": resource.id,
                            "file_name": resource.file_name,
                            "resource_type": resource.resource_type,
                            "mime_type": resource.mime_type,
                            "file_size": resource.file_size,
                            "width": meta.get("width"),
                            "height": meta.get("height"),
                            "duration": meta.get("duration")
                        })

                    export_data["questions"].append(q_data)

                # Add questions.json to ZIP
                questions_json = json.dumps(export_data, ensure_ascii=False, indent=2)
                zipf.writestr("questions.json", questions_json)

            # Return the ZIP file
            from urllib.parse import quote
            safe_filename = quote(f"{bank.name}_export.zip")

            return FileResponse(
                path=str(zip_path),
                media_type='application/zip',
                filename=f"{bank.name}_export.zip",
                headers={
                    'Content-Disposition': f"attachment; filename*=UTF-8''{safe_filename}"
                },
                background=lambda: shutil.rmtree(temp_dir, ignore_errors=True)
            )

        except Exception as e:
            # Clean up on error
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


# API endpoints
@app.get("/", tags=["🔧 System Status"])
async def root():
    """Root endpoint"""
    return {
        "app": "EXAM-MASTER",
        "version": settings.app_version,
        "api_docs": "/api/docs",
        "admin_panel": "/admin",
        "status": "running"
    }


# V2 Import/Export Routes
@app.post("/admin/v2/imports/{bank_id}", tags=["📥 Legacy Import/Export"])
async def admin_import_v2(
    bank_id: str,
    file: UploadFile = File(...),
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Import questions using V2 service"""
    service = QuestionBankService(qbank_db)
    
    # Save uploaded file temporarily
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # Import using service
        imported_count = service.import_questions(bank_id, tmp_path)
        return {"success": True, "imported_count": imported_count}
    finally:
        # Clean up temp file
        os.unlink(tmp_path)


@app.get("/admin/v2/exports/{bank_id}", tags=["📥 Legacy Import/Export"])
async def admin_export_v2(
    bank_id: str,
    format: str = "json",
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Export question bank using V2 service"""
    from fastapi.responses import FileResponse
    import tempfile
    import os
    
    service = QuestionBankService(qbank_db)
    
    # Export using service
    export_path = service.export_question_bank(bank_id, format)
    
    if not export_path or not os.path.exists(export_path):
        raise HTTPException(status_code=500, detail="Export failed")
    
    # Get bank name for filename
    bank = qbank_db.query(QuestionBankV2).filter(QuestionBankV2.id == bank_id).first()
    filename = f"{bank.name}_export.{format}"
    
    return FileResponse(
        path=export_path,
        filename=filename,
        media_type='application/json' if format == 'json' else 'text/csv'
    )


@app.get("/health", tags=["🔧 System Status"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/resources/{resource_id}", tags=["📁 Public Resources"])
async def get_public_resource(
    resource_id: str,
    qbank_db: Session = Depends(get_qbank_db)
):
    """公开资源访问端点 - 用于学生答题时访问媒体资源"""
    from fastapi.responses import FileResponse
    from pathlib import Path
    from app.models.question_models import QuestionResource
    from app.models.question_models_v2 import QuestionResourceV2, QuestionBankResource

    # 先尝试从V2资源表查找
    resource = qbank_db.query(QuestionResourceV2).filter(
        QuestionResourceV2.id == resource_id
    ).first()

    # 如果没找到，尝试从题库级别资源表查找
    if not resource:
        resource = qbank_db.query(QuestionBankResource).filter(
            QuestionBankResource.id == resource_id
        ).first()

    # 如果还是没找到，尝试从旧的资源表查找
    if not resource:
        resource = qbank_db.query(QuestionResource).filter(
            QuestionResource.id == resource_id
        ).first()

    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")

    # 构建文件路径
    base_storage = Path("storage")
    file_path = base_storage / resource.resource_path if hasattr(resource, 'resource_path') else base_storage / resource.file_path

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="资源文件不存在")

    # 返回文件
    return FileResponse(
        path=str(file_path),
        filename=resource.file_name,
        media_type=resource.mime_type or "application/octet-stream",
        headers={
            "Cache-Control": "public, max-age=31536000",  # 缓存1年
            "Access-Control-Allow-Origin": "*"  # 允许跨域访问
        }
    )

# ==================== Agent Testing ====================

@app.get("/admin/agent-test", response_class=HTMLResponse, tags=["🤖 Agent Testing"])
async def admin_agent_test(
    request: Request,
    current_admin = Depends(admin_required),
    main_db: Session = Depends(get_main_db)
):
    """Agent测试页面"""
    from app.models.ai_models import AIConfig
    
    # 获取所有AI配置
    configs = main_db.query(AIConfig).filter(
        AIConfig.user_id == current_admin['id']
    ).all()
    
    return templates.TemplateResponse("admin/agent_test.html", {
        "request": request,
        "current_user": current_admin,
        "configs": configs
    })


@app.post("/admin/agent-test/chat", tags=["🤖 Agent Testing"])
async def admin_agent_test_chat(
    request: Request,
    current_admin = Depends(admin_required),
    main_db: Session = Depends(get_main_db),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Agent对话API"""
    from app.models.ai_models import AIConfig
    from app.services.ai.base import AIModelConfig, Message, MessageRole
    from app.services.ai.openai_service import OpenAIService
    from app.services.ai.agent_service import AgentService
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        data = await request.json()
        config_id = data['config_id']
        user_message = data['message']
        enable_agent = data.get('enable_agent', True)
        
        # 获取AI配置
        ai_config_db = main_db.query(AIConfig).filter(
            AIConfig.id == config_id,
            AIConfig.user_id == current_admin['id']
        ).first()
        
        if not ai_config_db:
            return JSONResponse({
                "success": False,
                "error": "AI配置不存在"
            })
        
        # 创建AI服务配置
        ai_model_config = AIModelConfig(
            model_name=ai_config_db.model_name,
            api_key=ai_config_db.api_key,
            base_url=ai_config_db.base_url,
            temperature=ai_config_db.temperature,
            max_tokens=ai_config_db.max_tokens,
            top_p=ai_config_db.top_p
        )
        
        # 创建AI服务
        if ai_config_db.provider == "openai" or ai_config_db.provider == "custom":
            ai_service = OpenAIService(ai_model_config)
        else:
            return JSONResponse({
                "success": False,
                "error": f"暂不支持的提供商: {ai_config_db.provider}"
            })
        
        # 如果启用Agent，创建Agent服务
        if enable_agent:
            agent = AgentService(
                ai_service=ai_service,
                qbank_db=qbank_db,
                user_id=current_admin['id'],
                max_tool_iterations=getattr(ai_config_db, 'max_tool_iterations', 5)
            )
            
            messages = [Message(role=MessageRole.user, content=user_message)]
            
            result = await agent.chat_with_tools(
                messages=messages,
                provider=ai_config_db.provider,
                enable_tools=True
            )
            
            return JSONResponse({
                "success": True,
                "response": result['content'],
                "tool_calls": result['tool_calls'],
                "total_iterations": result['total_iterations'],
                "agent_enabled": True
            })
        else:
            # 不使用Agent，直接对话
            messages = [Message(role=MessageRole.user, content=user_message)]
            response = await ai_service.chat(messages)
            
            return JSONResponse({
                "success": True,
                "response": response.content,
                "tool_calls": [],
                "total_iterations": 0,
                "agent_enabled": False
            })
            
    except Exception as e:
        logger.error(f"Agent测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

        return JSONResponse({
            "success": False,
            "error": str(e)
        })


# ==================== Admin Activation Code API Endpoints (Session Auth) ====================

@app.get("/admin/api/activation-codes", tags=["🔑 Admin Activation API"])
async def admin_api_get_activation_codes(
    request: Request,
    skip: int = 0,
    limit: int = 50,
    bank_id: Optional[str] = None,
    is_used: Optional[bool] = None,
    expire_type: Optional[str] = None,
    search: Optional[str] = None,
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db)
):
    """获取激活码列表（Admin Panel API with Session Auth）"""
    from app.models.activation import ActivationCode
    from app.models.question_models_v2 import QuestionBankV2
    from sqlalchemy import or_, func

    query = qbank_db.query(ActivationCode)

    # 筛选条件
    if bank_id:
        query = query.filter(ActivationCode.bank_id == bank_id)
    if is_used is not None:
        query = query.filter(ActivationCode.is_used == is_used)
    if expire_type:
        query = query.filter(ActivationCode.expire_type == expire_type)
    if search:
        query = query.filter(
            or_(
                ActivationCode.code.contains(search),
                ActivationCode.description.contains(search)
            )
        )

    # 按创建时间倒序
    query = query.order_by(ActivationCode.created_at.desc())

    total = query.count()
    codes = query.offset(skip).limit(limit).all()

    # 统计已使用/未使用数量
    used_count = qbank_db.query(func.count(ActivationCode.id)).filter(
        ActivationCode.is_used == True
    ).scalar() or 0
    unused_count = total - used_count

    # 获取题库名称
    bank_ids = list(set(c.bank_id for c in codes))
    banks = qbank_db.query(QuestionBankV2).filter(
        QuestionBankV2.id.in_(bank_ids)
    ).all()
    bank_names = {b.id: b.name for b in banks}

    # 构造响应
    response_list = [
        {
            "id": code.id,
            "code": code.code,
            "bank_id": code.bank_id,
            "bank_name": bank_names.get(code.bank_id),
            "created_by": code.created_by,
            "created_at": code.created_at.isoformat(),
            "expire_type": code.expire_type.value,
            "expire_days": code.expire_days,
            "is_used": code.is_used,
            "used_by": code.used_by,
            "used_at": code.used_at.isoformat() if code.used_at else None,
            "description": code.description
        }
        for code in codes
    ]

    return {
        "codes": response_list,
        "total": total,
        "used_count": used_count,
        "unused_count": unused_count
    }


@app.post("/admin/api/activation-codes", tags=["🔑 Admin Activation API"])
async def admin_api_create_activation_codes(
    request: Request,
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db)
):
    """创建激活码（Admin Panel API with Session Auth）"""
    from app.models.activation import ActivationCode, ExpireType
    from app.models.question_models_v2 import QuestionBankV2
    import uuid
    import random
    import string

    data = await request.json()

    # 验证必填字段
    if not data.get('bank_id'):
        return JSONResponse(
            status_code=400,
            content={"detail": "题库ID不能为空"}
        )

    # 检查题库是否存在
    bank = qbank_db.query(QuestionBankV2).filter(
        QuestionBankV2.id == data['bank_id']
    ).first()

    if not bank:
        return JSONResponse(
            status_code=404,
            content={"detail": "题库不存在"}
        )

    # 如果是临时激活码，必须指定天数
    expire_type = data.get('expire_type', 'permanent')
    expire_days = data.get('expire_days')

    if expire_type == 'temporary' and not expire_days:
        return JSONResponse(
            status_code=400,
            content={"detail": "临时激活码必须指定有效天数"}
        )

    # 生成激活码的辅助函数
    def generate_activation_code(length: int = 16) -> str:
        chars = string.ascii_uppercase.replace('O', '').replace('I', '').replace('L', '') + string.digits.replace('0', '').replace('1', '')
        return ''.join(random.choice(chars) for _ in range(length))

    # 批量生成激活码
    count = data.get('count', 1)
    created_codes = []

    for _ in range(count):
        # 生成唯一激活码
        while True:
            new_code = generate_activation_code()
            existing = qbank_db.query(ActivationCode).filter(
                ActivationCode.code == new_code
            ).first()
            if not existing:
                break

        # 创建激活码记录
        activation_code = ActivationCode(
            id=str(uuid.uuid4()),
            code=new_code,
            bank_id=data['bank_id'],
            created_by=current_admin['id'],
            created_at=datetime.utcnow(),
            expire_type=ExpireType(expire_type),
            expire_days=expire_days,
            is_used=False,
            description=data.get('description')
        )

        qbank_db.add(activation_code)
        created_codes.append(activation_code)

    qbank_db.commit()

    # 构造响应
    return [
        {
            "id": code.id,
            "code": code.code,
            "bank_id": code.bank_id,
            "bank_name": bank.name,
            "created_by": code.created_by,
            "created_at": code.created_at.isoformat(),
            "expire_type": code.expire_type.value,
            "expire_days": code.expire_days,
            "is_used": code.is_used,
            "used_by": code.used_by,
            "used_at": code.used_at.isoformat() if code.used_at else None,
            "description": code.description
        }
        for code in created_codes
    ]


@app.delete("/admin/api/activation-codes/{code_id}", tags=["🔑 Admin Activation API"])
async def admin_api_delete_activation_code(
    code_id: str,
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db)
):
    """删除激活码（Admin Panel API with Session Auth）"""
    from app.models.activation import ActivationCode

    code = qbank_db.query(ActivationCode).filter(
        ActivationCode.id == code_id
    ).first()

    if not code:
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": "激活码不存在"}
        )

    # 如果已被使用，不允许删除
    if code.is_used:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "已使用的激活码不能删除"}
        )

    qbank_db.delete(code)
    qbank_db.commit()

    return {"success": True, "message": "激活码已删除"}
