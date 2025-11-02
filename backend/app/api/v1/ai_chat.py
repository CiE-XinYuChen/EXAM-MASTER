"""
AI Chat API - 对话式答题和AI助手
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from datetime import datetime
import uuid
import json

from app.core.database import get_main_db, get_qbank_db
from app.core.security import get_current_user
from app.models.user_models import User
from app.models.ai_models import AIConfig, ChatSession, ChatMessage
from app.schemas.ai_schemas import (
    AIProvider,
    AIConfigCreate,
    AIConfigUpdate,
    AIConfigResponse,
    AIConfigListResponse,
    ChatSessionCreate,
    ChatSessionResponse,
    ChatSessionListResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatResponse,
    ChatStreamRequest,
    AIUsageReport
)
from app.services.ai.base import Message as AIMessage, MessageRole, AIModelConfig
from app.services.ai.openai_service import OpenAIService
from app.services.ai.claude_service import ClaudeService
from app.services.ai.zhipu_service import ZhipuService
from app.api.mcp.tools import get_tools_schema, get_tools_for_claude
from app.api.mcp.handlers import execute_tool

router = APIRouter()


# ==================== Helper Functions ====================

def get_ai_service(config: AIConfig):
    """根据配置创建AI服务实例"""
    ai_config = AIModelConfig(
        model_name=config.model_name,
        api_key=config.api_key,
        base_url=config.base_url,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        top_p=config.top_p
    )

    if config.provider == AIProvider.openai.value:
        return OpenAIService(ai_config)
    elif config.provider == AIProvider.claude.value:
        return ClaudeService(ai_config)
    elif config.provider == AIProvider.zhipu.value:
        return ZhipuService(ai_config)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的AI提供商: {config.provider}"
        )


def get_system_prompt(mode: str, bank_id: Optional[str] = None) -> str:
    """获取系统提示词"""
    base_prompt = """你是EXAM-MASTER的AI学习助手，专门帮助用户进行高效学习和练习。

你可以使用以下工具来帮助用户：
- 获取题库和题目
- 帮助用户答题并提供即时反馈
- 管理收藏和错题
- 查看学习统计

请以友好、鼓励的方式与用户互动，帮助他们更好地学习和掌握知识。"""

    if mode == "practice":
        base_prompt += """

当前模式：答题练习模式
- 主动从题库中获取题目
- 逐个向用户展示题目
- 收集用户答案并提交
- 提供即时反馈和解析
- 记录学习进度"""

    elif mode == "review":
        base_prompt += """

当前模式：复习模式
- 重点关注错题和收藏题目
- 帮助用户理解易错知识点
- 提供详细的解题思路"""

    elif mode == "question":
        base_prompt += """

当前模式：问答模式
- 回答用户关于学习的问题
- 提供学习建议和统计分析
- 帮助用户查找相关题目"""

    return base_prompt


# ==================== AI Configuration Endpoints ====================

@router.post("/configs", response_model=AIConfigResponse, tags=["🤖 AI Chat"])
async def create_ai_config(
    config_data: AIConfigCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_main_db)
):
    """创建AI配置"""

    # 如果设置为默认配置，清除其他默认配置
    if config_data.is_default:
        db.query(AIConfig).filter(
            and_(
                AIConfig.user_id == current_user.id,
                AIConfig.is_default == True
            )
        ).update({"is_default": False})

    # 创建新配置
    config = AIConfig(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=config_data.name,
        provider=config_data.provider.value,
        model_name=config_data.model_name.value,
        api_key=config_data.api_key,  # TODO: 加密存储
        base_url=config_data.base_url,
        temperature=config_data.temperature,
        max_tokens=config_data.max_tokens,
        top_p=config_data.top_p,
        is_default=config_data.is_default,
        description=config_data.description,
        created_at=datetime.utcnow()
    )

    db.add(config)
    db.commit()
    db.refresh(config)

    return config


@router.get("/configs", response_model=AIConfigListResponse, tags=["🤖 AI Chat"])
async def list_ai_configs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_main_db)
):
    """获取用户的AI配置列表"""

    configs = db.query(AIConfig).filter(
        AIConfig.user_id == current_user.id
    ).order_by(desc(AIConfig.is_default), desc(AIConfig.created_at)).all()

    return AIConfigListResponse(configs=configs, total=len(configs))


@router.get("/configs/{config_id}", response_model=AIConfigResponse, tags=["🤖 AI Chat"])
async def get_ai_config(
    config_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_main_db)
):
    """获取AI配置详情"""

    config = db.query(AIConfig).filter(
        and_(
            AIConfig.id == config_id,
            AIConfig.user_id == current_user.id
        )
    ).first()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI配置不存在"
        )

    return config


@router.put("/configs/{config_id}", response_model=AIConfigResponse, tags=["🤖 AI Chat"])
async def update_ai_config(
    config_id: str,
    config_update: AIConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_main_db)
):
    """更新AI配置"""

    config = db.query(AIConfig).filter(
        and_(
            AIConfig.id == config_id,
            AIConfig.user_id == current_user.id
        )
    ).first()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI配置不存在"
        )

    # 如果设置为默认配置，清除其他默认配置
    if config_update.is_default:
        db.query(AIConfig).filter(
            and_(
                AIConfig.user_id == current_user.id,
                AIConfig.id != config_id,
                AIConfig.is_default == True
            )
        ).update({"is_default": False})

    # 更新字段
    if config_update.name:
        config.name = config_update.name
    if config_update.api_key:
        config.api_key = config_update.api_key
    if config_update.base_url is not None:
        config.base_url = config_update.base_url
    if config_update.temperature is not None:
        config.temperature = config_update.temperature
    if config_update.max_tokens is not None:
        config.max_tokens = config_update.max_tokens
    if config_update.top_p is not None:
        config.top_p = config_update.top_p
    if config_update.is_default is not None:
        config.is_default = config_update.is_default
    if config_update.description is not None:
        config.description = config_update.description

    config.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(config)

    return config


@router.delete("/configs/{config_id}", tags=["🤖 AI Chat"])
async def delete_ai_config(
    config_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_main_db)
):
    """删除AI配置"""

    config = db.query(AIConfig).filter(
        and_(
            AIConfig.id == config_id,
            AIConfig.user_id == current_user.id
        )
    ).first()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI配置不存在"
        )

    db.delete(config)
    db.commit()

    return {"success": True, "message": "AI配置已删除"}


# ==================== Chat Session Endpoints ====================

@router.post("/sessions", response_model=ChatSessionResponse, tags=["🤖 AI Chat"])
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    main_db: Session = Depends(get_main_db)
):
    """创建对话会话"""

    # 验证AI配置
    config = main_db.query(AIConfig).filter(
        and_(
            AIConfig.id == session_data.ai_config_id,
            AIConfig.user_id == current_user.id
        )
    ).first()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI配置不存在"
        )

    # 创建会话
    session = ChatSession(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        ai_config_id=session_data.ai_config_id,
        bank_id=session_data.bank_id,
        mode=session_data.mode.value,
        system_prompt=session_data.system_prompt or get_system_prompt(
            session_data.mode.value,
            session_data.bank_id
        ),
        total_messages=0,
        total_tokens=0,
        started_at=datetime.utcnow()
    )

    main_db.add(session)

    # 添加系统消息
    system_message = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=session.id,
        role="system",
        content=session.system_prompt,
        created_at=datetime.utcnow()
    )

    main_db.add(system_message)
    main_db.commit()
    main_db.refresh(session)

    return session


@router.get("/sessions", response_model=ChatSessionListResponse, tags=["🤖 AI Chat"])
async def list_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_main_db)
):
    """获取对话会话列表"""

    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(desc(ChatSession.last_activity_at)).all()

    return ChatSessionListResponse(sessions=sessions, total=len(sessions))


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse, tags=["🤖 AI Chat"])
async def get_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_main_db)
):
    """获取对话会话详情"""

    session = db.query(ChatSession).filter(
        and_(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        )
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话会话不存在"
        )

    return session


@router.delete("/sessions/{session_id}", tags=["🤖 AI Chat"])
async def delete_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_main_db)
):
    """删除对话会话"""

    session = db.query(ChatSession).filter(
        and_(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        )
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话会话不存在"
        )

    db.delete(session)
    db.commit()

    return {"success": True, "message": "对话会话已删除"}


# ==================== Chat Message Endpoints ====================

@router.get("/sessions/{session_id}/messages", tags=["🤖 AI Chat"])
async def get_chat_messages(
    session_id: str,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_main_db)
):
    """获取对话消息历史"""

    # 验证会话
    session = db.query(ChatSession).filter(
        and_(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        )
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话会话不存在"
        )

    # 获取消息
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).limit(limit).all()

    return {
        "messages": messages,
        "total": len(messages)
    }


@router.post("/sessions/{session_id}/chat", response_model=ChatResponse, tags=["🤖 AI Chat"])
async def chat(
    session_id: str,
    message_data: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    main_db: Session = Depends(get_main_db),
    qbank_db: Session = Depends(get_qbank_db)
):
    """发送消息并获取AI回复（非流式）"""

    # 获取会话和AI配置
    session = main_db.query(ChatSession).filter(
        and_(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        )
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话会话不存在"
        )

    config = main_db.query(AIConfig).filter(
        AIConfig.id == session.ai_config_id
    ).first()

    # 保存用户消息
    user_message = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role="user",
        content=message_data.content,
        created_at=datetime.utcnow()
    )
    main_db.add(user_message)

    # 获取对话历史
    history_messages = main_db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()

    # 转换为AI消息格式
    ai_messages = [
        AIMessage(
            role=MessageRole(msg.role),
            content=msg.content,
            tool_calls=msg.tool_calls,
            tool_call_id=msg.tool_call_id
        )
        for msg in history_messages
    ]

    # 获取工具定义
    tools = get_tools_schema() if config.provider == "openai" else get_tools_for_claude()

    # 调用AI服务
    ai_service = get_ai_service(config)
    response = await ai_service.chat(ai_messages, tools=tools)

    # 处理工具调用
    if response.tool_calls:
        # 保存AI消息（包含工具调用）
        assistant_message = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role="assistant",
            content=response.content or "",
            tool_calls=response.tool_calls,
            tokens=response.usage.get("completion_tokens") if response.usage else 0,
            created_at=datetime.utcnow()
        )
        main_db.add(assistant_message)

        # 执行工具调用
        for tool_call in response.tool_calls:
            tool_name = tool_call["function"]["name"]
            tool_args = tool_call["function"]["arguments"]

            # 执行工具
            tool_result = await execute_tool(tool_name, tool_args, qbank_db)

            # 保存工具结果消息
            tool_message = ChatMessage(
                id=str(uuid.uuid4()),
                session_id=session_id,
                role="tool",
                content=json.dumps(tool_result, ensure_ascii=False),
                tool_call_id=tool_call["id"],
                created_at=datetime.utcnow()
            )
            main_db.add(tool_message)

        main_db.commit()

        # 再次调用AI获取最终回复
        # (实际应用中可能需要递归调用，这里简化处理)
        return ChatResponse(
            message_id=assistant_message.id,
            content="工具调用完成，请刷新获取最新结果",
            tool_calls=response.tool_calls,
            finish_reason=response.finish_reason,
            tokens=response.usage.get("total_tokens", 0) if response.usage else 0
        )

    # 保存AI回复
    assistant_message = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role="assistant",
        content=response.content,
        tokens=response.usage.get("completion_tokens") if response.usage else 0,
        created_at=datetime.utcnow()
    )
    main_db.add(assistant_message)

    # 更新会话统计
    session.total_messages += 2  # 用户消息 + AI回复
    session.total_tokens += response.usage.get("total_tokens", 0) if response.usage else 0
    session.last_activity_at = datetime.utcnow()

    main_db.commit()

    return ChatResponse(
        message_id=assistant_message.id,
        content=response.content,
        tool_calls=None,
        finish_reason=response.finish_reason,
        tokens=response.usage.get("total_tokens", 0) if response.usage else 0
    )


# ==================== Usage Statistics Endpoints ====================

@router.get("/usage/report", response_model=AIUsageReport, tags=["🤖 AI Chat"])
async def get_usage_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_main_db)
):
    """获取AI使用报告"""

    # TODO: 实现详细的使用统计
    # 这里返回简化版本

    total_sessions = db.query(func.count(ChatSession.id)).filter(
        ChatSession.user_id == current_user.id
    ).scalar() or 0

    total_messages = db.query(func.count(ChatMessage.id)).join(
        ChatSession
    ).filter(
        ChatSession.user_id == current_user.id
    ).scalar() or 0

    total_tokens = db.query(func.sum(ChatSession.total_tokens)).filter(
        ChatSession.user_id == current_user.id
    ).scalar() or 0

    from app.schemas.ai_schemas import AIUsageStatistics

    overview = AIUsageStatistics(
        total_sessions=total_sessions,
        total_messages=total_messages,
        total_tokens=total_tokens,
        by_provider={},
        by_model={}
    )

    return AIUsageReport(
        overview=overview,
        daily_usage=[],
        top_models=[]
    )
