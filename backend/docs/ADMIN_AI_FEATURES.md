# AI 助手管理功能文档

## 功能概览

EXAM-MASTER 系统现已集成完整的 AI 助手管理功能，包括：

### 1. AI 配置管理
- **多提供商支持**：OpenAI、Claude、智谱AI (GLM)、自定义
- **模型选择**：支持各提供商的主流模型
- **参数调优**：Temperature、Max Tokens、Top P 等参数可配置
- **API 密钥管理**：安全存储（TODO: 加密）
- **默认配置**：每个用户可设置一个默认配置

### 2. 聊天会话管理
- **会话模式**：
  - `practice`: 答题练习模式
  - `review`: 复习模式
  - `question`: 问答模式
- **消息记录**：完整的对话历史
- **Token 统计**：实时跟踪 token 消耗
- **工具调用**：支持 MCP 工具集成

### 3. MCP 工具集成
- **12 个标准化工具**：
  - 获取题库列表
  - 获取题目
  - 提交答案
  - 管理错题
  - 管理收藏
  - 查看统计
  - 搜索题目
  - 练习会话管理
  - 等等...

### 4. 管理面板功能
- **AI 配置列表**：查看所有 AI 配置
- **创建/编辑配置**：可视化配置表单
- **会话监控**：查看所有聊天会话
- **消息详情**：查看完整对话历史
- **统计信息**：配置数、会话数、消息数、Token 消耗

---

## 页面结构

### 1. 仪表盘 (`/admin`)
新增统计卡片：
- **AI配置**：显示总配置数
- **AI会话**：显示总会话数

新增快速操作：
- **AI助手配置**：直达 AI 配置管理页面

### 2. AI 配置管理 (`/admin/ai-configs`)

#### 统计卡片
- 总配置数
- 活跃会话数
- 总消息数
- 总 Tokens 消耗

#### AI 配置列表
显示所有 AI 配置，包括：
- 配置名称和描述
- 用户信息
- 提供商和模型
- 参数（Temperature、Max Tokens）
- 是否默认配置
- 创建时间
- 操作按钮（编辑、删除）

#### 最近聊天会话
显示最近 10 个会话：
- 会话 ID（缩略）
- 用户信息
- 使用的配置
- 会话模式
- 消息数和 Token 数
- 最后活动时间
- 查看详情按钮

### 3. 创建/编辑 AI 配置 (`/admin/ai-configs/create`, `/admin/ai-configs/{id}/edit`)

#### 基本信息
- 配置名称
- 描述（可选）

#### AI 提供商
- 选择提供商（OpenAI/Claude/智谱AI/自定义）
- 选择模型（根据提供商动态更新）
- API 密钥
- 自定义 API 地址（可选）

#### 模型参数
- **Temperature** (0.0-2.0)
  - 控制输出随机性
  - 默认 0.7
- **Max Tokens** (1-32000)
  - 单次回复最大长度
  - 默认 2000
- **Top P** (0.0-1.0)
  - 控制输出多样性
  - 默认 1.0
- **是否默认配置**
  - 每个用户只能有一个默认配置

### 4. 会话详情 (`/admin/ai-sessions/{id}`)

#### 会话信息
- 会话 ID
- 用户信息
- 使用的 AI 配置
- 会话模式
- 题库 ID（如果有）
- 系统提示词
- 总消息数
- 总 Tokens
- 开始时间和最后活动时间

#### 对话消息
完整的对话历史，包括：
- **用户消息**：蓝色背景
- **AI 回复**：紫色背景
- **系统消息**：橙色背景
- **工具调用**：绿色背景

每条消息显示：
- 角色（用户/AI/系统/工具）
- 消息内容
- 时间戳
- Token 消耗
- 工具调用详情（如果有）

---

## API 端点

### Web 管理界面

```
GET    /admin/ai-configs                    # AI 配置列表
GET    /admin/ai-configs/create             # 创建配置表单
POST   /admin/ai-configs/create             # 创建配置
GET    /admin/ai-configs/{id}/edit          # 编辑配置表单
POST   /admin/ai-configs/{id}/edit          # 更新配置
POST   /admin/ai-configs/{id}/delete        # 删除配置
GET    /admin/ai-sessions/{id}              # 会话详情
POST   /admin/ai-sessions/{id}/delete       # 删除会话
```

### REST API

```
# AI 配置管理
POST   /api/v1/ai-chat/configs              # 创建配置
GET    /api/v1/ai-chat/configs              # 列出配置
GET    /api/v1/ai-chat/configs/{id}         # 获取配置
PUT    /api/v1/ai-chat/configs/{id}         # 更新配置
DELETE /api/v1/ai-chat/configs/{id}         # 删除配置

# 聊天会话管理
POST   /api/v1/ai-chat/sessions             # 创建会话
GET    /api/v1/ai-chat/sessions             # 列出会话
GET    /api/v1/ai-chat/sessions/{id}        # 获取会话
DELETE /api/v1/ai-chat/sessions/{id}        # 删除会话

# 对话
GET    /api/v1/ai-chat/sessions/{id}/messages   # 获取消息历史
POST   /api/v1/ai-chat/sessions/{id}/chat       # 发送消息并获取回复

# 统计
GET    /api/v1/ai-chat/usage/report         # 使用统计报告

# MCP 工具
GET    /api/v1/mcp/tools                    # 获取所有工具
GET    /api/v1/mcp/tools/{name}             # 获取特定工具
POST   /api/v1/mcp/execute                  # 执行工具
POST   /api/v1/mcp/batch                    # 批量执行工具
GET    /api/v1/mcp/categories               # 获取工具分类
```

---

## 数据库表结构

### ai_configs
AI 配置表，存储用户的 AI 模型配置

| 字段 | 类型 | 说明 |
|------|------|------|
| id | String(36) | 主键，UUID |
| user_id | Integer | 用户 ID（外键） |
| name | String(100) | 配置名称 |
| provider | String(20) | 提供商（openai/claude/zhipu/custom） |
| model_name | String(50) | 模型名称 |
| api_key | Text | API 密钥（TODO: 加密） |
| base_url | String(200) | 自定义 API 地址 |
| temperature | Float | Temperature 参数 |
| max_tokens | Integer | 最大 Token 数 |
| top_p | Float | Top P 参数 |
| is_default | Boolean | 是否默认配置 |
| description | String(500) | 配置描述 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### chat_sessions
聊天会话表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | String(36) | 主键，UUID |
| user_id | Integer | 用户 ID（外键） |
| ai_config_id | String(36) | AI 配置 ID（外键） |
| bank_id | String(36) | 题库 ID（跨库引用） |
| mode | String(20) | 会话模式（practice/review/question） |
| system_prompt | Text | 系统提示词 |
| total_messages | Integer | 总消息数 |
| total_tokens | Integer | 总 Token 数 |
| started_at | DateTime | 开始时间 |
| last_activity_at | DateTime | 最后活动时间 |

### chat_messages
对话消息表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | String(36) | 主键，UUID |
| session_id | String(36) | 会话 ID（外键） |
| role | String(20) | 角色（system/user/assistant/tool） |
| content | Text | 消息内容 |
| tool_calls | JSON | 工具调用列表 |
| tool_call_id | String(100) | 工具调用 ID |
| tokens | Integer | 该消息的 Token 数 |
| created_at | DateTime | 创建时间 |

---

## 使用示例

### 1. 创建 AI 配置

通过管理后台：
1. 访问 `/admin/ai-configs`
2. 点击"新建配置"
3. 填写配置信息：
   - 名称：如 "我的 GPT-4 配置"
   - 提供商：选择 OpenAI
   - 模型：选择 GPT-4
   - API 密钥：输入你的 OpenAI API Key
   - 调整参数（可选）
4. 保存配置

### 2. 使用 API 创建会话

```python
import requests

# 创建会话
response = requests.post(
    "http://localhost:8000/api/v1/ai-chat/sessions",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={
        "ai_config_id": "your-config-id",
        "mode": "question",
        "system_prompt": "你是一个友好的学习助手。"
    }
)

session = response.json()
session_id = session["id"]
```

### 3. 发送消息并获取回复

```python
# 发送消息
response = requests.post(
    f"http://localhost:8000/api/v1/ai-chat/sessions/{session_id}/chat",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={
        "content": "你好！"
    }
)

reply = response.json()
print(reply["content"])  # AI 的回复
```

### 4. AI 自动调用工具

当 AI 需要获取题目时，会自动调用 MCP 工具：

```python
# 用户问：给我一道题
response = requests.post(
    f"http://localhost:8000/api/v1/ai-chat/sessions/{session_id}/chat",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={
        "content": "从题库中给我一道题"
    }
)

# AI 会自动：
# 1. 调用 get_question_banks 工具获取题库
# 2. 调用 get_questions 工具获取题目
# 3. 将题目内容返回给用户
```

---

## 测试功能

运行测试脚本：

```bash
python test_ai_api.py
```

测试包括：
1. ✅ AI 配置 CRUD 操作
2. ✅ 聊天会话创建和消息管理
3. ✅ MCP 工具可用性
4. ✅ 使用统计

---

## 待完成功能

### 高优先级
- [ ] **API 密钥加密**：当前 API 密钥明文存储，需要加密
- [ ] **流式响应**：实现 `/sessions/{id}/stream` 端点
- [ ] **使用配额**：限制每个用户的 token 使用量
- [ ] **错误处理**：更详细的错误信息和重试机制

### 中优先级
- [ ] **对话导出**：导出会话历史为 PDF/JSON
- [ ] **统计图表**：可视化 token 使用趋势
- [ ] **模板库**：预设的系统提示词模板
- [ ] **批量操作**：批量删除会话/配置

### 低优先级
- [ ] **会话搜索**：按关键词搜索对话内容
- [ ] **会话标签**：为会话添加标签分类
- [ ] **会话分享**：生成分享链接
- [ ] **API 使用分析**：按时间、用户、模型统计

---

## 安全建议

1. **API 密钥安全**：
   - 尽快实现加密存储
   - 考虑使用环境变量或密钥管理服务
   - 定期轮换密钥

2. **访问控制**：
   - 验证用户只能访问自己的配置和会话
   - 管理员可以查看所有配置（已实现）

3. **输入验证**：
   - 验证 API 密钥格式
   - 限制参数范围（Temperature、Max Tokens 等）
   - 防止 SQL 注入和 XSS

4. **速率限制**：
   - 限制每个用户的请求频率
   - 限制 token 使用量
   - 防止滥用

---

## 技术栈

- **后端框架**：FastAPI
- **数据库**：SQLite (Main DB)
- **ORM**：SQLAlchemy
- **AI 集成**：
  - OpenAI SDK (aiohttp)
  - Anthropic Claude API (aiohttp)
  - 智谱 AI API (aiohttp)
- **前端**：Jinja2 模板 + 原生 JavaScript
- **样式**：自定义 CSS
- **图标**：Font Awesome

---

## 贡献者

开发时间：2025-11-02
版本：2.0.0

---

## 更新日志

### 2025-11-02 - Phase 2 完成
✅ AI 服务实现（OpenAI、Claude、智谱AI）
✅ AI 配置数据库模型
✅ AI 聊天 API（12 个端点）
✅ MCP 工具集成（12 个工具）
✅ 管理后台页面
✅ 仪表盘统计
✅ 完整测试套件

### 下一步：Phase 3
⏳ Flutter 移动端开发
⏳ AI 聊天界面
⏳ 题目练习界面
⏳ 配置管理界面
