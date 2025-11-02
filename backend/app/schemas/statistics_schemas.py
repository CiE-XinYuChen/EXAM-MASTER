"""
User Statistics Schemas
用户统计相关的Pydantic模型
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field


# ==================== Daily Statistics Schemas ====================

class DailyStatisticsResponse(BaseModel):
    """每日统计响应"""
    id: str
    user_id: int
    date: datetime
    questions_answered: int
    questions_correct: int
    accuracy_rate: float
    total_time_spent: int  # 秒
    avg_time_per_question: float  # 秒
    sessions_count: int
    sessions_completed: int
    banks_practiced: Dict[str, int]  # {bank_id: count}
    updated_at: datetime

    class Config:
        from_attributes = True


class DailyStatisticsListResponse(BaseModel):
    """每日统计列表响应"""
    statistics: List[DailyStatisticsResponse]
    total_days: int
    date_range: Dict[str, str]  # {"start": "2025-01-01", "end": "2025-01-31"}


# ==================== Bank Statistics Schemas ====================

class BankStatisticsResponse(BaseModel):
    """分题库统计响应"""
    id: str
    user_id: int
    bank_id: str
    bank_name: Optional[str] = None  # 可以从关联的bank获取
    total_questions: int
    practiced_questions: int
    correct_count: int
    wrong_count: int
    accuracy_rate: float
    favorite_count: int
    wrong_questions_count: int
    total_time_spent: int  # 秒
    type_statistics: Optional[Dict[str, Dict[str, int]]]  # {type: {total, correct, wrong}}
    first_practiced_at: Optional[datetime]
    last_practiced_at: Optional[datetime]
    updated_at: datetime

    class Config:
        from_attributes = True


class BankStatisticsListResponse(BaseModel):
    """分题库统计列表响应"""
    statistics: List[BankStatisticsResponse]
    total: int


# ==================== Overview Statistics Schemas ====================

class OverviewStatistics(BaseModel):
    """总览统计"""
    total_banks_accessed: int  # 总共访问的题库数
    total_questions_practiced: int  # 总共练习的题目数
    total_correct: int  # 总共答对数
    total_wrong: int  # 总共答错数
    overall_accuracy_rate: float  # 总体正确率
    total_time_spent: int  # 总用时（秒）
    total_sessions: int  # 总会话数
    total_favorites: int  # 总收藏数
    total_wrong_questions: int  # 总错题数
    consecutive_days: int  # 连续学习天数
    total_practice_days: int  # 总练习天数
    last_practice_date: Optional[datetime]  # 最后练习日期


class DetailedStatistics(BaseModel):
    """详细统计（包含图表数据）"""
    overview: OverviewStatistics
    daily_trend: List[Dict[str, Any]]  # 每日趋势数据
    bank_distribution: List[Dict[str, Any]]  # 题库分布
    type_distribution: List[Dict[str, Any]]  # 题型分布
    difficulty_distribution: List[Dict[str, Any]]  # 难度分布
    accuracy_trend: List[Dict[str, Any]]  # 正确率趋势


# ==================== Statistics Query Schemas ====================

class StatisticsQuery(BaseModel):
    """统计查询参数"""
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    bank_id: Optional[str] = Field(None, description="题库ID（用于筛选特定题库）")


class RankingItem(BaseModel):
    """排行榜项"""
    user_id: int
    username: Optional[str]
    score: int  # 可以是答题数、正确率等
    rank: int
    avatar: Optional[str] = None


class RankingResponse(BaseModel):
    """排行榜响应"""
    rankings: List[RankingItem]
    my_rank: Optional[int] = None  # 当前用户的排名
    total_users: int
