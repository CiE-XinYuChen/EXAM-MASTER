"""
Wrong Questions Schemas
错题本相关的Pydantic模型
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ==================== Wrong Question Schemas ====================

class WrongQuestionResponse(BaseModel):
    """错题响应"""
    id: str
    user_id: int
    question_id: str
    bank_id: str
    error_count: int
    last_error_answer: Optional[Dict[str, Any]]
    corrected: bool
    first_error_at: datetime
    last_error_at: datetime
    corrected_at: Optional[datetime]

    class Config:
        from_attributes = True


class WrongQuestionWithDetailsResponse(WrongQuestionResponse):
    """带题目详情的错题响应"""
    question_number: Optional[int]
    question_type: str
    question_stem: str
    question_difficulty: Optional[str]
    question_tags: Optional[List[str]]
    has_image: bool
    has_video: bool
    has_audio: bool
    correct_answer: Optional[Dict[str, Any]]  # 正确答案


class WrongQuestionListResponse(BaseModel):
    """错题列表响应"""
    wrong_questions: List[WrongQuestionWithDetailsResponse]
    total: int
    uncorrected_count: int  # 未订正的数量


# ==================== Wrong Question Query Schemas ====================

class WrongQuestionQuery(BaseModel):
    """错题查询参数"""
    bank_id: Optional[str] = Field(None, description="题库ID筛选")
    question_type: Optional[str] = Field(None, description="题型筛选")
    difficulty: Optional[str] = Field(None, description="难度筛选")
    corrected: Optional[bool] = Field(None, description="是否已订正")
    min_error_count: Optional[int] = Field(None, ge=1, description="最小错误次数")
    search: Optional[str] = Field(None, description="关键词搜索（题干）")
    skip: int = Field(0, ge=0, description="跳过数量")
    limit: int = Field(20, ge=1, le=100, description="返回数量")


class WrongQuestionCorrectRequest(BaseModel):
    """标记错题已订正"""
    corrected: bool = Field(True, description="是否已订正")


class WrongQuestionStatistics(BaseModel):
    """错题统计"""
    total_wrong_questions: int
    uncorrected_count: int
    corrected_count: int
    most_wrong_type: Optional[str]  # 错误最多的题型
    most_wrong_difficulty: Optional[str]  # 错误最多的难度
    error_distribution: Dict[str, int]  # 错误次数分布 {error_count: question_count}
    type_distribution: Dict[str, int]  # 题型分布 {type: count}
    difficulty_distribution: Dict[str, int]  # 难度分布 {difficulty: count}


class WrongQuestionAnalysis(BaseModel):
    """错题分析"""
    question_id: str
    question_stem: str
    question_type: str
    error_count: int
    common_mistakes: List[Dict[str, Any]]  # 常见错误答案
    correct_answer: Dict[str, Any]
    explanation: Optional[str]  # 题目解析
    related_knowledge: Optional[List[str]]  # 相关知识点
