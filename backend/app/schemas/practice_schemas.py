"""
Practice Session and Answer Record Schemas
答题会话与记录相关的Pydantic模型
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class PracticeModeEnum(str, Enum):
    """答题模式"""
    sequential = "sequential"  # 顺序答题
    random = "random"          # 随机答题
    wrong_only = "wrong_only"  # 只做错题
    favorite_only = "favorite_only"  # 只做收藏
    unpracticed = "unpracticed"  # 只做未练习的题目


class SessionStatusEnum(str, Enum):
    """会话状态"""
    in_progress = "in_progress"  # 进行中
    paused = "paused"             # 已暂停
    completed = "completed"       # 已完成
    abandoned = "abandoned"       # 已放弃


# ==================== Practice Session Schemas ====================

class PracticeSessionCreate(BaseModel):
    """创建答题会话"""
    bank_id: str = Field(..., description="题库ID")
    mode: PracticeModeEnum = Field(default=PracticeModeEnum.sequential, description="答题模式")
    question_types: Optional[List[str]] = Field(None, description="题型筛选 ['single', 'multiple', 'judge', 'fill', 'essay']")
    difficulty: Optional[str] = Field(None, description="难度筛选 easy/medium/hard/expert")


class PracticeSessionUpdate(BaseModel):
    """更新答题会话进度"""
    current_index: Optional[int] = Field(None, description="当前题目索引")
    status: Optional[SessionStatusEnum] = Field(None, description="会话状态")


class PracticeSessionResponse(BaseModel):
    """答题会话响应"""
    id: str
    user_id: int
    bank_id: str
    mode: str
    question_types: Optional[List[str]]
    difficulty: Optional[str]
    total_questions: int
    current_index: int
    completed_count: int
    correct_count: int
    status: str
    started_at: datetime
    last_activity_at: datetime
    completed_at: Optional[datetime]
    question_ids: List[str]
    meta_data: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class PracticeSessionListResponse(BaseModel):
    """答题会话列表响应"""
    sessions: List[PracticeSessionResponse]
    total: int


# ==================== Answer Record Schemas ====================

class AnswerSubmit(BaseModel):
    """提交答案"""
    question_id: str = Field(..., description="题目ID")
    user_answer: Dict[str, Any] = Field(..., description="用户答案（格式根据题型不同）")
    time_spent: Optional[int] = Field(None, description="答题用时（秒）")


class AnswerResult(BaseModel):
    """答题结果"""
    record_id: str
    question_id: str
    is_correct: bool
    correct_answer: Dict[str, Any]
    user_answer: Dict[str, Any]
    explanation: Optional[str] = None
    time_spent: Optional[int]
    created_at: datetime
    # 新增：显示选项内容（用于前端显示完整答案）
    options: Optional[List[Dict[str, Any]]] = None
    # 新增：题目信息
    question_type: Optional[str] = None
    question_stem: Optional[str] = None

    class Config:
        from_attributes = True


class UserAnswerRecordResponse(BaseModel):
    """用户答题记录响应"""
    id: str
    user_id: int
    question_id: str
    session_id: Optional[str]
    bank_id: str
    user_answer: Dict[str, Any]
    is_correct: bool
    time_spent: Optional[int]
    question_snapshot: Optional[Dict[str, Any]]
    correct_answer: Optional[Dict[str, Any]]
    attempt_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnswerHistoryResponse(BaseModel):
    """答题历史响应"""
    records: List[UserAnswerRecordResponse]
    total: int
    correct_count: int
    accuracy_rate: float


# ==================== Question in Practice Schemas ====================

class PracticeQuestionResponse(BaseModel):
    """答题时返回的题目信息（不包含答案）"""
    id: str
    bank_id: str
    type: str
    stem: str
    options: Optional[List[Dict[str, Any]]]
    difficulty: Optional[str]
    tags: Optional[List[str]]
    has_image: bool
    has_video: bool
    has_audio: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PracticeQuestionWithProgress(PracticeQuestionResponse):
    """带进度信息的题目"""
    current_index: int  # 当前是第几题（从1开始）
    total_questions: int  # 总共多少题
    is_favorite: bool  # 是否已收藏
    is_wrong_before: bool  # 是否曾经做错
    previous_answer: Optional[Dict[str, Any]]  # 之前的答案（如果有）


# ==================== Session Statistics Schemas ====================

class SessionStatistics(BaseModel):
    """会话统计信息"""
    session_id: str
    total_questions: int
    completed_count: int
    correct_count: int
    wrong_count: int
    accuracy_rate: float
    total_time_spent: int  # 秒
    avg_time_per_question: float  # 秒
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
