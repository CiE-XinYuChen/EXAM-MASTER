"""
Agent功能测试脚本
Test Agent functionality with MCP tools
"""

import asyncio
import sys
sys.path.insert(0, '/Users/shaynechen/shayne/demo/EXAM-MASTER/backend')

from app.core.database import SessionMain, SessionQBank
from app.models.ai_models import AIConfig
from app.services.ai.base import AIModelConfig, Message, MessageRole
from app.services.ai.openai_service import OpenAIService
from app.services.ai.agent_service import AgentService


async def test_agent():
    """测试Agent功能"""
    print("=" * 70)
    print("Agent功能测试")
    print("=" * 70)
    print()

    # 1. 从数据库加载AI配置
    print("📖 正在加载AI配置...")
    main_db = SessionMain()
    qbank_db = SessionQBank()

    try:
        # 获取第一个AI配置
        ai_config_db = main_db.query(AIConfig).first()

        if not ai_config_db:
            print("❌ 错误: 数据库中没有AI配置")
            print("💡 请先在管理面板中创建AI配置")
            return

        print(f"✅ 找到配置: {ai_config_db.name}")
        print(f"   提供商: {ai_config_db.provider}")
        print(f"   模型: {ai_config_db.model_name}")
        print(f"   Agent启用: {getattr(ai_config_db, 'enable_agent', True)}")
        print()

        # 2. 创建AI服务配置
        print("🤖 正在创建AI服务...")
        ai_model_config = AIModelConfig(
            model_name=ai_config_db.model_name,
            api_key=ai_config_db.api_key,
            base_url=ai_config_db.base_url,
            temperature=ai_config_db.temperature,
            max_tokens=ai_config_db.max_tokens,
            top_p=ai_config_db.top_p
        )

        # 创建基础AI服务
        if ai_config_db.provider == "openai" or ai_config_db.provider == "custom":
            ai_service = OpenAIService(ai_model_config)
        else:
            print(f"❌ 暂不支持的提供商: {ai_config_db.provider}")
            return

        print("✅ AI服务创建成功")
        print()

        # 3. 创建Agent服务
        print("🤖 正在创建Agent服务...")
        agent = AgentService(
            ai_service=ai_service,
            qbank_db=qbank_db,
            user_id=ai_config_db.user_id,
            max_tool_iterations=getattr(ai_config_db, 'max_tool_iterations', 5)
        )
        print("✅ Agent服务创建成功")
        print()

        # 4. 测试场景1: 获取题库列表
        print("=" * 70)
        print("测试场景1: 让AI获取题库列表")
        print("=" * 70)
        messages = [
            Message(
                role=MessageRole.user,
                content="请帮我查看一下我有哪些可用的题库？"
            )
        ]

        print("📤 发送请求...")
        result = await agent.chat_with_tools(
            messages=messages,
            provider=ai_config_db.provider,
            enable_tools=True
        )

        print()
        print("📥 收到响应:")
        print(f"   内容: {result['content'][:200]}...")
        print(f"   完成原因: {result['finish_reason']}")
        print(f"   工具调用次数: {len(result['tool_calls'])}")
        print(f"   迭代次数: {result['total_iterations']}")

        if result['tool_calls']:
            print()
            print("🔧 工具调用详情:")
            for i, call in enumerate(result['tool_calls'], 1):
                print(f"   {i}. {call['tool_name']}")
                print(f"      成功: {call['success']}")
                if call['success'] and 'result' in call:
                    result_data = call['result']
                    if 'banks' in result_data:
                        print(f"      返回了 {len(result_data['banks'])} 个题库")

        print()
        print("=" * 70)

        # 5. 测试场景2: 不使用工具（对比）
        print()
        print("=" * 70)
        print("测试场景2: 相同问题，不使用工具（对比）")
        print("=" * 70)

        result_no_tools = await agent.chat_with_tools(
            messages=messages,
            provider=ai_config_db.provider,
            enable_tools=False
        )

        print("📥 收到响应（无工具）:")
        print(f"   内容: {result_no_tools['content'][:200]}...")
        print(f"   工具调用次数: {len(result_no_tools['tool_calls'])}")
        print()

        print("=" * 70)
        print("🎉 测试完成！")
        print("=" * 70)
        print()
        print("对比结果:")
        print(f"  • 使用工具: 能够实际访问数据库，返回真实题库信息")
        print(f"  • 不使用工具: 只能基于训练数据回答，无法访问实时数据")
        print()

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        main_db.close()
        qbank_db.close()


async def test_mcp_tools():
    """测试MCP工具是否正常加载"""
    print("=" * 70)
    print("MCP工具检查")
    print("=" * 70)
    print()

    from app.api.mcp.tools import ALL_MCP_TOOLS, get_tools_schema

    print(f"✅ 共加载了 {len(ALL_MCP_TOOLS)} 个MCP工具:")
    print()

    for i, tool in enumerate(ALL_MCP_TOOLS, 1):
        print(f"{i}. {tool.name}")
        print(f"   描述: {tool.description}")
        print(f"   参数数量: {len(tool.parameters)}")
        print()

    print("=" * 70)
    print()


async def main():
    """主函数"""
    print()
    print("🚀 开始Agent系统测试")
    print()

    # 测试1: 检查MCP工具
    await test_mcp_tools()

    # 测试2: 测试Agent功能
    await test_agent()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
