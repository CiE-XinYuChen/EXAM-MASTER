"""
Test script for AI Chat API endpoints
测试AI聊天API端点
"""

import asyncio
import sys
from sqlalchemy.orm import Session
from app.core.database import SessionMain, SessionQBank, init_databases
from app.models.user_models import User, UserRole
from app.models.ai_models import AIConfig, ChatSession, ChatMessage
from app.core.security import get_password_hash
import uuid


async def test_ai_config_crud():
    """Test AI configuration CRUD operations"""
    print("\n" + "="*60)
    print("测试 AI 配置 CRUD 操作")
    print("="*60)

    main_db = SessionMain()

    try:
        # 1. 创建测试用户（如果不存在）
        test_user = main_db.query(User).filter(User.username == "test_ai_user").first()

        if not test_user:
            print("\n📝 创建测试用户...")
            test_user = User(
                username="test_ai_user",
                email="test_ai@example.com",
                password_hash=get_password_hash("test123"),
                role=UserRole.student,
                is_active=True
            )
            main_db.add(test_user)
            main_db.commit()
            main_db.refresh(test_user)
            print(f"✅ 创建测试用户成功: {test_user.username} (ID: {test_user.id})")
        else:
            print(f"✅ 使用现有测试用户: {test_user.username} (ID: {test_user.id})")

        # 2. 创建 AI 配置
        print("\n📝 创建 OpenAI 配置...")
        config_id = str(uuid.uuid4())
        ai_config = AIConfig(
            id=config_id,
            user_id=test_user.id,
            name="测试 OpenAI 配置",
            provider="openai",
            model_name="gpt-3.5-turbo",
            api_key="sk-test-key-123456",
            base_url="https://api.openai.com/v1",
            temperature=0.7,
            max_tokens=2000,
            top_p=1.0,
            is_default=True,
            description="这是一个测试配置"
        )
        main_db.add(ai_config)
        main_db.commit()
        main_db.refresh(ai_config)
        print(f"✅ AI 配置创建成功: {ai_config.name} (ID: {ai_config.id})")

        # 3. 读取 AI 配置
        print("\n📖 读取 AI 配置...")
        retrieved_config = main_db.query(AIConfig).filter(AIConfig.id == config_id).first()
        if retrieved_config:
            print(f"✅ 配置名称: {retrieved_config.name}")
            print(f"   提供商: {retrieved_config.provider}")
            print(f"   模型: {retrieved_config.model_name}")
            print(f"   是否默认: {retrieved_config.is_default}")
        else:
            print("❌ 配置读取失败")
            return False

        # 4. 更新 AI 配置
        print("\n✏️  更新 AI 配置...")
        retrieved_config.temperature = 0.9
        retrieved_config.description = "更新后的配置描述"
        main_db.commit()
        print(f"✅ 配置更新成功: temperature = {retrieved_config.temperature}")

        # 5. 列出用户的所有配置
        print("\n📋 列出用户的所有 AI 配置...")
        user_configs = main_db.query(AIConfig).filter(AIConfig.user_id == test_user.id).all()
        print(f"✅ 找到 {len(user_configs)} 个配置:")
        for cfg in user_configs:
            print(f"   - {cfg.name} ({cfg.provider}/{cfg.model_name})")

        # 6. 测试会话创建
        print("\n📝 创建聊天会话...")
        session_id = str(uuid.uuid4())
        chat_session = ChatSession(
            id=session_id,
            user_id=test_user.id,
            ai_config_id=config_id,
            bank_id=None,  # 问答模式，不绑定题库
            mode="question",
            system_prompt="你是一个友好的AI助手。",
            total_messages=0,
            total_tokens=0
        )
        main_db.add(chat_session)
        main_db.commit()
        main_db.refresh(chat_session)
        print(f"✅ 聊天会话创建成功: {chat_session.id}")
        print(f"   模式: {chat_session.mode}")

        # 7. 创建消息
        print("\n📝 创建聊天消息...")

        # 系统消息
        system_msg = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role="system",
            content="你是一个友好的AI助手。",
            tokens=10
        )
        main_db.add(system_msg)

        # 用户消息
        user_msg = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role="user",
            content="你好！",
            tokens=5
        )
        main_db.add(user_msg)

        # AI回复
        assistant_msg = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role="assistant",
            content="你好！我是你的AI助手，有什么可以帮助你的吗？",
            tokens=15
        )
        main_db.add(assistant_msg)

        # 更新会话统计
        chat_session.total_messages = 3
        chat_session.total_tokens = 30

        main_db.commit()
        print(f"✅ 创建了 3 条消息")
        print(f"   会话总消息数: {chat_session.total_messages}")
        print(f"   会话总 tokens: {chat_session.total_tokens}")

        # 8. 读取会话消息
        print("\n📖 读取会话消息...")
        messages = main_db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at).all()

        print(f"✅ 找到 {len(messages)} 条消息:")
        for msg in messages:
            print(f"   {msg.role}: {msg.content[:50]}...")

        # 9. 删除测试数据
        print("\n🗑️  清理测试数据...")
        main_db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
        main_db.query(ChatSession).filter(ChatSession.id == session_id).delete()
        main_db.query(AIConfig).filter(AIConfig.id == config_id).delete()
        main_db.commit()
        print("✅ 测试数据清理完成")

        print("\n" + "="*60)
        print("✅ AI 配置 CRUD 测试全部通过！")
        print("="*60)
        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        main_db.rollback()
        return False
    finally:
        main_db.close()


async def test_ai_statistics():
    """Test AI usage statistics"""
    print("\n" + "="*60)
    print("测试 AI 使用统计")
    print("="*60)

    main_db = SessionMain()

    try:
        # 获取 AI 配置总数
        total_configs = main_db.query(AIConfig).count()
        print(f"\n📊 AI 配置总数: {total_configs}")

        # 获取聊天会话总数
        total_sessions = main_db.query(ChatSession).count()
        print(f"📊 聊天会话总数: {total_sessions}")

        # 获取消息总数
        total_messages = main_db.query(ChatMessage).count()
        print(f"📊 消息总数: {total_messages}")

        # 按提供商统计配置
        from sqlalchemy import func
        provider_stats = main_db.query(
            AIConfig.provider,
            func.count(AIConfig.id).label('count')
        ).group_by(AIConfig.provider).all()

        print(f"\n📊 按提供商统计配置:")
        for provider, count in provider_stats:
            print(f"   {provider}: {count}")

        # 按模式统计会话
        mode_stats = main_db.query(
            ChatSession.mode,
            func.count(ChatSession.id).label('count')
        ).group_by(ChatSession.mode).all()

        print(f"\n📊 按模式统计会话:")
        for mode, count in mode_stats:
            print(f"   {mode}: {count}")

        # 统计总 tokens
        total_tokens = main_db.query(
            func.sum(ChatSession.total_tokens)
        ).scalar() or 0

        print(f"\n📊 总消耗 tokens: {total_tokens}")

        print("\n" + "="*60)
        print("✅ AI 统计测试完成！")
        print("="*60)
        return True

    except Exception as e:
        print(f"\n❌ 统计测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        main_db.close()


async def test_mcp_tools_availability():
    """Test MCP tools availability"""
    print("\n" + "="*60)
    print("测试 MCP 工具可用性")
    print("="*60)

    try:
        from app.api.mcp.tools import get_tools_schema

        tools = get_tools_schema()
        print(f"\n📊 可用 MCP 工具总数: {len(tools)}")

        print("\n📋 工具列表:")
        for tool in tools:
            print(f"\n   名称: {tool['function']['name']}")
            print(f"   描述: {tool['function']['description'][:60]}...")
            params = tool['function']['parameters'].get('properties', {})
            print(f"   参数: {', '.join(params.keys())}")

        print("\n" + "="*60)
        print("✅ MCP 工具可用性测试完成！")
        print("="*60)
        return True

    except Exception as e:
        print(f"\n❌ MCP 工具测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print(" "*25 + "AI 功能测试套件")
    print("="*80)

    # 初始化数据库
    print("\n🔧 初始化数据库...")
    init_databases()

    # 运行测试
    results = []

    # 1. CRUD 测试
    result = await test_ai_config_crud()
    results.append(("AI 配置 CRUD", result))

    # 2. 统计测试
    result = await test_ai_statistics()
    results.append(("AI 使用统计", result))

    # 3. MCP 工具测试
    result = await test_mcp_tools_availability()
    results.append(("MCP 工具", result))

    # 汇总结果
    print("\n" + "="*80)
    print(" "*30 + "测试结果汇总")
    print("="*80)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:.<50} {status}")

    all_passed = all(result for _, result in results)

    if all_passed:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查错误信息。")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
