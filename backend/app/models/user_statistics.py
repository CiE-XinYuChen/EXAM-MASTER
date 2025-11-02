"""
User Statistics Models
用户统计模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base, BaseQBank


class UserDailyStatistics(Base):
    """用户每日统计表"""
    __tablename__ = "user_daily_statistics"

    # 基本信息
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # 引用主库users.id（无外键约束）
    date = Column(DateTime, nullable=False, index=True)  # 统计日期（只到天）

    # 答题统计
    questions_answered = Column(Integer, default=0)  # 答题数量
    questions_correct = Column(Integer, default=0)   # 正确数量
    accuracy_rate = Column(Float, default=0.0)       # 正确率

    # 时间统计
    total_time_spent = Column(Integer, default=0)  # 总用时（秒）
    avg_time_per_question = Column(Float, default=0.0)  # 平均每题用时

    # 会话统计
    sessions_count = Column(Integer, default=0)  # 会话数量
    sessions_completed = Column(Integer, default=0)  # 完成的会话数

    # 题库分布
    banks_practiced = Column(JSON)  # {bank_id: count}

    # 更新时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserBankStatistics(BaseQBank):
    """用户分题库统计表"""
    __tablename__ = "user_bank_statistics"

    # 基本信息
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # 引用主库users.id（无外键约束）
    bank_id = Column(String(36), ForeignKey("question_banks_v2.id"), nullable=False, index=True)

    # 答题统计
    total_questions = Column(Integer, default=0)      # 题库总题数
    practiced_questions = Column(Integer, default=0)  # 已练习题数
    correct_count = Column(Integer, default=0)        # 正确数量
    wrong_count = Column(Integer, default=0)          # 错误数量
    accuracy_rate = Column(Float, default=0.0)        # 正确率

    # 收藏与错题
    favorite_count = Column(Integer, default=0)  # 收藏数量
    wrong_questions_count = Column(Integer, default=0)  # 错题数量

    # 时间统计
    total_time_spent = Column(Integer, default=0)  # 总用时（秒）

    # 分题型统计
    type_statistics = Column(JSON)  # {type: {total, correct, wrong}}

    # 时间
    first_practiced_at = Column(DateTime)
    last_practiced_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系（user关系因跨数据库无法建立）
    bank = relationship("QuestionBankV2", backref="user_stats")
