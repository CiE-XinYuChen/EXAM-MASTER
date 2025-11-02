# Agent System Documentation

## 概述 (Overview)

EXAM-MASTER现已集成完整的AI Agent系统，支持12个MCP (Model Context Protocol) 工具，让AI助手能够自动调用题库系统的各种功能。

## 系统状态 ✅

- **状态**: 已完成并可用
- **工具数量**: 12个MCP工具
- **支持的AI提供商**: OpenAI, Claude, 自定义兼容API
- **管理界面**: 已集成到 /admin/agent-test
- **测试脚本**: test_agent.py

## 快速开始

### 1. 启动服务器
```bash
cd /Users/shaynechen/shayne/demo/EXAM-MASTER/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 访问Agent测试界面
```
http://localhost:8000/admin/agent-test
```

### 3. 选择AI配置并开始对话

示例问题：
- "我有哪些题库？"
- "帮我查看错题"
- "显示我的学习统计"
- "给我一道Python题目"

## MCP工具列表 (12个)

| # | 工具名称 | 功能 | 主要参数 |
|---|---------|-----|---------|
| 1 | get_question_banks | 获取题库列表 | user_id, include_stats |
| 2 | get_questions | 获取题目列表 | user_id, bank_id, filters |
| 3 | get_question_detail | 获取题目详情 | user_id, question_id |
| 4 | submit_answer | 提交答案 | user_id, question_id, answer |
| 5 | get_wrong_questions | 获取错题 | user_id, bank_id |
| 6 | search_questions | 搜索题目 | user_id, query |
| 7 | get_user_statistics | 学习统计 | user_id, bank_id |
| 8 | add_favorite | 添加收藏 | user_id, question_id |
| 9 | get_favorites | 收藏列表 | user_id, bank_id |
| 10 | create_practice_session | 创建会话 | user_id, bank_id, mode |
| 11 | get_question_explanation | 获取解析 | user_id, question_id |
| 12 | mark_wrong_question_corrected | 标记订正 | user_id, question_id |

## 核心文件

### 新增文件
- `app/services/ai/agent_service.py` - Agent服务核心逻辑
- `templates/admin/agent_test.html` - Web测试界面
- `docs/AGENT_SYSTEM.md` - 本文档
- `test_agent.py` - 命令行测试脚本
- `add_agent_fields_migration.sql` - 数据库迁移

### 修改文件
- `app/main.py` - 添加MCP路由和Agent测试路由
- `app/models/ai_models.py` - 添加enable_agent和max_tool_iterations字段
- `app/api/mcp/tools.py` - 修复工具Schema的array类型
- `templates/admin/base.html` - 添加Agent测试菜单项

## Agent工作原理

```
用户问题 → AgentService → AI模型(带工具) → 工具调用检测
                ↑                                      ↓
            最终回复 ← 整合结果 ← 工具Handler ← 执行工具
```

### 工具调用循环

```python
while iteration < max_tool_iterations:
    # 1. AI分析并请求工具
    response = ai_service.chat(messages, tools)
    
    # 2. 如果完成，返回答案
    if response.finish_reason == "stop":
        return response
    
    # 3. 执行工具调用
    for tool_call in response.tool_calls:
        result = execute_tool(tool_call)
        messages.append(result)
    
    iteration += 1
```

## API端点

### GET /admin/agent-test
返回Agent测试页面HTML

### POST /admin/agent-test/chat
Agent对话API

**请求**:
```json
{
  "config_id": "uuid",
  "message": "我有哪些题库？",
  "enable_agent": true
}
```

**响应**:
```json
{
  "success": true,
  "response": "你有3个题库...",
  "tool_calls": [
    {
      "iteration": 1,
      "tool_name": "get_question_banks",
      "success": true,
      "result": {...}
    }
  ],
  "total_iterations": 1
}
```

### GET /api/mcp/tools
获取所有MCP工具定义

### POST /api/mcp/execute
直接执行MCP工具

## 配置说明

在数据库的 `ai_configs` 表中：

```sql
enable_agent BOOLEAN DEFAULT TRUE
max_tool_iterations INTEGER DEFAULT 5
```

- **enable_agent**: 控制是否启用Agent功能
- **max_tool_iterations**: 防止无限循环，建议3-10

## 测试方法

### 方法1: Web界面
访问 http://localhost:8000/admin/agent-test

### 方法2: 命令行
```bash
python test_agent.py
```

### 方法3: 直接API调用
```python
from app.services.ai.agent_service import AgentService

agent = AgentService(ai_service, qbank_db, user_id=1)
result = await agent.chat_with_tools(
    messages=[Message(role="user", content="我有哪些题库？")],
    provider="openai",
    enable_tools=True
)
```

## 示例场景

### 场景1: 简单查询
**用户**: "我有哪些题库？"
**流程**: 
1. 调用 `get_question_banks(user_id=1)`
2. 返回: "你有3个题库：Python基础、算法训练..."

### 场景2: 复杂任务（多次调用）
**用户**: "帮我找Python的错题"
**流程**:
1. 调用 `get_question_banks()` → 找到Python题库ID
2. 调用 `get_wrong_questions(bank_id="...")` → 获取错题
3. 返回: "在Python基础中，你有12道错题..."

## 故障排查

### Agent不调用工具
- 检查 `enable_agent` 是否为 True
- 确认模型支持function calling (如gpt-4, gpt-3.5-turbo)
- 查看工具描述是否清晰

### 工具调用失败
- 查看日志获取详细错误
- 检查参数类型是否正确
- 验证用户权限

### 响应慢
- 降低 `max_tool_iterations`
- 优化数据库查询
- 检查网络连接

## 安全特性

1. **权限验证**: 所有工具验证user_id
2. **迭代限制**: 防止无限循环
3. **工具白名单**: 只能调用预定义工具
4. **参数验证**: Pydantic类型检查

## 扩展开发

### 添加新工具

1. 在 `app/api/mcp/tools.py` 定义：
```python
NEW_TOOL = MCPTool(
    name="new_tool",
    description="工具描述",
    parameters=[...]
)
ALL_MCP_TOOLS.append(NEW_TOOL)
```

2. 在 `app/api/mcp/handlers.py` 实现：
```python
async def handle_new_tool(params, qbank_db):
    # 实现逻辑
    return {"success": True, "data": ...}
```

3. 注册Handler：
```python
tool_handlers["new_tool"] = handle_new_tool
```

## 版本信息

- **版本**: v1.0
- **发布日期**: 2025-11-02
- **状态**: Production Ready ✅

---

**维护**: EXAM-MASTER Team
**最后更新**: 2025-11-02
