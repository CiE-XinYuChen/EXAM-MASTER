"""
LLM Interface and Prompt Template Models
"""
from sqlalchemy import Column, String, Integer, Text, JSON, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import BaseQBank


class LLMInterface(BaseQBank):
    """LLM接口配置模型"""
    __tablename__ = "llm_interfaces"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # openai-compatible, anthropic, azure, custom-http
    config = Column(JSON, nullable=False)  # 存储API配置：base_url, api_key, headers等
    request_format = Column(JSON)  # 请求格式模板
    response_parser = Column(String(50), default="standard")  # 响应解析器类型
    prompt_template_id = Column(String(50), ForeignKey("prompt_templates.id"))
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)  # 是否为默认接口
    usage_count = Column(Integer, default=0)  # 使用次数统计
    last_used_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    prompt_template = relationship("PromptTemplate", back_populates="interfaces")
    parse_logs = relationship("LLMParseLog", back_populates="interface", cascade="all, delete-orphan")


class PromptTemplate(BaseQBank):
    """提示词模板模型"""
    __tablename__ = "prompt_templates"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer)  # NULL表示系统预设模板
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # question_parser, batch_parser, formatter等
    category = Column(String(50))  # 模板分类
    content = Column(Text, nullable=False)  # 模板内容
    variables = Column(JSON)  # 模板变量列表
    description = Column(Text)  # 模板说明
    example_input = Column(Text)  # 示例输入
    example_output = Column(Text)  # 示例输出
    is_public = Column(Boolean, default=False)  # 是否公开
    is_system = Column(Boolean, default=False)  # 是否为系统预设
    usage_count = Column(Integer, default=0)
    rating = Column(Integer, default=0)  # 用户评分
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    interfaces = relationship("LLMInterface", back_populates="prompt_template")


class LLMParseLog(BaseQBank):
    """LLM解析日志"""
    __tablename__ = "llm_parse_logs"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    interface_id = Column(String(50), ForeignKey("llm_interfaces.id"))
    user_id = Column(Integer, nullable=False)
    input_text = Column(Text)  # 输入文本
    parsed_result = Column(JSON)  # 解析结果
    token_used = Column(Integer)  # 使用的token数
    cost = Column(String(20))  # 费用（如果适用）
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    response_time = Column(Integer)  # 响应时间（毫秒）
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    interface = relationship("LLMInterface", back_populates="parse_logs")