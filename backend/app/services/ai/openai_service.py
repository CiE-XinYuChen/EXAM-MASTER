"""
OpenAI Service Implementation
OpenAI API集成，支持GPT-4、GPT-3.5等模型
"""

from typing import List, Dict, Any, Optional, AsyncIterator
import aiohttp
import json
from app.services.ai.base import (
    BaseAIService, AIModelConfig, AIResponse, Message, MessageRole
)


class OpenAIService(BaseAIService):
    """
    OpenAI服务实现

    支持模型:
    - gpt-4
    - gpt-4-turbo
    - gpt-3.5-turbo
    """

    def __init__(self, config: AIModelConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://api.openai.com/v1"
        self.api_key = config.api_key

    async def chat(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False
    ) -> AIResponse:
        """发送聊天请求到OpenAI API"""

        # 构建请求消息
        openai_messages = self._format_messages(messages)

        # 构建请求体
        request_body = {
            "model": self.config.model_name,
            "messages": openai_messages,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p
        }
        
        if self.config.max_tokens is not None:
            request_body["max_tokens"] = self.config.max_tokens

        # 添加工具（如果有）
        if tools:
            request_body["tools"] = tools
            request_body["tool_choice"] = "auto"

        # 发送请求
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=request_body
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API错误: {response.status} - {error_text}")

                result = await response.json()

        # 解析响应
        choice = result["choices"][0]
        message = choice["message"]

        # 提取内容和工具调用
        content = message.get("content", "")
        tool_calls = message.get("tool_calls")

        # 构建响应
        return AIResponse(
            content=content or "",
            finish_reason=choice["finish_reason"],
            tool_calls=self._parse_tool_calls(tool_calls) if tool_calls else None,
            usage=result.get("usage")
        )

    async def chat_stream(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncIterator[str]:
        """流式聊天"""

        # 构建请求消息
        openai_messages = self._format_messages(messages)

        # 构建请求体
        request_body = {
            "model": self.config.model_name,
            "messages": openai_messages,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "stream": True
        }
        
        if self.config.max_tokens is not None:
            request_body["max_tokens"] = self.config.max_tokens

        # 添加工具（如果有）
        if tools:
            request_body["tools"] = tools
            request_body["tool_choice"] = "auto"

        # 发送请求
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=request_body
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API错误: {response.status} - {error_text}")

                # 流式读取响应
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if not line or not line.startswith("data: "):
                        continue

                    # 移除 "data: " 前缀
                    data = line[6:]

                    # 检查是否是结束标记
                    if data == "[DONE]":
                        break

                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0]["delta"]

                        # 提取内容
                        if "content" in delta and delta["content"]:
                            yield delta["content"]

                    except json.JSONDecodeError:
                        continue

    def _format_messages(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """格式化消息为OpenAI格式"""
        openai_messages = []

        for msg in messages:
            message_dict = {
                "role": msg.role.value,
                "content": msg.content
            }

            # 添加工具调用（如果有）
            if msg.tool_calls:
                # 确保arguments是字符串格式
                formatted_tool_calls = []
                for call in msg.tool_calls:
                    formatted_call = {
                        "id": call["id"],
                        "type": call["type"],
                        "function": {
                            "name": call["function"]["name"],
                            # 如果arguments是对象，转换为JSON字符串
                            "arguments": json.dumps(call["function"]["arguments"])
                                if isinstance(call["function"]["arguments"], dict)
                                else call["function"]["arguments"]
                        }
                    }
                    formatted_tool_calls.append(formatted_call)
                message_dict["tool_calls"] = formatted_tool_calls

            # 添加工具调用ID（如果有）
            if msg.tool_call_id:
                message_dict["tool_call_id"] = msg.tool_call_id
                message_dict["role"] = "tool"

            openai_messages.append(message_dict)

        return openai_messages

    def _parse_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析OpenAI的工具调用"""
        parsed_calls = []

        for call in tool_calls:
            parsed_call = {
                "id": call["id"],
                "type": call["type"],
                "function": {
                    "name": call["function"]["name"],
                    "arguments": json.loads(call["function"]["arguments"])
                }
            }
            parsed_calls.append(parsed_call)

        return parsed_calls

    def format_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """OpenAI的工具格式已经是标准格式，直接返回"""
        return tools
