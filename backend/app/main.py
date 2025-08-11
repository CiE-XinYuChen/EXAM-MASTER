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
from app.api.v2 import api_router


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

# Include V2 API routes only
app.include_router(api_router, prefix="/api/v2")


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
@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    current_admin = Depends(admin_required),
    main_db: Session = Depends(get_main_db),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Admin dashboard"""
    # Get statistics using V2 models only
    total_users = main_db.query(User).count()
    total_banks = qbank_db.query(QuestionBankV2).count()
    total_questions = qbank_db.query(QuestionV2).count()
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "current_user": current_admin,
        "stats": {
            "users": total_users,
            "banks": total_banks,
            "questions": total_questions,
            "active": 0
        }
    })


@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """Admin login page"""
    return templates.TemplateResponse("admin/login.html", {"request": request})


@app.post("/admin/login")
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


@app.get("/admin/logout")
async def admin_logout(request: Request):
    """Admin logout"""
    session_id = request.cookies.get("admin_session")
    if session_id and session_id in admin_sessions:
        del admin_sessions[session_id]
    
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie(key="admin_session")
    return response


@app.get("/admin/users", response_class=HTMLResponse)
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


@app.get("/admin/users/create", response_class=HTMLResponse)
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


@app.post("/admin/users/create")
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


@app.get("/admin/users/{user_id}/edit", response_class=HTMLResponse)
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


@app.post("/admin/users/{user_id}/edit")
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


@app.get("/admin/users/{user_id}/password", response_class=HTMLResponse)
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


@app.post("/admin/users/{user_id}/password")
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


@app.post("/admin/users/{user_id}/delete")
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


@app.get("/admin/qbanks", response_class=HTMLResponse)
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


@app.get("/admin/qbanks/create", response_class=HTMLResponse)
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


@app.post("/admin/qbanks/create")
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


@app.get("/admin/qbanks/{bank_id}/edit", response_class=HTMLResponse)
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


@app.post("/admin/qbanks/{bank_id}/edit")
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


@app.post("/admin/qbanks/{bank_id}/delete")
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


@app.get("/admin/questions", response_class=HTMLResponse)
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


@app.get("/admin/questions/create", response_class=HTMLResponse)
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


@app.post("/admin/questions/create")
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


@app.get("/admin/questions/{question_id}/preview", response_class=HTMLResponse)
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


@app.get("/admin/questions/{question_id}/edit", response_class=HTMLResponse)
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


@app.post("/admin/questions/{question_id}/edit")
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
                elif key == "correct_option":
                    correct_options = [int(form_data[key])]
                elif key == "correct_options":
                    correct_options = [int(x) for x in form_data.getlist(key)]
            
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


@app.post("/admin/questions/{question_id}/delete")
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


@app.post("/admin/imports/csv")
async def admin_import_csv(
    request: Request,
    bank_id: str = Form(...),
    file: UploadFile = File(...),
    merge_duplicates: bool = Form(True),
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Import questions from CSV or JSON file"""
    import csv
    import io
    import json
    import uuid
    
    # Check file type and handle accordingly
    filename = file.filename.lower()
    if filename.endswith('.json'):
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
    """Export question bank to CSV or JSON"""
    from fastapi.responses import Response
    import csv
    import io
    import json
    
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


# API endpoints
@app.get("/")
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
@app.post("/admin/v2/imports/{bank_id}")
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


@app.get("/admin/v2/exports/{bank_id}")
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


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}