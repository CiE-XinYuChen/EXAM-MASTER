# Agent系统快速开始指南

## 🚀 快速开始

### 第一步：数据库迁移

```bash
cd /Users/shaynechen/shayne/demo/EXAM-MASTER/backend
sqlite3 databases/main.db < add_agent_fields_migration.sql
```

### 第二步：测试Agent功能

```bash
python test_agent.py
```

您应该看到：
```
🚀 开始Agent系统测试

======================================================================
MCP工具检查
======================================================================

✅ 共加载了 12 个MCP工具:

1. get_question_banks
   描述: 获取用户有权限访问的题库列表
   参数数量: 2

2. get_questions
   描述: 从指定题库获取题目列表，支持筛选和搜索
   参数数量: 7

... (更多工具)

======================================================================
Agent功能测试
======================================================================

📖 正在加载AI配置...
✅ 找到配置: admin
   提供商: custom
   模型: gpt-5
   Agent启用: True

🤖 正在创建AI服务...
✅ AI服务创建成功

🤖 正在创建Agent服务...
✅ Agent服务创建成功

======================================================================
测试场景1: 让AI获取题库列表
======================================================================
📤 发送请求...

📥 收到响应:
   内容: 您目前有以下可用的题库...
   完成原因: stop
   工具调用次数: 1
   迭代次数: 1

🔧 工具调用详情:
   1. get_question_banks
      成功: True
      返回了 X 个题库

🎉 测试完成！
```

### 第三步：在代码中使用Agent

```python
from app.services.ai.agent_service import AgentService
from app.services.ai.openai_service import OpenAIService
from app.services.ai.base import AIModelConfig, Message, MessageRole

# 1. 创建AI服务
ai_config = AIModelConfig(
    model_name="gpt-4",
    api_key="your-api-key",
    base_url="https://api.chienkjapi.mom/v1",
    temperature=0.7,
    max_tokens=2000,
    top_p=1.0
)

ai_service = OpenAIService(ai_config)

# 2. 创建Agent服务
agent = AgentService(
    ai_service=ai_service,
    qbank_db=your_qbank_db,
    user_id=user_id,
    max_tool_iterations=5
)

# 3. 发送请求
messages = [
    Message(
        role=MessageRole.user,
        content="请帮我查看一下我有哪些可用的题库？"
    )
]

result = await agent.chat_with_tools(
    messages=messages,
    provider="openai",
    enable_tools=True
)

print(result['content'])
```

## 💡 常见问题

### Q1: 如何知道Agent是否在工作？

查看`result['tool_calls']`列表，如果不为空说明Agent调用了工具：

```python
if result['tool_calls']:
    print(f"Agent调用了 {len(result['tool_calls'])} 次工具")
    for call in result['tool_calls']:
        print(f"- {call['tool_name']}: {call['success']}")
else:
    print("Agent没有使用工具")
```

### Q2: Agent支持哪些模型？

支持所有具有Function Calling能力的模型：
- ✅ GPT-4 / GPT-4 Turbo
- ✅ GPT-3.5 Turbo
- ✅ Claude 3 (Opus/Sonnet/Haiku)
- ✅ GPT-4o / GPT-5
- ❌ 基础模型（gpt-3.5-turbo-instruct等）不支持

### Q3: 如何禁用Agent功能？

在调用时设置`enable_tools=False`:

```python
result = await agent.chat_with_tools(
    messages=messages,
    enable_tools=False  # 禁用工具
)
```

或者在数据库中设置`ai_configs.enable_agent = FALSE`。

### Q4: Agent能做什么？

Agent可以：
- 📚 获取和搜索题库
- 📝 获取题目并帮助答题
- ❌ 查看和管理错题
- ⭐ 管理收藏题目
- 📊 查询学习统计

基本上，用户能通过界面做的事情，Agent都能帮忙完成！

### Q5: 如何添加新的工具？

参考文档 `AGENT_SYSTEM.md` 的"未来扩展"章节。

## 🎯 使用场景示例

### 场景1：智能题库助手

**用户**: "从算法题库给我出10道关于二叉树的中等难度题目"

**Agent工作流程**:
1. 调用`get_question_banks`找到算法题库
2. 调用`get_questions`筛选二叉树、中等难度题目
3. 返回10道符合条件的题目

### 场景2：错题复习助手

**用户**: "帮我看看我在数据结构题库有哪些错了3次以上的题目"

**Agent工作流程**:
1. 调用`get_question_banks`找到数据结构题库
2. 调用`get_wrong_questions`筛选错误3次以上的题目
3. 返回高频错题列表

### 场景3：学习进度查询

**用户**: "我的整体学习情况怎么样？"

**Agent工作流程**:
1. 调用`get_user_statistics`获取总体统计
2. 分析准确率、练习题数等数据
3. 给出学习建议

## 🔧 调试技巧

### 启用详细日志

```python
import logging
logging.basicConfig(level=logging.INFO)
```

### 查看工具调用详情

```python
for i, call in enumerate(result['tool_calls'], 1):
    print(f"\n工具调用 #{i}:")
    print(f"  工具: {call['tool_name']}")
    print(f"  参数: {call['arguments']}")
    print(f"  成功: {call['success']}")
    if call['success']:
        print(f"  结果: {call['result']}")
```

### 测试特定工具

直接调用MCP API：

```bash
curl -X POST http://localhost:8000/api/mcp/execute \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_question_banks",
    "parameters": {"include_stats": true}
  }'
```

## 📚 更多资源

- 📖 完整文档: `docs/AGENT_SYSTEM.md`
- 🧪 测试脚本: `test_agent.py`
- 🔧 工具定义: `app/api/mcp/tools.py`
- 💻 处理函数: `app/api/mcp/handlers.py`
- 🤖 Agent服务: `app/services/ai/agent_service.py`

## ✅ 检查清单

- [ ] 运行数据库迁移
- [ ] 测试脚本执行成功
- [ ] MCP API端点可访问
- [ ] AI配置中启用了Agent
- [ ] 测试了至少一个实际场景

完成以上步骤后，您的Agent系统就准备就绪了！🎉

---

**提示**: 如果遇到问题，请先查看日志输出，大多数问题都能通过日志快速定位。
