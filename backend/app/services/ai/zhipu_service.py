"""
Zhipu AI Service Implementation
智谱AI (GLM) API集成
"""

from typing import List, Dict, Any, Optional, AsyncIterator
import aiohttp
import json
from app.services.ai.base import (
    BaseAIService, AIModelConfig, AIResponse, Message, MessageRole
)


class ZhipuService(BaseAIService):
    """
    智谱AI服务实现

    支持模型:
    - glm-4
    - glm-3-turbo
    """

    def __init__(self, config: AIModelConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://open.bigmodel.cn/api/paas/v4"
        self.api_key = config.api_key

    async def chat(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False
    ) -> AIResponse:
        """发送聊天请求到智谱AI API"""

        # 构建请求消息
        zhipu_messages = self._format_messages(messages)

        # 构建请求体
        request_body = {
            "model": self.config.model_name,
            "messages": zhipu_messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "top_p": self.config.top_p
        }

        # 添加工具（如果有）
        if tools:
            request_body["tools"] = self._format_tools_for_zhipu(tools)

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
                    raise Exception(f"智谱AI API错误: {response.status} - {error_text}")

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
            finish_reason=choice.get("finish_reason", "stop"),
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
        zhipu_messages = self._format_messages(messages)

        # 构建请求体
        request_body = {
            "model": self.config.model_name,
            "messages": zhipu_messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "top_p": self.config.top_p,
            "stream": True
        }

        # 添加工具（如果有）
        if tools:
            request_body["tools"] = self._format_tools_for_zhipu(tools)

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
                    raise Exception(f"智谱AI API错误: {response.status} - {error_text}")

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
        """格式化消息为智谱AI格式（类似OpenAI）"""
        zhipu_messages = []

        for msg in messages:
            message_dict = {
                "role": msg.role.value,
                "content": msg.content
            }

            # 添加工具调用（如果有）
            if msg.tool_calls:
                message_dict["tool_calls"] = msg.tool_calls

            # 添加工具调用ID（如果有）
            if msg.tool_call_id:
                message_dict["tool_call_id"] = msg.tool_call_id
                message_dict["role"] = "tool"

            zhipu_messages.append(message_dict)

        return zhipu_messages

    def _format_tools_for_zhipu(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        格式化工具为智谱AI格式

        智谱AI支持类似OpenAI的工具格式
        """
        return tools

    def _parse_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析智谱AI的工具调用（类似OpenAI）"""
        parsed_calls = []

        for call in tool_calls:
            # 智谱AI的工具调用格式可能需要特殊处理
            arguments = call["function"]["arguments"]
            if isinstance(arguments, str):
                arguments = json.loads(arguments)

            parsed_call = {
                "id": call.get("id", ""),
                "type": call.get("type", "function"),
                "function": {
                    "name": call["function"]["name"],
                    "arguments": arguments
                }
            }
            parsed_calls.append(parsed_call)

        return parsed_calls

    def format_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """智谱AI使用类似OpenAI的工具格式"""
        return tools
