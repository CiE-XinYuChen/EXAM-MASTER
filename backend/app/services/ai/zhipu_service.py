"""
Zhipu AI Service Implementation
智谱AI (GLM) API集成
"""

from typing import List, Dict, Any, Optional, AsyncIterator
import json
import asyncio
from zhipuai import ZhipuAI
from app.services.ai.base import (
    BaseAIService, AIModelConfig, AIResponse, Message, MessageRole
)


class ZhipuService(BaseAIService):
    """
    智谱AI服务实现
    
    支持模型:
    - glm-4
    - glm-4-plus
    - glm-4-flash
    - glm-3-turbo
    """

    def __init__(self, config: AIModelConfig):
        super().__init__(config)
        
        # 处理 base_url
        base_url = config.base_url
        if not base_url or base_url.strip() == "":
            base_url = None
        elif base_url.rstrip("/") == "https://open.bigmodel.cn":
            base_url = None
            
        # 初始化智谱AI客户端
        self.client = ZhipuAI(api_key=config.api_key, base_url=base_url)

    async def chat(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False
    ) -> AIResponse:
        """发送聊天请求到智谱AI API"""
        
        # 构建请求参数
        kwargs = {
            "model": self.config.model_name,
            "messages": self._format_messages(messages),
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "top_p": self.config.top_p,
            "stream": False
        }

        # 如果启用工具
        if tools:
            kwargs["tools"] = tools

        # 调用SDK (同步调用需包装在线程中)
        try:
            # 使用asyncio.to_thread运行同步的SDK调用
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                **kwargs
            )
            
            choice = response.choices[0]
            message = choice.message
            
            # 解析工具调用
            tool_calls = []
            if message.tool_calls:
                for tc in message.tool_calls:
                    tool_calls.append({
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": json.loads(tc.function.arguments)
                        }
                    })

            return AIResponse(
                content=message.content or "",
                finish_reason=choice.finish_reason,
                tool_calls=tool_calls if tool_calls else None,
                usage=response.usage.model_dump() if response.usage else None
            )

        except Exception as e:
            raise Exception(f"智谱AI API错误: {str(e)}")

    async def chat_stream(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncIterator[str]:
        """流式聊天"""
        
        # 构建请求参数
        kwargs = {
            "model": self.config.model_name,
            "messages": self._format_messages(messages),
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "top_p": self.config.top_p,
            "stream": True
        }
        
        if tools:
            kwargs["tools"] = tools

        try:
            # 启动流式请求
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                **kwargs
            )
            
            # 迭代生成器
            # 由于SyncIterator不能直接await，我们需要将其包装
            iterator = iter(response)
            
            while True:
                try:
                    # 在线程中获取下一个chunk，避免阻塞事件循环
                    chunk = await asyncio.to_thread(next, iterator)
                    
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if delta.content:
                            yield delta.content
                            
                except StopIteration:
                    break
                except Exception as e:
                     raise Exception(f"流式读取错误: {str(e)}")

        except Exception as e:
            raise Exception(f"智谱AI API错误: {str(e)}")

    def _format_messages(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """格式化消息为智谱AI格式"""
        zhipu_messages = []
        for msg in messages:
            message_dict = {
                "role": msg.role.value,
                "content": msg.content
            }
            
            # 处理工具调用
            if msg.tool_calls:
                message_dict["tool_calls"] = msg.tool_calls
            
            # 处理工具响应
            if msg.tool_call_id:
                message_dict["tool_call_id"] = msg.tool_call_id
                
            zhipu_messages.append(message_dict)
        return zhipu_messages