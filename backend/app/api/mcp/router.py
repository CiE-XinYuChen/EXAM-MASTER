"""
MCP API Router - MCP服务端点
提供标准化的MCP接口供AI模型调用
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_qbank_db
from app.core.security import get_current_user
from app.models.user_models import User
from app.api.mcp.tools import get_tools_schema, get_tools_for_claude, get_tool_by_name, ALL_MCP_TOOLS
from app.api.mcp.handlers import execute_tool

router = APIRouter()


# ==================== Request/Response Models ====================

class MCPToolCallRequest(BaseModel):
    """工具调用请求"""
    tool_name: str
    parameters: Dict[str, Any]


class MCPToolCallResponse(BaseModel):
    """工具调用响应"""
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class MCPToolsListResponse(BaseModel):
    """工具列表响应"""
    tools: List[Dict[str, Any]]
    total: int
    format: str  # "openai" or "claude"


# ==================== MCP Endpoints ====================

@router.get("/tools", response_model=MCPToolsListResponse, tags=["🤖 MCP"])
async def list_mcp_tools(
    format: str = "openai",
    current_user: User = Depends(get_current_user)
):
    """
    获取所有可用的MCP工具定义

    Parameters:
    - format: 工具格式，"openai" 或 "claude"
    """
    if format == "claude":
        tools = get_tools_for_claude()
    else:
        tools = get_tools_schema()

    return MCPToolsListResponse(
        tools=tools,
        total=len(tools),
        format=format
    )


@router.post("/execute", response_model=MCPToolCallResponse, tags=["🤖 MCP"])
async def execute_mcp_tool(
    request: MCPToolCallRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """
    执行MCP工具

    AI模型可以通过此端点调用任何定义好的工具
    """
    # 验证工具是否存在
    tool = get_tool_by_name(request.tool_name)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工具不存在: {request.tool_name}"
        )

    # 注入user_id（如果工具需要）
    params = request.parameters.copy()
    if "user_id" in [p.name for p in tool.parameters]:
        params["user_id"] = current_user.id

    # 执行工具
    result = await execute_tool(request.tool_name, params, db)

    if result.get("success"):
        return MCPToolCallResponse(
            success=True,
            result=result
        )
    else:
        return MCPToolCallResponse(
            success=False,
            error=result.get("error", "工具执行失败")
        )


@router.get("/tools/{tool_name}", tags=["🤖 MCP"])
async def get_tool_definition(
    tool_name: str,
    format: str = "openai",
    current_user: User = Depends(get_current_user)
):
    """获取单个工具的定义"""
    tool = get_tool_by_name(tool_name)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工具不存在: {tool_name}"
        )

    if format == "claude":
        tools = get_tools_for_claude()
        tool_def = next((t for t in tools if t["name"] == tool_name), None)
    else:
        tools = get_tools_schema()
        tool_def = next((t for t in tools if t["function"]["name"] == tool_name), None)

    return tool_def


# ==================== Batch Execution ====================

class MCPBatchRequest(BaseModel):
    """批量工具调用请求"""
    calls: List[MCPToolCallRequest]


class MCPBatchResponse(BaseModel):
    """批量工具调用响应"""
    results: List[MCPToolCallResponse]
    total: int
    success_count: int
    failed_count: int


@router.post("/batch", response_model=MCPBatchResponse, tags=["🤖 MCP"])
async def execute_batch_tools(
    request: MCPBatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """
    批量执行多个MCP工具

    用于一次性执行多个工具调用，提高效率
    """
    results = []
    success_count = 0
    failed_count = 0

    for call in request.calls:
        # 验证工具
        tool = get_tool_by_name(call.tool_name)
        if not tool:
            results.append(MCPToolCallResponse(
                success=False,
                error=f"工具不存在: {call.tool_name}"
            ))
            failed_count += 1
            continue

        # 注入user_id
        params = call.parameters.copy()
        if "user_id" in [p.name for p in tool.parameters]:
            params["user_id"] = current_user.id

        # 执行工具
        result = await execute_tool(call.tool_name, params, db)

        if result.get("success"):
            results.append(MCPToolCallResponse(success=True, result=result))
            success_count += 1
        else:
            results.append(MCPToolCallResponse(
                success=False,
                error=result.get("error", "工具执行失败")
            ))
            failed_count += 1

    return MCPBatchResponse(
        results=results,
        total=len(results),
        success_count=success_count,
        failed_count=failed_count
    )


# ==================== Tool Discovery ====================

@router.get("/categories", tags=["🤖 MCP"])
async def get_tool_categories(
    current_user: User = Depends(get_current_user)
):
    """获取工具分类"""
    categories = {
        "question_bank": {
            "name": "题库管理",
            "tools": ["get_question_banks", "get_questions", "get_question_detail", "search_questions"]
        },
        "practice": {
            "name": "答题练习",
            "tools": ["create_practice_session", "submit_answer", "get_question_explanation"]
        },
        "wrong_questions": {
            "name": "错题管理",
            "tools": ["get_wrong_questions", "mark_wrong_question_corrected"]
        },
        "favorites": {
            "name": "收藏管理",
            "tools": ["add_favorite", "get_favorites"]
        },
        "statistics": {
            "name": "统计查询",
            "tools": ["get_user_statistics"]
        }
    }

    return {
        "categories": categories,
        "total_categories": len(categories),
        "total_tools": len(ALL_MCP_TOOLS)
    }
