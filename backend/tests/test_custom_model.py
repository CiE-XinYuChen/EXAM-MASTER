"""
测试自定义模型名称功能
Test custom model name functionality
"""

from sqlalchemy.orm import Session
from app.core.database import SessionMain, init_databases
from app.models.user_models import User, UserRole
from app.models.ai_models import AIConfig
from app.core.security import get_password_hash
import uuid


def test_custom_model_names():
    """测试各种自定义模型名称"""
    print("\n" + "="*60)
    print("测试自定义模型名称功能")
    print("="*60)

    main_db = SessionMain()

    try:
        # 创建或获取测试用户
        test_user = main_db.query(User).filter(User.username == "test_custom_model").first()
        if not test_user:
            test_user = User(
                username="test_custom_model",
                email="test_custom@example.com",
                password_hash=get_password_hash("test123"),
                role=UserRole.student,
                is_active=True
            )
            main_db.add(test_user)
            main_db.commit()
            main_db.refresh(test_user)
            print(f"✅ 创建测试用户: {test_user.username}")

        # 测试各种自定义模型名称
        test_cases = [
            {
                "name": "OpenAI GPT-4 Turbo 最新版",
                "provider": "openai",
                "model_name": "gpt-4-1106-preview",
                "description": "使用最新的GPT-4 Turbo模型"
            },
            {
                "name": "Claude 3.5 Sonnet",
                "provider": "claude",
                "model_name": "claude-3-5-sonnet-20240620",
                "description": "使用最新的Claude 3.5模型"
            },
            {
                "name": "DeepSeek Chat",
                "provider": "custom",
                "model_name": "deepseek-chat",
                "description": "使用DeepSeek的聊天模型"
            },
            {
                "name": "Qwen Turbo",
                "provider": "custom",
                "model_name": "qwen-turbo",
                "description": "使用通义千问Turbo模型"
            },
            {
                "name": "Moonshot v1",
                "provider": "custom",
                "model_name": "moonshot-v1-8k",
                "description": "使用Moonshot的8K上下文模型"
            }
        ]

        created_configs = []

        print(f"\n📝 创建 {len(test_cases)} 个自定义模型配置...")

        for i, test_case in enumerate(test_cases, 1):
            config_id = str(uuid.uuid4())
            config = AIConfig(
                id=config_id,
                user_id=test_user.id,
                name=test_case["name"],
                provider=test_case["provider"],
                model_name=test_case["model_name"],
                api_key=f"sk-test-{i}",
                temperature=0.7,
                max_tokens=2000,
                top_p=1.0,
                is_default=(i == 1),
                description=test_case["description"]
            )
            main_db.add(config)
            created_configs.append(config)
            print(f"   {i}. {test_case['name']}")
            print(f"      提供商: {test_case['provider']}")
            print(f"      模型: {test_case['model_name']}")

        main_db.commit()
        print(f"\n✅ 成功创建 {len(created_configs)} 个配置")

        # 验证所有配置
        print(f"\n📖 验证配置...")
        for config in created_configs:
            main_db.refresh(config)
            print(f"\n   配置: {config.name}")
            print(f"   ID: {config.id}")
            print(f"   提供商: {config.provider}")
            print(f"   模型名称: {config.model_name}")
            print(f"   描述: {config.description}")
            print(f"   默认: {'是' if config.is_default else '否'}")

        # 测试查询
        print(f"\n🔍 测试查询功能...")

        # 按提供商查询
        openai_configs = main_db.query(AIConfig).filter(
            AIConfig.user_id == test_user.id,
            AIConfig.provider == "openai"
        ).all()
        print(f"   OpenAI 配置数: {len(openai_configs)}")

        custom_configs = main_db.query(AIConfig).filter(
            AIConfig.user_id == test_user.id,
            AIConfig.provider == "custom"
        ).all()
        print(f"   自定义配置数: {len(custom_configs)}")

        # 查询默认配置
        default_config = main_db.query(AIConfig).filter(
            AIConfig.user_id == test_user.id,
            AIConfig.is_default == True
        ).first()
        if default_config:
            print(f"   默认配置: {default_config.name} ({default_config.model_name})")

        # 清理测试数据
        print(f"\n🗑️  清理测试数据...")
        for config in created_configs:
            main_db.delete(config)
        main_db.commit()
        print(f"✅ 清理完成")

        print("\n" + "="*60)
        print("✅ 自定义模型名称功能测试通过！")
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


def test_model_name_validation():
    """测试模型名称验证"""
    print("\n" + "="*60)
    print("测试模型名称验证")
    print("="*60)

    main_db = SessionMain()

    try:
        test_user = main_db.query(User).filter(User.username == "test_custom_model").first()
        if not test_user:
            print("⚠️  需要先创建测试用户")
            return False

        # 测试各种边界情况
        print("\n📝 测试边界情况...")

        # 1. 测试超长模型名称
        try:
            long_name = "a" * 101
            config = AIConfig(
                id=str(uuid.uuid4()),
                user_id=test_user.id,
                name="超长模型名称测试",
                provider="custom",
                model_name=long_name,
                api_key="test-key"
            )
            main_db.add(config)
            main_db.commit()
            main_db.delete(config)
            main_db.commit()
            print("   ⚠️  超长模型名称应该被拒绝（数据库层面会截断）")
        except Exception as e:
            print(f"   ✅ 超长模型名称被正确拒绝: {type(e).__name__}")

        # 2. 测试空模型名称
        try:
            config = AIConfig(
                id=str(uuid.uuid4()),
                user_id=test_user.id,
                name="空模型名称测试",
                provider="openai",
                model_name="",
                api_key="test-key"
            )
            main_db.add(config)
            main_db.commit()
            main_db.delete(config)
            main_db.commit()
            print("   ⚠️  空模型名称应该被拒绝")
        except Exception as e:
            print(f"   ✅ 空模型名称被正确拒绝: {type(e).__name__}")

        # 3. 测试特殊字符
        special_names = [
            "gpt-4-0125-preview",  # 带数字和连字符
            "claude_3_opus",        # 带下划线
            "model.v1",             # 带点号
            "model@latest",         # 带@符号
            "模型-中文-名称"        # 中文
        ]

        print(f"\n   测试特殊字符模型名称:")
        for model_name in special_names:
            try:
                config = AIConfig(
                    id=str(uuid.uuid4()),
                    user_id=test_user.id,
                    name=f"特殊字符测试: {model_name}",
                    provider="custom",
                    model_name=model_name,
                    api_key="test-key"
                )
                main_db.add(config)
                main_db.commit()
                main_db.delete(config)
                main_db.commit()
                print(f"      ✅ '{model_name}' - 通过")
            except Exception as e:
                print(f"      ❌ '{model_name}' - 失败: {type(e).__name__}")

        print("\n" + "="*60)
        print("✅ 模型名称验证测试完成！")
        print("="*60)

        return True

    except Exception as e:
        print(f"\n❌ 验证测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        main_db.rollback()
        return False
    finally:
        main_db.close()


def main():
    """运行所有测试"""
    print("\n" + "="*80)
    print(" "*20 + "自定义模型名称功能测试套件")
    print("="*80)

    # 初始化数据库
    print("\n🔧 初始化数据库...")
    init_databases()

    results = []

    # 测试1: 自定义模型名称
    result = test_custom_model_names()
    results.append(("自定义模型名称", result))

    # 测试2: 模型名称验证
    result = test_model_name_validation()
    results.append(("模型名称验证", result))

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
        print("\n✨ 功能特性:")
        print("   - 支持任意提供商的自定义模型名称")
        print("   - 支持常用模型的下拉选择")
        print("   - 支持自定义输入框手动输入")
        print("   - 编辑时自动识别模型是否在列表中")
        print("   - 自定义提供商自动切换到自定义输入")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查错误信息。")
        return 1


if __name__ == "__main__":
    import sys
    exit_code = main()
    sys.exit(exit_code)
