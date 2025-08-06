"""
Main FastAPI application with integrated admin panel
"""

from fastapi import FastAPI, Request, Depends, HTTPException, Form, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from typing import Optional
import secrets

from app.core.config import settings
from app.core.database import init_databases, get_main_db, get_qbank_db
from app.core.security import verify_password, get_password_hash, create_access_token, get_current_user
from app.api.v1 import api_router
from app.models.user_models import User, UserBankPermission, UserRole
from app.models.question_models import QuestionBank, Question


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

# Include API routes
app.include_router(api_router, prefix=settings.api_v1_prefix)


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
    # Get statistics
    total_users = main_db.query(User).count()
    total_banks = qbank_db.query(QuestionBank).count()
    total_questions = qbank_db.query(Question).count()
    
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


@app.get("/admin/qbanks", response_class=HTMLResponse)
async def admin_qbanks(
    request: Request,
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db),
    page: int = 1
):
    """Question banks management page"""
    per_page = 20
    skip = (page - 1) * per_page
    
    banks = qbank_db.query(QuestionBank).offset(skip).limit(per_page).all()
    
    # Add question count
    for bank in banks:
        bank.question_count = qbank_db.query(Question).filter(
            Question.bank_id == bank.id
        ).count()
    
    return templates.TemplateResponse("admin/qbanks.html", {
        "request": request,
        "current_user": current_admin,
        "banks": banks,
        "page": page
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
    """Create new question bank"""
    import uuid
    
    # Create question bank
    bank_id = str(uuid.uuid4())
    bank = QuestionBank(
        id=bank_id,
        name=name,
        description=description,
        category=category,
        is_public=is_public,
        creator_id=current_admin["id"],
        version="1.0.0"
    )
    
    qbank_db.add(bank)
    qbank_db.commit()
    
    # Grant admin permission to creator
    permission = UserBankPermission(
        user_id=current_admin["id"],
        bank_id=bank_id,
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
    """Show edit question bank form"""
    bank = qbank_db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
    
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
    """Update question bank"""
    bank = qbank_db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
    
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")
    
    bank.name = name
    bank.description = description
    bank.category = category
    bank.is_public = is_public
    
    qbank_db.commit()
    
    return RedirectResponse(url="/admin/qbanks", status_code=303)


@app.post("/admin/qbanks/{bank_id}/delete")
async def admin_qbanks_delete(
    bank_id: str,
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db),
    main_db: Session = Depends(get_main_db)
):
    """Delete question bank"""
    bank = qbank_db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
    
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")
    
    # Delete bank (cascades to questions, options, resources)
    qbank_db.delete(bank)
    qbank_db.commit()
    
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
    
    query = qbank_db.query(Question)
    
    if bank_id:
        query = query.filter(Question.bank_id == bank_id)
    
    # Get total count for pagination
    total_count = query.count()
    per_page = 20
    total_pages = math.ceil(total_count / per_page) if total_count > 0 else 1
    
    # Ensure page is within valid range
    page = max(1, min(page, total_pages))
    
    skip = (page - 1) * per_page
    questions = query.offset(skip).limit(per_page).all()
    
    # Get banks for filter
    banks = qbank_db.query(QuestionBank).limit(100).all()
    
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
    banks = qbank_db.query(QuestionBank).limit(100).all()
    
    return templates.TemplateResponse("admin/question_form.html", {
        "request": request,
        "current_user": current_admin,
        "question": None,
        "banks": banks,
        "selected_bank_id": bank_id,
        "action": "create"
    })


@app.post("/admin/questions/create")
async def admin_questions_create(
    request: Request,
    bank_id: str = Form(...),
    question_number: int = Form(0),
    stem: str = Form(...),
    type: str = Form(...),
    difficulty: str = Form("medium"),
    category: str = Form(""),
    explanation: str = Form(""),
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Create new question"""
    import uuid
    from app.models.question_models import QuestionOption
    
    # Create question
    question_id = str(uuid.uuid4())
    question = Question(
        id=question_id,
        bank_id=bank_id,
        question_number=question_number,
        stem=stem,
        type=type,
        difficulty=difficulty,
        category=category,
        explanation=explanation,
        stem_format="text",
        explanation_format="text"
    )
    
    qbank_db.add(question)
    
    # Handle options for choice questions
    if type in ["single", "multiple"]:
        # Get form data for options
        form_data = await request.form()
        option_labels = []
        option_contents = []
        correct_options = []
        
        # Extract options from form
        for key in form_data:
            if key.startswith("option_label_"):
                idx = key.replace("option_label_", "")
                option_labels.append((idx, form_data[key]))
            elif key.startswith("option_content_"):
                idx = key.replace("option_content_", "")
                option_contents.append((idx, form_data[key]))
            elif key.startswith("option_correct_"):
                idx = key.replace("option_correct_", "")
                correct_options.append(idx)
        
        # Sort and create options
        option_labels.sort(key=lambda x: x[0])
        option_contents.sort(key=lambda x: x[0])
        
        for i, (idx, label) in enumerate(option_labels):
            content = next((c for _, c in option_contents if _ == idx), "")
            if content:
                option = QuestionOption(
                    id=str(uuid.uuid4()),
                    question_id=question_id,
                    option_label=label,
                    option_content=content,
                    option_format="text",
                    is_correct=(idx in correct_options),
                    sort_order=i
                )
                qbank_db.add(option)
    
    qbank_db.commit()
    
    return RedirectResponse(url=f"/admin/questions?bank_id={bank_id}", status_code=303)


@app.get("/admin/questions/{question_id}/edit", response_class=HTMLResponse)
async def admin_questions_edit_form(
    request: Request,
    question_id: str,
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Show edit question form"""
    from app.models.question_models import QuestionOption
    
    question = qbank_db.query(Question).filter(Question.id == question_id).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    # Get banks for dropdown
    banks = qbank_db.query(QuestionBank).limit(100).all()
    
    # Get existing options
    options = qbank_db.query(QuestionOption).filter(
        QuestionOption.question_id == question_id
    ).order_by(QuestionOption.sort_order).all()
    
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
    bank_id: str = Form(...),
    question_number: int = Form(0),
    stem: str = Form(...),
    type: str = Form(...),
    difficulty: str = Form("medium"),
    category: str = Form(""),
    explanation: str = Form(""),
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Update question"""
    from app.models.question_models import QuestionOption
    import uuid
    
    question = qbank_db.query(Question).filter(Question.id == question_id).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    # Update question fields
    question.bank_id = bank_id
    question.question_number = question_number
    question.stem = stem
    question.type = type
    question.difficulty = difficulty
    question.category = category
    question.explanation = explanation
    
    # Delete existing options
    qbank_db.query(QuestionOption).filter(
        QuestionOption.question_id == question_id
    ).delete()
    
    # Handle options for choice questions
    if type in ["single", "multiple"]:
        # Get form data for options
        form_data = await request.form()
        option_labels = []
        option_contents = []
        correct_options = []
        
        # Extract options from form
        for key in form_data:
            if key.startswith("option_label_"):
                idx = key.replace("option_label_", "")
                option_labels.append((idx, form_data[key]))
            elif key.startswith("option_content_"):
                idx = key.replace("option_content_", "")
                option_contents.append((idx, form_data[key]))
            elif key.startswith("option_correct_"):
                idx = key.replace("option_correct_", "")
                correct_options.append(idx)
        
        # Sort and create options
        option_labels.sort(key=lambda x: x[0])
        option_contents.sort(key=lambda x: x[0])
        
        for i, (idx, label) in enumerate(option_labels):
            content = next((c for _, c in option_contents if _ == idx), "")
            if content:
                option = QuestionOption(
                    id=str(uuid.uuid4()),
                    question_id=question_id,
                    option_label=label,
                    option_content=content,
                    option_format="text",
                    is_correct=(idx in correct_options),
                    sort_order=i
                )
                qbank_db.add(option)
    
    qbank_db.commit()
    
    return RedirectResponse(url=f"/admin/questions?bank_id={bank_id}", status_code=303)


@app.post("/admin/questions/{question_id}/delete")
async def admin_questions_delete(
    question_id: str,
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Delete question"""
    question = qbank_db.query(Question).filter(Question.id == question_id).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    bank_id = question.bank_id
    
    # Delete question (cascades to options)
    qbank_db.delete(question)
    qbank_db.commit()
    
    return RedirectResponse(url=f"/admin/questions?bank_id={bank_id}", status_code=303)


@app.get("/admin/imports", response_class=HTMLResponse)
async def admin_imports(
    request: Request,
    current_admin = Depends(admin_required),
    qbank_db: Session = Depends(get_qbank_db)
):
    """Import/Export page"""
    banks = qbank_db.query(QuestionBank).limit(100).all()
    
    for bank in banks:
        bank.question_count = qbank_db.query(Question).filter(
            Question.bank_id == bank.id
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
    """Import questions from CSV file"""
    import csv
    import io
    import uuid
    from app.models.question_models import QuestionOption
    
    # Check file type
    if not file.filename.endswith('.csv'):
        return RedirectResponse(url="/admin/imports?error=invalid_file", status_code=303)
    
    # Check bank exists
    bank = qbank_db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
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
            question = Question(
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
                    option = QuestionOption(
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
    
    # Get bank
    bank = qbank_db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")
    
    # Get questions with options
    questions = qbank_db.query(Question).filter(
        Question.bank_id == bank_id
    ).order_by(Question.question_number).all()
    
    if format == "csv":
        from app.models.question_models import QuestionOption
        
        # First pass: determine the maximum number of options in the bank
        max_options = 0
        all_question_options = []
        
        for question in questions:
            options = qbank_db.query(QuestionOption).filter(
                QuestionOption.question_id == question.id
            ).order_by(QuestionOption.sort_order).all()
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
            from app.models.question_models import QuestionOption
            options = qbank_db.query(QuestionOption).filter(
                QuestionOption.question_id == question.id
            ).order_by(QuestionOption.sort_order).all()
            
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


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}