# 自定义模型名称使用指南

## 🎯 功能概述

EXAM-MASTER AI 助手现在支持 **完全自定义的模型名称**，你可以：

✅ 从预定义列表中快速选择常用模型
✅ 手动输入任意模型名称（支持各种新模型）
✅ 在两种输入方式之间自由切换
✅ 编辑时自动识别模型名称来源

---

## 📋 支持的提供商和模型

### OpenAI
**预定义模型**（可从下拉列表选择）:
- `gpt-4` - GPT-4 最强大
- `gpt-4-turbo` - GPT-4 Turbo 更快
- `gpt-4-turbo-preview` - GPT-4 Turbo Preview
- `gpt-3.5-turbo` - GPT-3.5 Turbo 快速经济
- `gpt-3.5-turbo-16k` - GPT-3.5 Turbo 16K 长上下文

**自定义示例**:
- `gpt-4-1106-preview` - 最新的 GPT-4 Turbo
- `gpt-4-0125-preview` - 2024年1月版本
- `gpt-4-vision-preview` - 支持视觉
- `gpt-3.5-turbo-0125` - 特定日期版本

### Anthropic Claude
**预定义模型**:
- `claude-3-opus-20240229` - Claude 3 Opus 最强大
- `claude-3-sonnet-20240229` - Claude 3 Sonnet 平衡
- `claude-3-haiku-20240307` - Claude 3 Haiku 快速
- `claude-2.1` - Claude 2.1
- `claude-2.0` - Claude 2.0

**自定义示例**:
- `claude-3-5-sonnet-20240620` - Claude 3.5 Sonnet（最新）
- `claude-instant-1.2` - Claude Instant
- `claude-3-opus-20240229-vertex` - Vertex AI 版本

### 智谱 AI (GLM)
**预定义模型**:
- `glm-4` - GLM-4 最新
- `glm-4v` - GLM-4V 视觉
- `glm-3-turbo` - GLM-3 Turbo 快速

**自定义示例**:
- `glm-4-plus` - GLM-4 Plus
- `glm-4-0520` - 特定版本
- `chatglm3-6b` - 开源版本

### 自定义提供商
支持任意第三方模型，例如：

**DeepSeek**:
- `deepseek-chat`
- `deepseek-coder`

**通义千问 (Qwen)**:
- `qwen-turbo`
- `qwen-plus`
- `qwen-max`

**Moonshot (月之暗面)**:
- `moonshot-v1-8k`
- `moonshot-v1-32k`
- `moonshot-v1-128k`

**百川 (Baichuan)**:
- `baichuan2-turbo`
- `baichuan2-53b`

**其他**:
- `llama-2-70b`
- `mixtral-8x7b`
- `yi-34b-chat`

---

## 🖥️ 使用方法

### 方式 1：通过管理后台创建配置

1. **登录管理后台**
   ```
   http://localhost:8000/admin
   ```

2. **进入 AI 配置页面**
   - 点击侧边栏 "AI 助手"
   - 点击 "新建配置"

3. **填写基本信息**
   - 配置名称：如 "Claude 3.5 Sonnet 配置"
   - 描述：可选

4. **选择提供商**
   - OpenAI / Claude / 智谱AI / 自定义

5. **输入模型名称**

   **选项 A：从列表选择（推荐新手）**
   - 选中 "从列表选择" 选项
   - 从下拉列表中选择预定义模型

   **选项 B：自定义输入（高级用户）**
   - 选中 "自定义输入" 选项
   - 手动输入模型名称
   - 示例：`claude-3-5-sonnet-20240620`

6. **输入 API 密钥**

7. **调整参数（可选）**
   - Temperature: 0.7（默认）
   - Max Tokens: 2000（默认）
   - Top P: 1.0（默认）

8. **保存配置**

### 方式 2：通过 API 创建配置

```bash
curl -X POST http://localhost:8000/api/v1/ai-chat/configs \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Claude 3.5 Sonnet 配置",
    "provider": "claude",
    "model_name": "claude-3-5-sonnet-20240620",
    "api_key": "sk-ant-your-api-key",
    "temperature": 0.7,
    "max_tokens": 4000,
    "is_default": true,
    "description": "使用最新的 Claude 3.5 Sonnet 模型"
  }'
```

---

## 📝 实际使用案例

### 案例 1：使用最新的 OpenAI 模型

```python
# 创建配置使用最新的 GPT-4 Turbo
config_data = {
    "name": "GPT-4 Turbo 最新版",
    "provider": "openai",
    "model_name": "gpt-4-0125-preview",  # 自定义输入
    "api_key": "sk-your-openai-key",
    "temperature": 0.8,
    "max_tokens": 4000
}
```

### 案例 2：使用 Claude 3.5

```python
# Claude 3.5 在列表中没有，需要自定义输入
config_data = {
    "name": "Claude 3.5 Sonnet",
    "provider": "claude",
    "model_name": "claude-3-5-sonnet-20240620",
    "api_key": "sk-ant-your-key",
    "temperature": 0.7,
    "max_tokens": 8000
}
```

### 案例 3：使用国产模型 DeepSeek

```python
# 使用自定义提供商
config_data = {
    "name": "DeepSeek Chat",
    "provider": "custom",
    "model_name": "deepseek-chat",
    "api_key": "your-deepseek-key",
    "base_url": "https://api.deepseek.com/v1",
    "temperature": 0.7,
    "max_tokens": 2000
}
```

### 案例 4：使用 Moonshot（月之暗面）

```python
config_data = {
    "name": "Moonshot 128K",
    "provider": "custom",
    "model_name": "moonshot-v1-128k",
    "api_key": "your-moonshot-key",
    "base_url": "https://api.moonshot.cn/v1",
    "temperature": 0.3,
    "max_tokens": 1000
}
```

### 案例 5：使用通义千问

```python
config_data = {
    "name": "通义千问 Max",
    "provider": "custom",
    "model_name": "qwen-max",
    "api_key": "your-qwen-key",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "temperature": 0.7,
    "max_tokens": 2000
}
```

---

## 🔧 编辑现有配置

### 行为说明

1. **模型在预定义列表中**
   - 自动选择 "从列表选择"
   - 下拉列表自动定位到该模型

2. **模型不在预定义列表中**
   - 自动切换到 "自定义输入"
   - 输入框显示当前模型名称

3. **自定义提供商**
   - 始终使用 "自定义输入"
   - 不显示下拉列表

### 示例

假设你之前创建了一个配置：
- 提供商：OpenAI
- 模型：`gpt-4-vision-preview`（不在列表中）

当你编辑这个配置时：
- ✅ 自动识别模型不在列表中
- ✅ 自动切换到"自定义输入"模式
- ✅ 输入框自动填充 `gpt-4-vision-preview`

---

## ⚠️ 注意事项

### 模型名称格式

✅ **支持的格式**:
- 字母、数字、连字符：`gpt-4-turbo`
- 下划线：`claude_3_opus`
- 点号：`model.v1`
- 特殊符号：`model@latest`
- 中文：`模型-名称`

❌ **限制**:
- 最大长度：100 个字符
- 不能为空

### API 兼容性

确保你输入的模型名称与 API 提供商兼容：

1. **OpenAI API**
   - 使用官方模型名称
   - 参考：https://platform.openai.com/docs/models

2. **Claude API**
   - 使用完整的模型标识符
   - 参考：https://docs.anthropic.com/claude/docs/models-overview

3. **自定义 API**
   - 查看提供商文档
   - 确认模型名称拼写正确

### 成本考虑

不同模型有不同的价格：

| 模型 | 成本 | 适用场景 |
|------|------|---------|
| GPT-4 | 高 | 复杂任务、高质量输出 |
| GPT-4 Turbo | 中高 | 平衡性能和成本 |
| GPT-3.5 Turbo | 低 | 简单任务、高频调用 |
| Claude 3 Opus | 高 | 最复杂的推理 |
| Claude 3 Sonnet | 中 | 日常使用 |
| Claude 3 Haiku | 低 | 快速响应 |
| 国产模型 | 低 | 成本敏感场景 |

---

## 🧪 测试配置

创建配置后，建议测试：

```bash
# 1. 创建测试会话
curl -X POST http://localhost:8000/api/v1/ai-chat/sessions \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ai_config_id": "your-config-id",
    "mode": "question"
  }'

# 2. 发送测试消息
curl -X POST http://localhost:8000/api/v1/ai-chat/sessions/SESSION_ID/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "你好，请做个自我介绍。"
  }'
```

如果收到正常回复，说明配置正确！

---

## 📚 常见问题

### Q1: 我输入的模型名称系统不认识怎么办？
**A**: 只要 API 提供商支持该模型，系统就会正常工作。系统不会验证模型名称的有效性，而是直接传递给 API。

### Q2: 能否使用本地部署的模型？
**A**: 可以！选择"自定义"提供商，填写本地 API 地址和模型名称即可。

### Q3: 如何知道某个模型是否支持？
**A**: 查看 API 提供商的官方文档，或者直接测试。

### Q4: 模型列表会更新吗？
**A**: 预定义列表会定期更新，但你可以随时使用自定义输入添加新模型。

### Q5: 切换到自定义输入后能否切回列表选择？
**A**: 可以！两种方式可以随时切换。

---

## 🎉 总结

自定义模型名称功能让 EXAM-MASTER 能够：

✅ **灵活性** - 支持任意模型
✅ **易用性** - 常用模型快速选择
✅ **前瞻性** - 新模型无需等待更新
✅ **兼容性** - 支持所有 OpenAI 兼容 API

开始使用吧！🚀
