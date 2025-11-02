"""
AI Configuration and Chat Schemas
AI配置和对话相关的Pydantic模型
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class AIProvider(str, Enum):
    """AI提供商"""
    openai = "openai"
    claude = "claude"
    zhipu = "zhipu"
    custom = "custom"


# 常用模型名称（仅供参考，不做强制限制）
COMMON_MODELS = {
    "openai": [
        "gpt-4",
        "gpt-4-turbo",
        "gpt-4-turbo-preview",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k"
    ],
    "claude": [
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
        "claude-2.1",
        "claude-2.0"
    ],
    "zhipu": [
        "glm-4",
        "glm-4v",
        "glm-3-turbo"
    ]
}


# ==================== AI Configuration Schemas ====================

class AIConfigCreate(BaseModel):
    """创建AI配置"""
    name: str = Field(..., min_length=1, max_length=100, description="配置名称")
    provider: AIProvider = Field(..., description="AI提供商")
    model_name: str = Field(..., min_length=1, max_length=100, description="模型名称（支持自定义）")
    api_key: str = Field(..., min_length=1, description="API密钥")
    base_url: Optional[str] = Field(None, description="自定义API地址（可选）")
    temperature: float = Field(0.7, ge=0, le=2, description="温度参数")
    max_tokens: int = Field(2000, ge=1, le=200000, description="最大token数")
    top_p: float = Field(1.0, ge=0, le=1, description="top_p参数")
    is_default: bool = Field(False, description="是否为默认配置")
    description: Optional[str] = Field(None, max_length=500, description="配置描述")


class AIConfigUpdate(BaseModel):
    """更新AI配置"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0, le=2)
    max_tokens: Optional[int] = Field(None, ge=1, le=200000)
    top_p: Optional[float] = Field(None, ge=0, le=1)
    is_default: Optional[bool] = None
    description: Optional[str] = Field(None, max_length=500)


class AIConfigResponse(BaseModel):
    """AI配置响应"""
    id: str
    user_id: int
    name: str
    provider: str
    model_name: str
    base_url: Optional[str]
    temperature: float
    max_tokens: int
    top_p: float
    is_default: bool
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    # API密钥不返回，安全考虑
    class Config:
        from_attributes = True


class AIConfigListResponse(BaseModel):
    """AI配置列表响应"""
    configs: List[AIConfigResponse]
    total: int


# ==================== AI Chat Session Schemas ====================

class ChatMode(str, Enum):
    """对话模式"""
    practice = "practice"  # 答题模式
    review = "review"  # 复习模式
    question = "question"  # 问答模式


class ChatSessionCreate(BaseModel):
    """创建对话会话"""
    ai_config_id: str = Field(..., description="AI配置ID")
    bank_id: Optional[str] = Field(None, description="题库ID（答题模式必填）")
    mode: ChatMode = Field(ChatMode.practice, description="对话模式")
    system_prompt: Optional[str] = Field(None, description="自定义系统提示词")


class ChatSessionResponse(BaseModel):
    """对话会话响应"""
    id: str
    user_id: int
    ai_config_id: str
    bank_id: Optional[str]
    mode: str
    system_prompt: Optional[str]
    total_messages: int
    total_tokens: int
    started_at: datetime
    last_activity_at: datetime

    class Config:
        from_attributes = True


class ChatSessionListResponse(BaseModel):
    """对话会话列表响应"""
    sessions: List[ChatSessionResponse]
    total: int


# ==================== Chat Message Schemas ====================

class ChatMessageRole(str, Enum):
    """消息角色"""
    system = "system"
    user = "user"
    assistant = "assistant"
    tool = "tool"


class ChatMessageCreate(BaseModel):
    """创建聊天消息"""
    content: str = Field(..., min_length=1, description="消息内容")


class ChatMessageResponse(BaseModel):
    """聊天消息响应"""
    id: str
    session_id: str
    role: str
    content: str
    tool_calls: Optional[List[Dict[str, Any]]]
    tool_call_id: Optional[str]
    tokens: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    """对话响应"""
    message_id: str
    content: str
    tool_calls: Optional[List[Dict[str, Any]]]
    finish_reason: str
    tokens: int


class ChatStreamRequest(BaseModel):
    """流式对话请求"""
    session_id: str
    message: str


# ==================== AI Usage Statistics Schemas ====================

class AIUsageStatistics(BaseModel):
    """AI使用统计"""
    total_sessions: int
    total_messages: int
    total_tokens: int
    by_provider: Dict[str, Dict[str, int]]  # {provider: {sessions, messages, tokens}}
    by_model: Dict[str, Dict[str, int]]  # {model: {sessions, messages, tokens}}


class AIUsageByDate(BaseModel):
    """按日期统计AI使用"""
    date: str
    sessions: int
    messages: int
    tokens: int


class AIUsageReport(BaseModel):
    """AI使用报告"""
    overview: AIUsageStatistics
    daily_usage: List[AIUsageByDate]
    top_models: List[Dict[str, Any]]


# ==================== Tool Call Schemas ====================

class ToolCallRequest(BaseModel):
    """工具调用请求（内部使用）"""
    tool_name: str
    arguments: Dict[str, Any]


class ToolCallResponse(BaseModel):
    """工具调用响应（内部使用）"""
    tool_call_id: str
    result: Dict[str, Any]
    success: bool
    error: Optional[str] = None
