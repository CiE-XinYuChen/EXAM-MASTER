"""
Question Bank API V2 - 新架构API接口
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
import os
import json

from app.core.database import get_qbank_db
from app.core.security import get_current_user
from app.models.user_models import User
from app.models.question_models_v2 import QuestionType, QuestionBankV2, QuestionV2
from app.services.question_bank_service import QuestionBankService
from app.schemas.qbank_schemas_v2 import (
    QuestionBankCreate,
    QuestionBankUpdate,
    QuestionBankResponse,
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    QuestionImportRequest,
    QuestionExportRequest
)

router = APIRouter()


# ==================== 题库管理 ====================

@router.post("/banks", response_model=QuestionBankResponse, tags=["📚 Bank Management"])
async def create_question_bank(
    bank_data: QuestionBankCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """创建新题库"""
    service = QuestionBankService(db)
    bank = service.create_question_bank(
        name=bank_data.name,
        description=bank_data.description,
        category=bank_data.category,
        creator_id=current_user.id,
        tags=bank_data.tags,
        is_public=bank_data.is_public
    )
    return bank


@router.get("/banks", response_model=List[QuestionBankResponse], tags=["📚 Bank Management"])
async def list_question_banks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=10000),
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """获取题库列表"""
    query = db.query(QuestionBankV2)
    
    # 筛选条件
    if category:
        query = query.filter(QuestionBankV2.category == category)
    if search:
        query = query.filter(
            QuestionBankV2.name.contains(search) | 
            QuestionBankV2.description.contains(search)
        )
    
    # 权限过滤：只显示公开的或自己创建的
    query = query.filter(
        (QuestionBankV2.is_public == True) | 
        (QuestionBankV2.creator_id == current_user.id)
    )
    
    banks = query.offset(skip).limit(limit).all()
    return banks


@router.get("/banks/{bank_id}", response_model=QuestionBankResponse, tags=["📚 Bank Management"])
async def get_question_bank(
    bank_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """获取题库详情"""
    service = QuestionBankService(db)
    bank = service.get_question_bank(bank_id)
    
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")
    
    # 权限检查
    if not bank.is_public and bank.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问该题库")
    
    return bank


@router.put("/banks/{bank_id}", response_model=QuestionBankResponse, tags=["📚 Bank Management"])
async def update_question_bank(
    bank_id: str,
    bank_data: QuestionBankUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """更新题库信息"""
    service = QuestionBankService(db)
    bank = service.get_question_bank(bank_id)
    
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")
    
    # 权限检查
    if bank.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改该题库")
    
    # 更新
    update_data = bank_data.dict(exclude_unset=True)
    bank = service.update_question_bank(bank_id, **update_data)
    
    return bank


@router.delete("/banks/{bank_id}", tags=["📚 Bank Management"])
async def delete_question_bank(
    bank_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """删除题库"""
    service = QuestionBankService(db)
    bank = service.get_question_bank(bank_id)
    
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")
    
    # 权限检查
    if bank.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除该题库")
    
    service.delete_question_bank(bank_id)
    
    return {"message": "题库已删除"}


# ==================== 题目管理 ====================

@router.post("/banks/{bank_id}/questions", response_model=QuestionResponse, tags=["❓ Question Management"])
async def add_question(
    bank_id: str,
    question_data: QuestionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """添加题目到题库"""
    service = QuestionBankService(db)
    bank = service.get_question_bank(bank_id)
    
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")
    
    # 权限检查
    if bank.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权添加题目")
    
    question = service.add_question(
        bank_id=bank_id,
        stem=question_data.stem,
        type=question_data.type,
        options=question_data.options,
        meta_data=question_data.meta_data,
        difficulty=question_data.difficulty,
        category=question_data.category,
        explanation=question_data.explanation,
        question_number=question_data.question_number,
        tags=question_data.tags,
        score=question_data.score
    )
    
    return question


@router.get("/banks/{bank_id}/questions", response_model=List[QuestionResponse], tags=["❓ Question Management"])
async def list_questions(
    bank_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=10000),
    type: Optional[QuestionType] = None,
    difficulty: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """获取题库中的题目列表"""
    service = QuestionBankService(db)
    bank = service.get_question_bank(bank_id)
    
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")
    
    # 权限检查
    if not bank.is_public and bank.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问该题库")
    
    query = db.query(QuestionV2).filter(QuestionV2.bank_id == bank_id)
    
    if type:
        query = query.filter(QuestionV2.type == type)
    if difficulty:
        query = query.filter(QuestionV2.difficulty == difficulty)
    
    questions = query.offset(skip).limit(limit).all()
    return questions


@router.get("/questions/{question_id}", response_model=QuestionResponse, tags=["❓ Question Management"])
async def get_question(
    question_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """获取题目详情"""
    question = db.query(QuestionV2).filter(QuestionV2.id == question_id).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    # 权限检查
    bank = question.bank
    if not bank.is_public and bank.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问该题目")
    
    return question


@router.put("/questions/{question_id}", response_model=QuestionResponse, tags=["❓ Question Management"])
async def update_question(
    question_id: str,
    question_data: QuestionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """更新题目"""
    question = db.query(QuestionV2).filter(QuestionV2.id == question_id).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    # 权限检查
    bank = question.bank
    if bank.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改该题目")
    
    # 更新题目
    update_data = question_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(question, key):
            setattr(question, key, value)
    
    question.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(question)
    
    return question


@router.delete("/questions/{question_id}", tags=["❓ Question Management"])
async def delete_question(
    question_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """删除题目"""
    question = db.query(QuestionV2).filter(QuestionV2.id == question_id).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    # 权限检查
    bank = question.bank
    if bank.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除该题目")
    
    # 更新题库统计
    bank.total_questions -= 1
    
    db.delete(question)
    db.commit()
    
    return {"message": "题目已删除"}


# ==================== 资源管理 ====================

@router.post("/questions/{question_id}/images", tags=["🖼️ Media & Resources"])
async def upload_question_image(
    question_id: str,
    file: UploadFile = File(...),
    position: str = Form("stem"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """上传题目图片"""
    # 检查文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只能上传图片文件")
    
    # 检查文件大小（限制10MB）
    if file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片大小不能超过10MB")
    
    service = QuestionBankService(db)
    
    # 权限检查
    question = db.query(QuestionV2).filter(QuestionV2.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    if question.bank.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权上传图片")
    
    resource = await service.upload_question_image(question_id, file, position)
    
    return {
        "id": resource.id,
        "url": f"/api/v2/qbank/resources/{resource.id}",
        "path": resource.resource_path,
        "position": position
    }


@router.get("/resources/{resource_id}", tags=["🖼️ Media & Resources"])
async def get_resource(
    resource_id: str,
    db: Session = Depends(get_qbank_db)
):
    """获取资源文件"""
    from app.models.question_models_v2 import QuestionResourceV2
    
    resource = db.query(QuestionResourceV2).filter(
        QuestionResourceV2.id == resource_id
    ).first()
    
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")
    
    file_path = f"storage/{resource.resource_path}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        file_path,
        media_type=resource.mime_type,
        filename=resource.file_name
    )


# ==================== 导入导出 ====================

@router.post("/banks/{bank_id}/export", tags=["📤 Export Operations"])
async def export_question_bank(
    bank_id: str,
    format: str = Query("zip", regex="^(json|zip|csv)$"),
    include_images: bool = Query(True),
    include_answers: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """导出题库"""
    service = QuestionBankService(db)
    bank = service.get_question_bank(bank_id)
    
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")
    
    # 权限检查
    if not bank.is_public and bank.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权导出该题库")
    
    if not bank.allow_download and bank.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="该题库不允许下载")
    
    export_path = service.export_question_bank(
        bank_id=bank_id,
        include_images=include_images,
        format=format
    )
    
    if not os.path.exists(export_path):
        raise HTTPException(status_code=500, detail="导出失败")
    
    filename = os.path.basename(export_path)
    
    return FileResponse(
        export_path,
        media_type="application/octet-stream",
        filename=filename
    )


@router.post("/import", tags=["📥 Import Operations"])
async def import_question_bank(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """导入题库"""
    # 检查文件类型
    if not (file.filename.endswith('.json') or file.filename.endswith('.zip')):
        raise HTTPException(status_code=400, detail="只支持JSON或ZIP格式")
    
    # 保存上传文件
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        service = QuestionBankService(db)
        new_bank = service.import_question_bank(tmp_path, current_user.id)
        
        return {
            "message": "导入成功",
            "bank_id": new_bank.id,
            "bank_name": new_bank.name,
            "question_count": new_bank.total_questions
        }
    finally:
        # 清理临时文件
        os.unlink(tmp_path)


@router.post("/banks/{bank_id}/duplicate", tags=["📚 Bank Management"])
async def duplicate_question_bank(
    bank_id: str,
    new_name: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """复制题库"""
    service = QuestionBankService(db)
    source_bank = service.get_question_bank(bank_id)
    
    if not source_bank:
        raise HTTPException(status_code=404, detail="源题库不存在")
    
    # 权限检查
    if not source_bank.is_public and not source_bank.allow_fork:
        if source_bank.creator_id != current_user.id:
            raise HTTPException(status_code=403, detail="该题库不允许复制")
    
    # 导出源题库
    export_path = service.export_question_bank(bank_id, format="zip")
    
    # 导入为新题库
    new_bank = service.import_question_bank(export_path, current_user.id)
    
    # 更新名称
    service.update_question_bank(new_bank.id, name=new_name)
    
    return {
        "message": "复制成功",
        "bank_id": new_bank.id,
        "bank_name": new_name
    }


# ==================== 统计信息 ====================

@router.get("/banks/{bank_id}/stats", tags=["📊 Statistics"])
async def get_bank_statistics(
    bank_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """获取题库统计信息"""
    service = QuestionBankService(db)
    bank = service.get_question_bank(bank_id)
    
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")
    
    # 统计各类型题目数量
    type_stats = {}
    for q_type in QuestionType:
        count = db.query(QuestionV2).filter(
            QuestionV2.bank_id == bank_id,
            QuestionV2.type == q_type
        ).count()
        type_stats[q_type.value] = count
    
    # 统计难度分布
    difficulty_stats = {}
    for diff in ["easy", "medium", "hard", "expert"]:
        count = db.query(QuestionV2).filter(
            QuestionV2.bank_id == bank_id,
            QuestionV2.difficulty == diff
        ).count()
        difficulty_stats[diff] = count
    
    return {
        "bank_id": bank_id,
        "bank_name": bank.name,
        "total_questions": bank.total_questions,
        "total_size_mb": bank.total_size_mb,
        "has_images": bank.has_images,
        "has_audio": bank.has_audio,
        "has_video": bank.has_video,
        "type_distribution": type_stats,
        "difficulty_distribution": difficulty_stats,
        "created_at": bank.created_at,
        "updated_at": bank.updated_at
    }


@router.get("/categories", tags=["📊 Statistics"])
async def get_categories(
    db: Session = Depends(get_qbank_db)
):
    """获取所有题库分类"""
    categories = db.query(QuestionBankV2.category).distinct().all()
    return [cat[0] for cat in categories if cat[0]]


@router.get("/search", tags=["🔍 Search"])
async def search_questions(
    q: str = Query(..., min_length=2),
    bank_id: Optional[str] = None,
    type: Optional[QuestionType] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=10000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """搜索题目"""
    query = db.query(QuestionV2)
    
    # 搜索条件
    query = query.filter(
        QuestionV2.stem.contains(q) | 
        QuestionV2.explanation.contains(q)
    )
    
    if bank_id:
        query = query.filter(QuestionV2.bank_id == bank_id)
    if type:
        query = query.filter(QuestionV2.type == type)
    
    # 权限过滤
    query = query.join(QuestionBankV2).filter(
        (QuestionBankV2.is_public == True) | 
        (QuestionBankV2.creator_id == current_user.id)
    )
    
    total = query.count()
    questions = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "questions": questions
    }


# ==================== Dashboard统计 ====================

@router.get("/stats/users", tags=["📊 Statistics"])
async def get_users_stats(
    db: Session = Depends(get_qbank_db)
):
    """获取用户统计信息"""
    from app.core.database import get_main_db
    from app.models.user_models import User
    main_db = next(get_main_db())
    try:
        total = main_db.query(User).count()
        return {"total": total}
    finally:
        main_db.close()


@router.get("/stats/banks", tags=["📊 Statistics"]) 
async def get_banks_stats(
    db: Session = Depends(get_qbank_db)
):
    """获取题库统计信息"""
    total = db.query(QuestionBankV2).count()
    return {"total": total}


@router.get("/stats/questions", tags=["📊 Statistics"])
async def get_questions_stats(
    db: Session = Depends(get_qbank_db)
):
    """获取题目统计信息"""
    total = db.query(QuestionV2).count()
    return {"total": total}