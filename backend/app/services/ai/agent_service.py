"""
Agent Service - AI Agent with MCP Tool Calling
整合MCP工具调用能力的AI Agent服务
"""

from typing import List, Dict, Any, Optional, AsyncIterator
from sqlalchemy.orm import Session
import json
import logging

from app.services.ai.base import BaseAIService, AIModelConfig, Message, MessageRole, AIResponse
from app.api.mcp.tools import get_tools_schema, get_tools_for_claude
from app.api.mcp.handlers import execute_tool

logger = logging.getLogger(__name__)


class AgentService:
    """
    Agent服务 - 带工具调用能力的AI助手

    功能:
    1. 自动调用MCP工具
    2. 处理多轮工具调用
    3. 记录工具调用历史
    """

    def __init__(
        self,
        ai_service: BaseAIService,
        qbank_db: Session,
        user_id: int,
        max_tool_iterations: int = 5
    ):
        """
        初始化Agent服务

        Args:
            ai_service: 底层AI服务(OpenAI/Claude/等)
            qbank_db: 题库数据库连接
            user_id: 当前用户ID
            max_tool_iterations: 最大工具调用次数
        """
        self.ai_service = ai_service
        self.qbank_db = qbank_db
        self.user_id = user_id
        self.max_tool_iterations = max_tool_iterations
        self.tool_call_history = []

    def _get_tools_for_provider(self, provider: str) -> List[Dict[str, Any]]:
        """根据AI提供商获取工具定义"""
        if provider == "claude":
            return get_tools_for_claude()
        else:
            # OpenAI format (also used for most other providers)
            return get_tools_schema()

    async def chat_with_tools(
        self,
        messages: List[Message],
        provider: str = "openai",
        enable_tools: bool = True
    ) -> Dict[str, Any]:
        """
        带工具调用的对话

        Args:
            messages: 对话历史
            provider: AI提供商类型
            enable_tools: 是否启用工具调用

        Returns:
            包含响应内容和工具调用历史的字典
        """
        if not enable_tools:
            # 不使用工具，直接调用AI
            response = await self.ai_service.chat(messages)
            return {
                "content": response.content,
                "finish_reason": response.finish_reason,
                "tool_calls": [],
                "total_iterations": 0
            }

        # 获取工具定义
        tools = self._get_tools_for_provider(provider)

        # 工具调用循环
        iteration = 0
        current_messages = messages.copy()
        all_tool_calls = []

        while iteration < self.max_tool_iterations:
            logger.info(f"Agent iteration {iteration + 1}/{self.max_tool_iterations}")

            # 调用AI
            response = await self.ai_service.chat(
                messages=current_messages,
                tools=tools
            )

            # 如果没有工具调用，返回结果
            if response.finish_reason == "stop" or not response.tool_calls:
                logger.info("Agent completed without tool calls")
                return {
                    "content": response.content,
                    "finish_reason": response.finish_reason,
                    "tool_calls": all_tool_calls,
                    "total_iterations": iteration + 1,
                    "usage": response.usage
                }

            # 处理工具调用
            logger.info(f"Agent requesting {len(response.tool_calls)} tool calls")

            # 添加助手消息（包含工具调用请求）
            current_messages.append(Message(
                role=MessageRole.assistant,
                content=response.content or "",
                tool_calls=response.tool_calls
            ))

            # 执行每个工具调用
            for tool_call in response.tool_calls:
                tool_name = tool_call.get("function", {}).get("name") or tool_call.get("name")
                tool_args_str = tool_call.get("function", {}).get("arguments") or tool_call.get("input", {})
                tool_call_id = tool_call.get("id") or f"call_{iteration}_{tool_name}"

                logger.info(f"Executing tool: {tool_name}")

                try:
                    # 解析参数
                    if isinstance(tool_args_str, str):
                        tool_args = json.loads(tool_args_str)
                    else:
                        tool_args = tool_args_str

                    # 注入user_id
                    tool_args["user_id"] = self.user_id

                    # 执行工具
                    tool_result = await execute_tool(tool_name, tool_args, self.qbank_db)

                    # 记录工具调用
                    call_record = {
                        "iteration": iteration + 1,
                        "tool_name": tool_name,
                        "arguments": tool_args,
                        "result": tool_result,
                        "success": tool_result.get("success", False)
                    }
                    all_tool_calls.append(call_record)

                    # 添加工具结果消息
                    current_messages.append(Message(
                        role=MessageRole.tool,
                        content=json.dumps(tool_result, ensure_ascii=False),
                        tool_call_id=tool_call_id
                    ))

                    logger.info(f"Tool {tool_name} executed: {tool_result.get('success', False)}")

                except Exception as e:
                    logger.error(f"Tool execution failed: {str(e)}")
                    error_result = {
                        "success": False,
                        "error": f"工具执行失败: {str(e)}"
                    }

                    all_tool_calls.append({
                        "iteration": iteration + 1,
                        "tool_name": tool_name,
                        "arguments": tool_args if 'tool_args' in locals() else {},
                        "result": error_result,
                        "success": False
                    })

                    current_messages.append(Message(
                        role=MessageRole.tool,
                        content=json.dumps(error_result, ensure_ascii=False),
                        tool_call_id=tool_call_id
                    ))

            iteration += 1

        # 达到最大迭代次数
        logger.warning(f"Agent reached max iterations ({self.max_tool_iterations})")
        return {
            "content": "达到最大工具调用次数限制",
            "finish_reason": "max_iterations",
            "tool_calls": all_tool_calls,
            "total_iterations": iteration
        }

    async def chat_stream_with_tools(
        self,
        messages: List[Message],
        provider: str = "openai",
        enable_tools: bool = True
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        流式对话（带工具调用）

        Yields:
            事件字典，包含type和data字段
        """
        if not enable_tools:
            # 不使用工具，直接流式输出
            async for chunk in self.ai_service.chat_stream(messages):
                yield {
                    "type": "content",
                    "data": chunk
                }
            return

        # 获取工具定义
        tools = self._get_tools_for_provider(provider)

        iteration = 0
        current_messages = messages.copy()

        while iteration < self.max_tool_iterations:
            yield {
                "type": "iteration_start",
                "data": {
                    "iteration": iteration + 1,
                    "max_iterations": self.max_tool_iterations
                }
            }

            # 首先进行非流式调用以获取工具调用
            response = await self.ai_service.chat(
                messages=current_messages,
                tools=tools
            )

            # 如果有内容，输出内容
            if response.content:
                yield {
                    "type": "content",
                    "data": response.content
                }

            # 如果没有工具调用，结束
            if response.finish_reason == "stop" or not response.tool_calls:
                yield {
                    "type": "done",
                    "data": {
                        "finish_reason": response.finish_reason,
                        "total_iterations": iteration + 1
                    }
                }
                return

            # 输出工具调用信息
            yield {
                "type": "tool_calls_start",
                "data": {
                    "tool_count": len(response.tool_calls)
                }
            }

            # 添加助手消息
            current_messages.append(Message(
                role=MessageRole.assistant,
                content=response.content or "",
                tool_calls=response.tool_calls
            ))

            # 执行工具调用
            for tool_call in response.tool_calls:
                tool_name = tool_call.get("function", {}).get("name") or tool_call.get("name")
                tool_args_str = tool_call.get("function", {}).get("arguments") or tool_call.get("input", {})
                tool_call_id = tool_call.get("id") or f"call_{iteration}_{tool_name}"

                yield {
                    "type": "tool_call",
                    "data": {
                        "tool_name": tool_name,
                        "status": "executing"
                    }
                }

                try:
                    # 解析并执行
                    if isinstance(tool_args_str, str):
                        tool_args = json.loads(tool_args_str)
                    else:
                        tool_args = tool_args_str

                    tool_args["user_id"] = self.user_id
                    tool_result = await execute_tool(tool_name, tool_args, self.qbank_db)

                    yield {
                        "type": "tool_result",
                        "data": {
                            "tool_name": tool_name,
                            "success": tool_result.get("success", False),
                            "result": tool_result
                        }
                    }

                    current_messages.append(Message(
                        role=MessageRole.tool,
                        content=json.dumps(tool_result, ensure_ascii=False),
                        tool_call_id=tool_call_id
                    ))

                except Exception as e:
                    error_result = {"success": False, "error": str(e)}
                    yield {
                        "type": "tool_error",
                        "data": {
                            "tool_name": tool_name,
                            "error": str(e)
                        }
                    }

                    current_messages.append(Message(
                        role=MessageRole.tool,
                        content=json.dumps(error_result, ensure_ascii=False),
                        tool_call_id=tool_call_id
                    ))

            iteration += 1

        yield {
            "type": "error",
            "data": {
                "message": "达到最大工具调用次数限制"
            }
        }
