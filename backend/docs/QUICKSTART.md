# EXAM-MASTER AI 助手 - 快速启动指南

## 🚀 5分钟快速上手

### 1. 启动服务器

```bash
cd backend
uvicorn app.main:app --reload
```

服务器将在 `http://localhost:8000` 启动

### 2. 访问管理后台

打开浏览器访问：`http://localhost:8000/admin`

默认管理员账户：
- 用户名：`admin`
- 密码：`admin123`

### 3. 配置 AI 助手

#### 方式一：通过管理后台（推荐）

1. 登录后，点击左侧菜单 **"AI 助手"**
2. 点击 **"新建配置"** 按钮
3. 填写配置信息：

   **基本信息**
   - 配置名称：如 "我的 GPT-4 配置"
   - 描述：可选

   **AI 提供商**
   - 选择提供商：OpenAI / Claude / 智谱AI
   - 选择模型：根据提供商选择
   - API 密钥：输入你的 API Key
   - API 地址：可选（使用代理时填写）

   **模型参数**（可使用默认值）
   - Temperature: 0.7（控制随机性）
   - Max Tokens: 2000（最大长度）
   - Top P: 1.0（多样性）
   - 设为默认配置：勾选此项

4. 点击 **"保存配置"**

#### 方式二：通过 API

```bash
curl -X POST http://localhost:8000/api/v1/ai-chat/configs \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "我的OpenAI配置",
    "provider": "openai",
    "model_name": "gpt-3.5-turbo",
    "api_key": "sk-your-api-key",
    "temperature": 0.7,
    "max_tokens": 2000,
    "top_p": 1.0,
    "is_default": true
  }'
```

### 4. 创建聊天会话

```bash
curl -X POST http://localhost:8000/api/v1/ai-chat/sessions \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ai_config_id": "your-config-id",
    "mode": "question",
    "system_prompt": "你是一个友好的学习助手，帮助用户学习和答题。"
  }'
```

响应示例：
```json
{
  "id": "session-uuid",
  "user_id": 1,
  "ai_config_id": "config-uuid",
  "mode": "question",
  "total_messages": 0,
  "total_tokens": 0,
  "started_at": "2025-11-02T10:00:00",
  "last_activity_at": "2025-11-02T10:00:00"
}
```

### 5. 发送消息

```bash
curl -X POST http://localhost:8000/api/v1/ai-chat/sessions/SESSION_ID/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "你好！请给我一道编程题。"
  }'
```

AI 会自动调用 MCP 工具获取题目并回复！

---

## 📋 支持的 AI 提供商

### OpenAI
- **API Key 获取**：https://platform.openai.com/api-keys
- **支持模型**：
  - `gpt-4` - 最强大
  - `gpt-4-turbo-preview` - 更快更便宜
  - `gpt-3.5-turbo` - 快速经济
- **API 地址**：`https://api.openai.com/v1`（默认）

### Anthropic Claude
- **API Key 获取**：https://console.anthropic.com/
- **支持模型**：
  - `claude-3-opus-20240229` - 最强大
  - `claude-3-sonnet-20240229` - 平衡
  - `claude-3-haiku-20240307` - 快速
- **API 地址**：`https://api.anthropic.com/v1`（默认）

### 智谱 AI (GLM)
- **API Key 获取**：https://open.bigmodel.cn/
- **支持模型**：
  - `glm-4` - 最新
  - `glm-3-turbo` - 快速
- **API 地址**：`https://open.bigmodel.cn/api/paas/v4`（默认）

---

## 🛠️ 会话模式说明

### `practice` - 答题练习模式
AI 作为答题助手，引导用户练习题目：
- 自动获取题目
- 评估答案正确性
- 提供详细解析
- 记录答题历史

**使用场景**：日常练习、考前冲刺

### `review` - 复习模式
AI 帮助用户复习错题和收藏：
- 获取错题列表
- 讲解错题原因
- 巩固知识点
- 标记已掌握

**使用场景**：错题复习、知识巩固

### `question` - 问答模式
AI 作为通用学习助手：
- 回答学习问题
- 解释知识点
- 提供学习建议
- 自由对话

**使用场景**：自由提问、知识答疑

---

## 🎯 常见使用场景

### 场景 1：智能答题练习

```python
import requests

# 1. 创建练习会话
session = requests.post(
    "http://localhost:8000/api/v1/ai-chat/sessions",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={
        "ai_config_id": "config-id",
        "bank_id": "bank-id",  # 指定题库
        "mode": "practice"
    }
).json()

# 2. 请求题目
response = requests.post(
    f"http://localhost:8000/api/v1/ai-chat/sessions/{session['id']}/chat",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={"content": "给我一道题"}
).json()

print(response["content"])  # AI 会自动获取题目并展示

# 3. 提交答案
response = requests.post(
    f"http://localhost:8000/api/v1/ai-chat/sessions/{session['id']}/chat",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={"content": "我的答案是 A"}
).json()

print(response["content"])  # AI 会自动提交答案并给出反馈
```

### 场景 2：错题复习

```python
# 创建复习会话
session = requests.post(
    "http://localhost:8000/api/v1/ai-chat/sessions",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={
        "ai_config_id": "config-id",
        "mode": "review"
    }
).json()

# 请求错题
response = requests.post(
    f"http://localhost:8000/api/v1/ai-chat/sessions/{session['id']}/chat",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={"content": "给我看看我的错题"}
).json()

# AI 会自动调用工具获取错题列表
print(response["content"])
```

### 场景 3：知识问答

```python
# 创建问答会话
session = requests.post(
    "http://localhost:8000/api/v1/ai-chat/sessions",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={
        "ai_config_id": "config-id",
        "mode": "question",
        "system_prompt": "你是一位专业的编程导师。"
    }
).json()

# 自由提问
response = requests.post(
    f"http://localhost:8000/api/v1/ai-chat/sessions/{session['id']}/chat",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={"content": "Python 中的装饰器是什么？"}
).json()

print(response["content"])
```

---

## 📊 管理后台功能

### 仪表盘 (`/admin`)
- 查看系统整体统计
- AI 配置数量
- 活跃会话数
- 快速访问 AI 配置

### AI 配置管理 (`/admin/ai-configs`)
- 查看所有 AI 配置
- 创建新配置
- 编辑现有配置
- 删除配置
- 查看配置统计
- 查看最近会话

### 会话详情 (`/admin/ai-sessions/{id}`)
- 查看完整对话历史
- 查看 token 使用情况
- 查看工具调用记录
- 删除会话

---

## 🔧 MCP 工具说明

AI 可以自动调用以下 12 个工具：

### 题库相关
1. **get_question_banks** - 获取题库列表
2. **get_questions** - 获取题目列表
3. **get_question_detail** - 获取题目详情
4. **search_questions** - 搜索题目

### 答题相关
5. **submit_answer** - 提交答案
6. **get_question_explanation** - 获取题目解析
7. **create_practice_session** - 创建练习会话

### 错题和收藏
8. **get_wrong_questions** - 获取错题列表
9. **mark_wrong_question_corrected** - 标记错题已订正
10. **add_favorite** - 添加收藏
11. **get_favorites** - 获取收藏列表

### 统计
12. **get_user_statistics** - 获取用户统计

AI 会根据对话上下文自动选择合适的工具调用！

---

## ⚠️ 注意事项

### 安全性
- ⚠️ **API 密钥目前明文存储**，请尽快实现加密
- ✅ 用户只能访问自己的配置和会话
- 建议使用环境变量存储敏感信息

### 成本控制
- 建议为每个用户设置 token 使用配额
- 定期检查 API 使用量
- 使用成本较低的模型进行测试

### 性能优化
- 建议使用 Redis 缓存会话数据
- 定期清理过期会话
- 监控 API 响应时间

---

## 📚 更多资源

- **详细文档**：`ADMIN_AI_FEATURES.md`
- **API 文档**：`http://localhost:8000/api/docs`
- **测试套件**：`python test_ai_api.py`

---

## 🆘 故障排除

### 问题：无法创建配置
**解决方案**：
1. 检查 API 密钥格式是否正确
2. 确认提供商和模型名称匹配
3. 查看浏览器控制台错误信息

### 问题：AI 无法回复
**解决方案**：
1. 检查 API 密钥是否有效
2. 确认 API 地址是否正确
3. 查看后端日志：`tail -f logs/app.log`

### 问题：工具调用失败
**解决方案**：
1. 确认题库和题目是否存在
2. 检查用户权限
3. 查看 MCP 工具日志

---

## 🎉 开始使用

现在你已经准备好开始使用 AI 助手功能了！

1. ✅ 启动服务器
2. ✅ 登录管理后台
3. ✅ 创建 AI 配置
4. ✅ 开始对话

祝你使用愉快！🚀
