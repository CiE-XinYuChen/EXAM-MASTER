"""
User Favorites Schemas
用户收藏相关的Pydantic模型
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ==================== Favorite Schemas ====================

class FavoriteCreate(BaseModel):
    """添加收藏"""
    question_id: str = Field(..., description="题目ID")
    bank_id: str = Field(..., description="题库ID")
    note: Optional[str] = Field(None, max_length=500, description="收藏备注")


class FavoriteUpdate(BaseModel):
    """更新收藏备注"""
    note: Optional[str] = Field(None, max_length=500, description="收藏备注")


class FavoriteResponse(BaseModel):
    """收藏响应"""
    id: str
    user_id: int
    question_id: str
    bank_id: str
    note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionOption(BaseModel):
    """题目选项"""
    label: str
    content: str
    is_correct: Optional[bool] = None


class FavoriteWithQuestionResponse(FavoriteResponse):
    """带题目信息的收藏响应"""
    question_number: Optional[int]
    question_type: str
    question_stem: str
    question_difficulty: Optional[str]
    question_tags: Optional[List[str]]
    question_options: Optional[List[QuestionOption]] = None
    question_explanation: Optional[str] = None
    has_image: bool
    has_video: bool
    has_audio: bool


class FavoriteListResponse(BaseModel):
    """收藏列表响应"""
    favorites: List[FavoriteWithQuestionResponse]
    total: int


# ==================== Favorite Query Schemas ====================

class FavoriteQuery(BaseModel):
    """收藏查询参数"""
    bank_id: Optional[str] = Field(None, description="题库ID筛选")
    question_type: Optional[str] = Field(None, description="题型筛选")
    difficulty: Optional[str] = Field(None, description="难度筛选")
    tags: Optional[List[str]] = Field(None, description="标签筛选")
    search: Optional[str] = Field(None, description="关键词搜索（题干）")
    skip: int = Field(0, ge=0, description="跳过数量")
    limit: int = Field(20, ge=1, le=100, description="返回数量")


class FavoriteCheckResponse(BaseModel):
    """检查是否已收藏"""
    question_id: str
    is_favorite: bool
    favorite_id: Optional[str] = None


class BatchFavoriteCheckRequest(BaseModel):
    """批量检查收藏状态"""
    question_ids: List[str] = Field(..., max_items=100, description="题目ID列表")


class BatchFavoriteCheckResponse(BaseModel):
    """批量检查收藏状态响应"""
    favorites: Dict[str, bool]  # {question_id: is_favorite}
