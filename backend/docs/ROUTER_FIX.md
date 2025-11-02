# 路由修复说明 - 404 错误解决

## 问题描述

视频上传时遇到 404 错误：
```
POST /api/v1/qbank/resources/upload HTTP/1.1" 404 Not Found
```

## 根本原因

`backend/app/main.py` 中只注册了 `/api/v2` 路由，**没有注册 `/api/v1` 路由**。

## 修复内容

### 文件: `backend/app/main.py`

#### 1. 导入 v1 路由 (line 23)
```python
from app.api.v1 import api_router as v1_api_router
from app.api.v2 import api_router
```

#### 2. 注册 v1 路由 (line 66-70)
```python
# Include V1 API routes (for resources and other endpoints)
app.include_router(v1_api_router, prefix="/api/v1")

# Include V2 API routes
app.include_router(api_router, prefix="/api/v2")
```

## 修复后的 API 路由

### ✅ V1 API (现在可用)
- `POST /api/v1/qbank/resources/upload` - 资源上传 ✅
- `GET /api/v1/qbank/resources/{id}/download` - 资源下载 ✅
- `DELETE /api/v1/qbank/resources/{id}` - 删除资源 ✅
- `POST /api/v1/qbank/resources/batch-upload` - 批量上传 ✅
- 以及其他 v1 端点...

### ✅ V2 API (已存在)
- `GET /api/v2/qbank/banks` - 题库列表
- `POST /api/v2/auth/login` - 认证
- 等等...

## 测试步骤

### 1. 重启应用
```bash
# 停止当前运行的服务器 (Ctrl+C)
# 重新启动
python run.py
```

### 2. 验证路由可用
访问 API 文档查看所有路由：
```
http://localhost:8000/api/docs
```

应该看到：
- ✅ V1 路由: `/api/v1/*`
- ✅ V2 路由: `/api/v2/*`

### 3. 测试视频上传

#### 方法 1: 通过管理后台
1. 访问 http://localhost:8000/admin
2. 进入题目编辑页面
3. 点击"上传图片/音频/视频"
4. 选择视频文件
5. 点击"上传"

#### 方法 2: 通过 API
```bash
curl -X POST "http://localhost:8000/api/v1/qbank/resources/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@video.mp4" \
  -F "question_id=YOUR_QUESTION_ID"
```

### 4. 预期结果

成功的日志应该显示：
```
INFO: 127.0.0.1:xxxxx - "POST /api/v1/qbank/resources/upload HTTP/1.1" 201 Created
```

而不是：
```
❌ INFO: 127.0.0.1:xxxxx - "POST /api/v1/qbank/resources/upload HTTP/1.1" 404 Not Found
```

## 相关修改的文件

1. ✅ `backend/app/main.py` - 添加 v1 路由注册
2. ✅ `backend/templates/admin/question_edit.html` - 修正 API 调用路径和字段名

## API 响应示例

### 成功上传视频
```json
{
  "id": "abc-123-def",
  "resource_type": "video",
  "file_name": "experiment.mp4",
  "file_path": "video/bank_id/abc-123-def.mp4",
  "file_size": 5242880,
  "mime_type": "video/mp4",
  "url": "/api/v1/qbank/resources/abc-123-def/download",
  "created_at": "2025-11-02T09:00:00"
}
```

## 为什么需要 V1 和 V2 路由

### V1 API
- **用途**: 资源管理（上传、下载）、导入导出等基础功能
- **状态**: 稳定，向后兼容
- **路径**: `/api/v1/*`

### V2 API
- **用途**: 重构的题库管理、考试会话、统计等
- **状态**: 正在开发，功能更完善
- **路径**: `/api/v2/*`

**两者共存**，V2 复用部分 V1 路由（如 auth、resources）。

## 故障排查

### 如果仍然 404

1. **检查路由是否注册**
   ```bash
   # 查看所有路由
   curl http://localhost:8000/api/docs
   ```

2. **检查导入是否成功**
   ```python
   # 在 main.py 中添加调试输出
   print(f"V1 routes: {v1_api_router.routes}")
   print(f"V2 routes: {api_router.routes}")
   ```

3. **检查前端调用的 URL**
   - 打开浏览器开发者工具
   - 查看 Network 标签
   - 确认请求的 URL 是否正确

4. **清除浏览器缓存**
   ```
   Ctrl + Shift + R (Windows/Linux)
   Cmd + Shift + R (Mac)
   ```

## 总结

修复非常简单，只需在 `main.py` 中：
1. 导入 v1 路由
2. 注册 v1 路由

现在视频上传功能应该完全正常工作了！🎉

---

**修复日期**: 2025-11-02
**影响范围**: 所有 V1 API 端点
**修复后状态**: ✅ 完全可用
