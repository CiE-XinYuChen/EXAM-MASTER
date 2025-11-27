"""
Claude Service Implementation
Anthropic Claude API集成
"""

from typing import List, Dict, Any, Optional, AsyncIterator
import aiohttp
import json
from app.services.ai.base import (
    BaseAIService, AIModelConfig, AIResponse, Message, MessageRole
)


class ClaudeService(BaseAIService):
    """
    Claude服务实现

    支持模型:
    - claude-3-opus
    - claude-3-sonnet
    - claude-3-haiku
    """

    def __init__(self, config: AIModelConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://api.anthropic.com/v1"
        self.api_key = config.api_key

    async def chat(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False
    ) -> AIResponse:
        """发送聊天请求到Claude API"""

        # 提取system消息
        system_message = None
        conversation_messages = []

        for msg in messages:
            if msg.role == MessageRole.system:
                system_message = msg.content
            else:
                conversation_messages.append(msg)

        # 构建请求消息
        claude_messages = self._format_messages(conversation_messages)

        # 构建请求体
        max_tokens = self.config.max_tokens if self.config.max_tokens is not None else 4096
        
        request_body = {
            "model": self.config.model_name,
            "messages": claude_messages,
            "max_tokens": max_tokens,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p
        }

        # 添加system消息（如果有）
        if system_message:
            request_body["system"] = system_message

        # 添加工具（如果有）
        if tools:
            request_body["tools"] = tools

        # 发送请求
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=request_body
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Claude API错误: {response.status} - {error_text}")

                result = await response.json()

        # 解析响应
        content_blocks = result.get("content", [])

        # 提取文本内容和工具调用
        text_content = ""
        tool_calls = []

        for block in content_blocks:
            if block["type"] == "text":
                text_content += block["text"]
            elif block["type"] == "tool_use":
                tool_calls.append({
                    "id": block["id"],
                    "type": "function",
                    "function": {
                        "name": block["name"],
                        "arguments": block["input"]
                    }
                })

        # 构建响应
        return AIResponse(
            content=text_content,
            finish_reason=result.get("stop_reason", "stop"),
            tool_calls=tool_calls if tool_calls else None,
            usage={
                "prompt_tokens": result.get("usage", {}).get("input_tokens", 0),
                "completion_tokens": result.get("usage", {}).get("output_tokens", 0),
                "total_tokens": (
                    result.get("usage", {}).get("input_tokens", 0) +
                    result.get("usage", {}).get("output_tokens", 0)
                )
            }
        )

    async def chat_stream(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncIterator[str]:
        """流式聊天"""

        # 提取system消息
        system_message = None
        conversation_messages = []

        for msg in messages:
            if msg.role == MessageRole.system:
                system_message = msg.content
            else:
                conversation_messages.append(msg)

        # 构建请求消息
        claude_messages = self._format_messages(conversation_messages)

        # 构建请求体
        max_tokens = self.config.max_tokens if self.config.max_tokens is not None else 4096
        
        request_body = {
            "model": self.config.model_name,
            "messages": claude_messages,
            "max_tokens": max_tokens,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "stream": True
        }

        # 添加system消息（如果有）
        if system_message:
            request_body["system"] = system_message

        # 添加工具（如果有）
        if tools:
            request_body["tools"] = tools

        # 发送请求
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=request_body
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Claude API错误: {response.status} - {error_text}")

                # 流式读取响应
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if not line or not line.startswith("data: "):
                        continue

                    # 移除 "data: " 前缀
                    data = line[6:]

                    try:
                        chunk = json.loads(data)

                        # 处理不同类型的事件
                        if chunk["type"] == "content_block_delta":
                            delta = chunk.get("delta", {})
                            if delta.get("type") == "text_delta":
                                yield delta.get("text", "")

                    except json.JSONDecodeError:
                        continue

    def _format_messages(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """格式化消息为Claude格式"""
        claude_messages = []

        for msg in messages:
            # Claude不支持system角色在messages中
            if msg.role == MessageRole.system:
                continue

            message_dict = {
                "role": msg.role.value if msg.role != MessageRole.tool else "user",
                "content": []
            }

            # 添加文本内容
            if msg.content:
                message_dict["content"].append({
                    "type": "text",
                    "text": msg.content
                })

            # 添加工具调用结果
            if msg.tool_call_id:
                message_dict["content"] = [{
                    "type": "tool_result",
                    "tool_use_id": msg.tool_call_id,
                    "content": msg.content
                }]

            # 如果消息有工具调用
            if msg.tool_calls:
                for call in msg.tool_calls:
                    message_dict["content"].append({
                        "type": "tool_use",
                        "id": call["id"],
                        "name": call["function"]["name"],
                        "input": call["function"]["arguments"]
                    })

            # 如果content是字符串，转换为列表格式
            if isinstance(message_dict["content"], str):
                message_dict["content"] = [{
                    "type": "text",
                    "text": message_dict["content"]
                }]

            claude_messages.append(message_dict)

        return claude_messages

    def format_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        将OpenAI格式的工具转换为Claude格式

        OpenAI格式:
        {
            "type": "function",
            "function": {
                "name": "...",
                "description": "...",
                "parameters": {...}
            }
        }

        Claude格式:
        {
            "name": "...",
            "description": "...",
            "input_schema": {...}
        }
        """
        claude_tools = []

        for tool in tools:
            if tool.get("type") == "function":
                func = tool["function"]
                claude_tool = {
                    "name": func["name"],
                    "description": func["description"],
                    "input_schema": func["parameters"]
                }
                claude_tools.append(claude_tool)

        return claude_tools
