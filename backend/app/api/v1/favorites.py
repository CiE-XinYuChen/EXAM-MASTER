"""
Favorites API - 收藏管理
"""

from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime
import uuid

from app.core.database import get_qbank_db
from app.core.security import get_current_user
from app.models.user_models import User
from app.models.user_practice import UserFavorite
from app.models.question_models_v2 import QuestionV2
from app.schemas.favorites_schemas import (
    FavoriteCreate,
    FavoriteUpdate,
    FavoriteResponse,
    FavoriteWithQuestionResponse,
    FavoriteListResponse,
    FavoriteQuery,
    FavoriteCheckResponse,
    BatchFavoriteCheckRequest,
    BatchFavoriteCheckResponse
)

router = APIRouter()


# ==================== Favorite Management Endpoints ====================

@router.post("", response_model=FavoriteResponse, tags=["⭐ Favorites"])
async def add_favorite(
    favorite_data: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """添加收藏"""

    # 检查题目是否存在
    question = db.query(QuestionV2).filter(
        QuestionV2.id == favorite_data.question_id
    ).first()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )

    # 检查是否已收藏
    existing = db.query(UserFavorite).filter(
        and_(
            UserFavorite.user_id == current_user.id,
            UserFavorite.question_id == favorite_data.question_id
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已经收藏过该题目"
        )

    # 创建收藏记录
    favorite = UserFavorite(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        question_id=favorite_data.question_id,
        bank_id=favorite_data.bank_id,
        note=favorite_data.note,
        created_at=datetime.utcnow()
    )

    db.add(favorite)
    db.commit()
    db.refresh(favorite)

    return favorite


@router.get("", response_model=FavoriteListResponse, tags=["⭐ Favorites"])
async def list_favorites(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=10000),
    bank_id: Optional[str] = None,
    question_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """获取收藏列表"""

    # 基础查询 - join题目表
    query = db.query(UserFavorite, QuestionV2).join(
        QuestionV2,
        UserFavorite.question_id == QuestionV2.id
    ).filter(
        UserFavorite.user_id == current_user.id
    )

    # 筛选条件
    if bank_id:
        query = query.filter(UserFavorite.bank_id == bank_id)
    if question_type:
        query = query.filter(QuestionV2.type == question_type)
    if difficulty:
        query = query.filter(QuestionV2.difficulty == difficulty)
    if search:
        query = query.filter(QuestionV2.stem.contains(search))

    # 按收藏时间倒序
    query = query.order_by(UserFavorite.created_at.desc())

    total = query.count()
    results = query.offset(skip).limit(limit).all()

    # 构造响应
    favorites_with_question = []
    for favorite, question in results:
        favorites_with_question.append(FavoriteWithQuestionResponse(
            id=favorite.id,
            user_id=favorite.user_id,
            question_id=favorite.question_id,
            bank_id=favorite.bank_id,
            note=favorite.note,
            created_at=favorite.created_at,
            question_number=question.number if hasattr(question, 'number') else None,
            question_type=question.type.value,
            question_stem=question.stem,
            question_difficulty=question.difficulty.value if hasattr(question.difficulty, 'value') else question.difficulty,
            question_tags=question.tags,
            has_image=question.has_image if hasattr(question, 'has_image') else False,
            has_video=question.has_video if hasattr(question, 'has_video') else False,
            has_audio=question.has_audio if hasattr(question, 'has_audio') else False
        ))

    return FavoriteListResponse(
        favorites=favorites_with_question,
        total=total
    )


@router.get("/{favorite_id}", response_model=FavoriteResponse, tags=["⭐ Favorites"])
async def get_favorite(
    favorite_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """获取收藏详情"""

    favorite = db.query(UserFavorite).filter(
        and_(
            UserFavorite.id == favorite_id,
            UserFavorite.user_id == current_user.id
        )
    ).first()

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="收藏不存在"
        )

    return favorite


@router.put("/{favorite_id}", response_model=FavoriteResponse, tags=["⭐ Favorites"])
async def update_favorite(
    favorite_id: str,
    favorite_update: FavoriteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """更新收藏备注"""

    favorite = db.query(UserFavorite).filter(
        and_(
            UserFavorite.id == favorite_id,
            UserFavorite.user_id == current_user.id
        )
    ).first()

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="收藏不存在"
        )

    # 更新备注
    if favorite_update.note is not None:
        favorite.note = favorite_update.note

    db.commit()
    db.refresh(favorite)

    return favorite


@router.delete("/{favorite_id}", tags=["⭐ Favorites"])
async def delete_favorite(
    favorite_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """取消收藏"""

    favorite = db.query(UserFavorite).filter(
        and_(
            UserFavorite.id == favorite_id,
            UserFavorite.user_id == current_user.id
        )
    ).first()

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="收藏不存在"
        )

    db.delete(favorite)
    db.commit()

    return {"success": True, "message": "已取消收藏"}


@router.delete("/question/{question_id}", tags=["⭐ Favorites"])
async def delete_favorite_by_question(
    question_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """通过题目ID取消收藏"""

    favorite = db.query(UserFavorite).filter(
        and_(
            UserFavorite.user_id == current_user.id,
            UserFavorite.question_id == question_id
        )
    ).first()

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未收藏该题目"
        )

    db.delete(favorite)
    db.commit()

    return {"success": True, "message": "已取消收藏"}


# ==================== Favorite Check Endpoints ====================

@router.get("/check/{question_id}", response_model=FavoriteCheckResponse, tags=["⭐ Favorites"])
async def check_favorite(
    question_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """检查题目是否已收藏"""

    favorite = db.query(UserFavorite).filter(
        and_(
            UserFavorite.user_id == current_user.id,
            UserFavorite.question_id == question_id
        )
    ).first()

    return FavoriteCheckResponse(
        question_id=question_id,
        is_favorite=favorite is not None,
        favorite_id=favorite.id if favorite else None
    )


@router.post("/check/batch", response_model=BatchFavoriteCheckResponse, tags=["⭐ Favorites"])
async def batch_check_favorites(
    request: BatchFavoriteCheckRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """批量检查收藏状态"""

    # 查询这些题目的收藏状态
    favorites = db.query(UserFavorite.question_id).filter(
        and_(
            UserFavorite.user_id == current_user.id,
            UserFavorite.question_id.in_(request.question_ids)
        )
    ).all()

    favorited_ids = set(f[0] for f in favorites)

    # 构造响应
    result = {qid: (qid in favorited_ids) for qid in request.question_ids}

    return BatchFavoriteCheckResponse(favorites=result)


# ==================== Statistics Endpoints ====================

@router.get("/stats/count", tags=["⭐ Favorites"])
async def get_favorite_count(
    bank_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """获取收藏数量"""

    query = db.query(func.count(UserFavorite.id)).filter(
        UserFavorite.user_id == current_user.id
    )

    if bank_id:
        query = query.filter(UserFavorite.bank_id == bank_id)

    count = query.scalar() or 0

    return {"total": count, "bank_id": bank_id}
