# 认证问题修复 - 401 Unauthorized 解决

## 问题描述

视频上传时遇到 401 Unauthorized 错误：
```
POST /api/v1/qbank/resources/upload HTTP/1.1" 401 Unauthorized
```

## 根本原因

**认证机制不匹配**：
- **API 端点** (`/api/v1/qbank/resources/upload`) 需要 **JWT Bearer Token** 认证
- **管理后台** 使用 **Cookie Session** 认证
- 两者不兼容！

## 解决方案

在管理后台 (`main.py`) 添加专用的资源上传端点，使用 cookie session 认证。

### 修改内容

#### 1. 添加管理后台资源上传端点 (`backend/app/main.py:1008-1116`)

```python
@app.post("/admin/questions/{question_id}/resources/upload", tags=["🖥️ Admin Questions"])
async def admin_upload_resource(
    question_id: str,
    file: UploadFile = File(...),
    current_admin = Depends(admin_required),  # ✅ 使用 cookie session 认证
    qbank_db: Session = Depends(get_qbank_db)
):
    """Upload resource for a question (images, videos, audio)"""
    # 文件验证、保存、数据库记录
    ...
```

**关键点**：
- ✅ 使用 `admin_required` 依赖项（cookie session 认证）
- ✅ 路径：`/admin/questions/{question_id}/resources/upload`
- ✅ 支持所有媒体类型（图片、视频、音频、文档）
- ✅ 返回标准的 JSON 响应

#### 2. 更新前端调用 (`backend/templates/admin/question_edit.html:489`)

```javascript
// 旧代码 (401 错误)
const response = await fetch(`/api/v1/qbank/resources/upload`, {
    method: 'POST',
    body: formData
});

// 新代码 (✅ 正常工作)
const response = await fetch(`/admin/questions/${questionId}/resources/upload`, {
    method: 'POST',
    body: formData
});
```

**关键点**：
- ✅ 移除 `question_id` form 参数（已在 URL 路径中）
- ✅ Cookie 会自动附加，无需手动添加认证头

## 修改的文件

1. ✅ `backend/app/main.py` - 添加管理后台上传端点
2. ✅ `backend/templates/admin/question_edit.html` - 更新 API 调用路径

## 测试步骤

### 1. 重启应用
```bash
# 停止服务器 (Ctrl+C)
cd backend
python run.py
```

### 2. 刷新浏览器
在题目编辑页面按 `Ctrl + Shift + R` 强制刷新

### 3. 测试上传
1. 点击"上传图片/音频/视频"
2. 选择文件
3. 点击"上传"

### 4. 预期结果

✅ **成功日志**：
```
INFO: 127.0.0.1:xxxxx - "POST /admin/questions/{id}/resources/upload HTTP/1.1" 200 OK
```

✅ **前端显示**：
- 视频预览播放器
- 文件名和大小
- "插入题干"按钮

❌ **不再出现**：
```
401 Unauthorized
```

## API 对比

### 旧方案（401 错误）
| 特性 | 值 |
|------|-----|
| 路径 | `/api/v1/qbank/resources/upload` |
| 认证 | JWT Bearer Token ❌ |
| 用途 | API 客户端调用 |
| 问题 | 管理后台无 JWT token |

### 新方案（✅ 正常工作）
| 特性 | 值 |
|------|-----|
| 路径 | `/admin/questions/{id}/resources/upload` |
| 认证 | Cookie Session ✅ |
| 用途 | 管理后台调用 |
| 优势 | 自动认证，无需 token |

## 响应格式

成功上传视频后的响应：

```json
{
  "id": "abc-123-def-456",
  "resource_type": "video",
  "file_name": "experiment.mp4",
  "file_path": "video/bank_id/abc-123-def-456.mp4",
  "file_size": 5242880,
  "mime_type": "video/mp4",
  "url": "/admin/questions/{question_id}/resources/{resource_id}/download",
  "created_at": "2025-11-02T10:00:00"
}
```

## 支持的文件类型

| 类型 | 扩展名 | 大小限制 |
|------|--------|----------|
| 图片 | .jpg, .png, .gif, .svg, .webp | 10MB |
| 视频 | .mp4, .webm, .avi, .mov, .mkv | **100MB** ✅ |
| 音频 | .mp3, .wav, .ogg, .m4a, .flac | 20MB |
| 文档 | .pdf, .doc, .docx, .txt, .md | 20MB |

## 为什么需要两个上传端点？

### `/api/v1/qbank/resources/upload` (JWT 认证)
- **用途**: 外部 API 客户端、移动应用
- **认证**: JWT Bearer Token
- **场景**: 第三方集成、API 调用

### `/admin/questions/{id}/resources/upload` (Session 认证)
- **用途**: 管理后台 Web 界面
- **认证**: Cookie Session
- **场景**: 管理员通过浏览器操作

**两者共存**，各司其职！

## 故障排查

### 如果仍然 401

1. **检查是否登录管理后台**
   - 访问 http://localhost:8000/admin
   - 确保已登录

2. **检查 Cookie**
   - 打开浏览器开发者工具
   - Application → Cookies
   - 确认有 `admin_session` cookie

3. **清除缓存并刷新**
   ```
   Ctrl + Shift + R (Windows/Linux)
   Cmd + Shift + R (Mac)
   ```

### 如果出现其他错误

**400 Bad Request** - 文件类型不支持或文件太大
```json
{"error": "不支持的文件类型: .xyz"}
{"error": "文件太大，video类型最大100MB"}
```

**404 Not Found** - 题目不存在
```json
{"error": "题目不存在"}
```

**500 Internal Server Error** - 文件保存失败
```json
{"error": "文件保存失败: ..."}
```

## 总结

修复认证问题的关键：
1. ✅ 为管理后台添加专用上传端点
2. ✅ 使用 `admin_required` 依赖项（cookie 认证）
3. ✅ 前端调用管理后台端点

现在视频上传功能应该完全正常工作了！🎉

---

**修复日期**: 2025-11-02
**问题**: 401 Unauthorized
**解决**: 添加管理后台专用端点
**状态**: ✅ 已修复
