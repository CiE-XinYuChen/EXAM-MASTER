"""
User Practice and Answer Record Models
用户答题与记录模型
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, JSON, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base, BaseQBank


class PracticeMode(str, enum.Enum):
    """答题模式"""
    sequential = "sequential"  # 顺序答题
    random = "random"          # 随机答题
    wrong_only = "wrong_only"  # 只做错题
    favorite_only = "favorite_only"  # 只做收藏
    unpracticed = "unpracticed"  # 未练习的题目


class SessionStatus(str, enum.Enum):
    """会话状态"""
    in_progress = "in_progress"  # 进行中
    paused = "paused"             # 已暂停
    completed = "completed"       # 已完成
    abandoned = "abandoned"       # 已放弃


class PracticeSession(BaseQBank):
    """答题会话表 - 记录用户的答题进程"""
    __tablename__ = "practice_sessions"

    # 基本信息
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # 引用主库的users.id（无外键约束）
    bank_id = Column(String(36), ForeignKey("question_banks_v2.id"), nullable=False, index=True)

    # 会话配置
    mode = Column(SQLEnum(PracticeMode), default=PracticeMode.sequential, nullable=False)
    question_types = Column(JSON)  # 题型筛选 ["single", "multiple"]
    difficulty = Column(String(20))  # 难度筛选 easy/medium/hard

    # 进度信息
    total_questions = Column(Integer, default=0)
    current_index = Column(Integer, default=0)  # 当前题目索引
    completed_count = Column(Integer, default=0)  # 已完成题目数
    correct_count = Column(Integer, default=0)    # 正确题目数

    # 状态
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.in_progress)

    # 时间记录
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)

    # 会话数据（题目ID列表等）
    question_ids = Column(JSON)  # 本次会话的题目ID列表
    meta_data = Column(JSON)     # 其他元数据

    # 关系
    answer_records = relationship("UserAnswerRecord", back_populates="session", cascade="all, delete-orphan")


class UserAnswerRecord(BaseQBank):
    """用户答题记录表"""
    __tablename__ = "user_answer_records"

    # 基本信息
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # 引用主库的users.id（无外键约束）
    question_id = Column(String(36), ForeignKey("questions_v2.id"), nullable=False, index=True)
    session_id = Column(String(36), ForeignKey("practice_sessions.id"), nullable=True, index=True)
    bank_id = Column(String(36), ForeignKey("question_banks_v2.id"), nullable=False, index=True)

    # 答题数据
    user_answer = Column(JSON, nullable=False)  # 用户答案（格式根据题型不同）
    is_correct = Column(Boolean, default=False)
    time_spent = Column(Integer)  # 答题用时（秒）

    # 题目快照（防止题目被修改后无法回溯）
    question_snapshot = Column(JSON)  # 题目内容快照
    correct_answer = Column(JSON)     # 正确答案快照

    # 统计
    attempt_count = Column(Integer, default=1)  # 尝试次数

    # 时间
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    session = relationship("PracticeSession", back_populates="answer_records")
    question = relationship("QuestionV2", backref="user_answers_records")


class UserFavorite(BaseQBank):
    """用户收藏题目表"""
    __tablename__ = "user_favorites"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # 引用主库的users.id（无外键约束）
    question_id = Column(String(36), ForeignKey("questions_v2.id"), nullable=False, index=True)
    bank_id = Column(String(36), ForeignKey("question_banks_v2.id"), nullable=False, index=True)

    # 收藏备注
    note = Column(Text)

    # 时间
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # 关系
    question = relationship("QuestionV2", backref="favorited_by")

    # 联合唯一索引（一个用户不能重复收藏同一题目）
    __table_args__ = (
        {'extend_existing': True},
    )


class UserWrongQuestion(BaseQBank):
    """用户错题本表"""
    __tablename__ = "user_wrong_questions"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # 引用主库的users.id（无外键约束）
    question_id = Column(String(36), ForeignKey("questions_v2.id"), nullable=False, index=True)
    bank_id = Column(String(36), ForeignKey("question_banks_v2.id"), nullable=False, index=True)

    # 错误统计
    error_count = Column(Integer, default=1)      # 错误次数
    last_error_answer = Column(JSON)              # 最后一次错误答案
    corrected = Column(Boolean, default=False)    # 是否已订正

    # 时间
    first_error_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_error_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    corrected_at = Column(DateTime)

    # 关系
    question = relationship("QuestionV2", backref="wrong_by_users")
