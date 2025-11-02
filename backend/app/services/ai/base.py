"""
Base AI Service
AI服务基类，定义统一接口
"""

from typing import List, Dict, Any, Optional, AsyncIterator
from abc import ABC, abstractmethod
from pydantic import BaseModel
from enum import Enum


class MessageRole(str, Enum):
    """消息角色"""
    system = "system"
    user = "user"
    assistant = "assistant"
    tool = "tool"


class Message(BaseModel):
    """对话消息"""
    role: MessageRole
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


class AIModelConfig(BaseModel):
    """AI模型配置"""
    model_name: str
    api_key: str
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0


class AIResponse(BaseModel):
    """AI响应"""
    content: str
    finish_reason: str  # "stop", "length", "tool_calls"
    tool_calls: Optional[List[Dict[str, Any]]] = None
    usage: Optional[Dict[str, Any]] = None  # 改为Any以支持嵌套字典


class BaseAIService(ABC):
    """
    AI服务基类

    所有AI服务提供商都需要实现此接口
    """

    def __init__(self, config: AIModelConfig):
        self.config = config

    @abstractmethod
    async def chat(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False
    ) -> AIResponse:
        """
        发送聊天请求

        Args:
            messages: 对话历史
            tools: 可用工具列表
            stream: 是否流式输出

        Returns:
            AI响应
        """
        pass

    @abstractmethod
    async def chat_stream(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncIterator[str]:
        """
        流式聊天

        Args:
            messages: 对话历史
            tools: 可用工具列表

        Yields:
            响应文本片段
        """
        pass

    def format_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        格式化工具定义为当前模型支持的格式

        子类可以重写此方法以适配不同的工具格式
        """
        return tools

    def parse_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析工具调用

        子类可以重写此方法以适配不同的工具调用格式
        """
        return tool_call
