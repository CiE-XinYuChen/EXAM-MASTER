"""
AI Configuration and Chat Session Models
AI配置和对话会话数据库模型
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class AIConfig(Base):
    """AI配置表"""
    __tablename__ = "ai_configs"

    # 基本信息
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 配置信息
    name = Column(String(100), nullable=False)
    provider = Column(String(20), nullable=False)  # openai, claude, zhipu, custom
    model_name = Column(String(50), nullable=False)
    api_key = Column(Text, nullable=False)  # 加密存储
    base_url = Column(String(200))  # 自定义API地址

    # 模型参数
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=2000)
    top_p = Column(Float, default=1.0)

    # Agent配置
    enable_agent = Column(Boolean, default=True)  # 启用Agent工具调用
    max_tool_iterations = Column(Integer, default=5)  # 最大工具调用次数

    # 状态
    is_default = Column(Boolean, default=False, index=True)
    description = Column(String(500))

    # 时间
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", backref="ai_configs")
    chat_sessions = relationship("ChatSession", back_populates="ai_config", cascade="all, delete-orphan")


class ChatSession(Base):
    """AI对话会话表"""
    __tablename__ = "chat_sessions"

    # 基本信息
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    ai_config_id = Column(String(36), ForeignKey("ai_configs.id"), nullable=False, index=True)

    # 会话配置
    bank_id = Column(String(36))  # 题库ID（跨库引用，无外键）
    mode = Column(String(20), nullable=False)  # practice, review, question
    system_prompt = Column(Text)  # 自定义系统提示词

    # 统计
    total_messages = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)

    # 时间
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    # 关系
    user = relationship("User", backref="chat_sessions")
    ai_config = relationship("AIConfig", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """对话消息表"""
    __tablename__ = "chat_messages"

    # 基本信息
    id = Column(String(36), primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey("chat_sessions.id"), nullable=False, index=True)

    # 消息内容
    role = Column(String(20), nullable=False)  # system, user, assistant, tool
    content = Column(Text, nullable=False)

    # 工具调用
    tool_calls = Column(JSON)  # 工具调用列表
    tool_call_id = Column(String(100))  # 工具调用ID（tool消息使用）

    # 统计
    tokens = Column(Integer)  # 该消息消耗的token数

    # 时间
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # 关系
    session = relationship("ChatSession", back_populates="messages")
