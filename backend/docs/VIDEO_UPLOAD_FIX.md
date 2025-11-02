# 视频上传功能修复说明

## 问题描述

前端调用了不存在的 API 路由 `/api/v2/qbank/banks/.../resources/upload`，导致 404 错误。

## 修复内容

### 修改文件：`backend/templates/admin/question_edit.html`

#### 1. **修正 API 路由**
- **旧路径**: `/api/v2/qbank/banks/${bankId}/resources/upload?question_id=${questionId}`
- **新路径**: `/api/v1/qbank/resources/upload`

#### 2. **添加必需的 Form 参数**
```javascript
formData.append('question_id', questionId);
```

#### 3. **修正响应字段名**
- `resource.type` → `resource.resource_type`
- `resource.filename` → `resource.file_name`

## 现在可以使用的完整功能

### 上传资源
- **端点**: `POST /api/v1/qbank/resources/upload`
- **参数**:
  - `file`: UploadFile (必需)
  - `question_id`: str (必需)
  - `option_id`: str (可选)
  - `description`: str (可选)

### 支持的文件类型
```python
ALLOWED_EXTENSIONS = {
    'image': {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.bmp'},
    'video': {'.mp4', '.webm', '.avi', '.mov', '.mkv'},  # ✅ 视频支持
    'audio': {'.mp3', '.wav', '.ogg', '.m4a', '.flac'},
    'document': {'.pdf', '.doc', '.docx', '.txt', '.tex', '.md'}
}
```

### 文件大小限制
```python
MAX_FILE_SIZES = {
    'image': 10 * 1024 * 1024,      # 10MB
    'video': 100 * 1024 * 1024,     # 100MB  ✅
    'audio': 20 * 1024 * 1024,      # 20MB
    'document': 20 * 1024 * 1024    # 20MB
}
```

## 测试步骤

1. **重启应用**（如果正在运行）
   ```bash
   # 停止当前运行的服务器
   # 重新启动
   cd backend
   python run.py
   ```

2. **访问管理后台**
   ```
   http://localhost:8000/admin
   ```

3. **编辑一道题目**
   - 进入题库管理
   - 选择或创建一道题目
   - 点击"编辑"

4. **上传视频**
   - 点击"上传图片/音频/视频"按钮
   - 选择一个视频文件（推荐 .mp4 格式）
   - 点击"上传"

5. **验证上传成功**
   - 资源列表中应该显示视频预览播放器
   - 可以直接播放视频
   - 显示文件名和文件大小
   - 点击"插入题干"可以将视频添加到题目中

## API 响应示例

```json
{
  "id": "abc-123-def",
  "resource_type": "video",
  "file_name": "experiment.mp4",
  "file_path": "video/bank_id/abc-123-def.mp4",
  "file_size": 5242880,
  "mime_type": "video/mp4",
  "created_at": "2025-11-02T08:55:21",
  "url": "/api/v1/qbank/resources/abc-123-def/download"
}
```

## 预期结果

### ✅ 成功上传
- HTTP 状态码: `201 Created`
- 返回资源对象 JSON
- 前端显示视频预览播放器

### ❌ 常见错误

#### 1. 文件类型不支持
```json
{
  "detail": "File type not allowed. Allowed extensions: .mp4, .webm, ..."
}
```
**解决**: 使用支持的视频格式

#### 2. 文件太大
```json
{
  "detail": "File too large. Maximum size for video is 100MB"
}
```
**解决**: 压缩视频或修改 `MAX_FILE_SIZES['video']` 限制

#### 3. 未授权
```json
{
  "detail": "Not authenticated"
}
```
**解决**: 确保已登录管理后台

#### 4. 无权限
```json
{
  "detail": "No permission to modify this question"
}
```
**解决**: 确保当前用户有题库的写入权限

## 故障排查

### 检查日志
如果上传仍然失败，查看服务器日志：
```bash
# 日志会显示详细的错误信息
# 包括文件验证、权限检查等
```

### 检查存储目录
确保存储目录存在且有写入权限：
```bash
ls -la backend/storage/
```

应该看到：
```
storage/
├── question_banks/
├── resources/
└── uploads/
    └── temp/
```

### 检查数据库
确认题目和题库存在：
```sql
SELECT id, bank_id FROM questions WHERE id = 'your-question-id';
```

## 相关文件

- **前端模板**: `backend/templates/admin/question_edit.html`
- **API 路由**: `backend/app/api/v1/qbank/resources.py`
- **数据模型**: `backend/app/models/question_models.py`
- **验证逻辑**: `resources.py` 中的 `validate_file()` 函数

## 完成修复的功能

- [x] 修正 API 路由路径
- [x] 添加必需的 form 参数
- [x] 修正响应字段映射
- [x] 视频预览播放器
- [x] 文件大小显示
- [x] 多文件上传支持
- [x] 资源类型图标
- [x] 插入题干功能

---

**更新时间**: 2025-11-02
**修复版本**: 2.0.1
