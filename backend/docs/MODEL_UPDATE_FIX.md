# 模型配置更新问题修复

## 🐛 问题描述

**症状**: 在管理后台编辑AI配置时，修改模型名称后保存，但修改没有生效。

**报告**:
```
我修改这个模型，但没有生效
```

---

## 🔍 根本原因

后端编辑路由 (`/admin/ai-configs/{config_id}/edit`) 中：

1. ❌ **缺少 `model_name` 参数接收**
   - 表单提交了 `model_name` 字段
   - 但后端函数参数列表中没有接收它

2. ❌ **缺少 `model_name` 更新逻辑**
   - 即使接收到了值，也没有将其更新到数据库

### 原代码 (app/main.py:1459-1503)

```python
@app.post("/admin/ai-configs/{config_id}/edit")
async def admin_ai_configs_edit(
    request: Request,
    config_id: str,
    name: str = Form(...),
    # ❌ 缺少 model_name 参数
    api_key: Optional[str] = Form(None),
    base_url: Optional[str] = Form(None),
    temperature: float = Form(0.7),
    max_tokens: int = Form(2000),
    top_p: float = Form(1.0),
    is_default: bool = Form(False),
    description: Optional[str] = Form(None),
    ...
):
    ...
    # Update config
    config.name = name
    # ❌ 缺少 model_name 更新
    if api_key and api_key != "••••••••":
        config.api_key = api_key
    config.base_url = base_url
    ...
```

---

## ✅ 修复方案

### 修改1: 添加 model_name 参数

```python
@app.post("/admin/ai-configs/{config_id}/edit")
async def admin_ai_configs_edit(
    request: Request,
    config_id: str,
    name: str = Form(...),
    model_name: str = Form(...),  # ✅ 添加此行
    api_key: Optional[str] = Form(None),
    base_url: Optional[str] = Form(None),
    ...
):
```

**位置**: `app/main.py:1464`

### 修改2: 添加 model_name 更新逻辑

```python
    # Update config
    config.name = name
    config.model_name = model_name  # ✅ 添加此行
    if api_key and api_key != "••••••••":
        config.api_key = api_key
    config.base_url = base_url
    ...
```

**位置**: `app/main.py:1495`

---

## 🧪 测试验证

### 测试步骤

1. **访问AI配置列表**:
   ```
   http://localhost:8000/admin/ai-configs
   ```

2. **编辑现有配置**:
   - 点击某个配置的 "编辑" 按钮
   - 修改 "模型名称" 字段（例如从 `gpt-4` 改为 `gpt-4-turbo`）
   - 点击 "保存配置"

3. **验证更新**:
   - 返回AI配置列表
   - 确认模型名称已更新

### 预期结果

✅ 模型名称应该成功更新
✅ 页面重定向到配置列表
✅ 列表中显示新的模型名称

---

## 📝 受影响的文件

| 文件 | 修改内容 | 行号 |
|------|---------|------|
| `app/main.py` | 添加 model_name 参数 | 1464 |
| `app/main.py` | 添加 model_name 更新逻辑 | 1495 |

---

## 🔄 完整的更新流程

### 前端表单提交

```html
<form method="post">
    <input name="name" value="配置名称" />
    <input name="model_name" value="gpt-4-turbo" />  <!-- ✅ 表单字段 -->
    <input name="api_key" value="..." />
    <input name="base_url" value="..." />
    ...
    <button type="submit">保存配置</button>
</form>
```

### 后端接收和处理

```python
@app.post("/admin/ai-configs/{config_id}/edit")
async def admin_ai_configs_edit(
    name: str = Form(...),           # ✅ 接收配置名称
    model_name: str = Form(...),     # ✅ 接收模型名称
    api_key: Optional[str] = Form(None),
    ...
):
    config.name = name               # ✅ 更新配置名称
    config.model_name = model_name   # ✅ 更新模型名称
    config.api_key = api_key         # ✅ 更新API密钥
    ...
    main_db.commit()                 # ✅ 提交到数据库
```

---

## 🎯 其他相关问题

### 激活码页面401错误

**错误信息**:
```
GET http://127.0.0.1:8000/api/v1/activation/admin/codes?skip=0&limit=20 401 (Unauthorized)
```

**原因**: 激活码页面使用 `localStorage.getItem('token')` 获取认证token，但管理后台使用session认证，不使用token。

**临时解决方案**:
1. 使用管理员账号登录
2. 确保session有效
3. 或者修改激活码页面的认证方式

**详细修复**: 需要单独的工作任务

---

## ✅ 修复状态

- [x] 诊断问题
- [x] 添加 model_name 参数
- [x] 添加 model_name 更新逻辑
- [x] 创建修复文档
- [ ] 用户验证修复

---

## 📞 如何验证修复

### 快速测试

```bash
# 1. 确保服务器已重启（加载新代码）
# 服务器应该自动重新加载 (uvicorn --reload)

# 2. 访问管理后台
open http://localhost:8000/admin/ai-configs

# 3. 编辑任意配置，修改模型名称
# 4. 保存并验证更新是否生效
```

### Python测试脚本

```python
import requests

# 假设已经登录并有session cookie
response = requests.post(
    'http://localhost:8000/admin/ai-configs/{config_id}/edit',
    data={
        'name': '测试配置',
        'model_name': 'gpt-4-turbo',  # ✅ 新的模型名称
        'api_key': 'sk-test-key',
        'base_url': 'https://api.example.com/v1',
        'temperature': 0.7,
        'max_tokens': 2000,
        'top_p': 1.0,
        'is_default': False,
        'description': '测试描述'
    },
    cookies={'session': 'your-session-cookie'}
)

print(f"状态码: {response.status_code}")
print(f"重定向到: {response.url}")
```

---

## 📚 相关文档

- `AI_TESTING_FEATURES.md` - AI配置测试功能文档
- `CONSOLE_TEST_401_FIX.md` - API令牌401错误修复
- `SESSION_SUMMARY.md` - 工作会话总结

---

**修复时间**: 2025-11-02
**修复状态**: ✅ 完成
**需要重启**: ✅ 是 (uvicorn应自动重载)
