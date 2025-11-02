# 视频支持功能文档

## 概述

EXAM-MASTER 题库系统已全面支持视频资源，可以在题目的题干、选项、解析等位置嵌入视频文件。

## 功能特性

### ✅ 已实现的功能

#### 1. 后端支持
- **数据库模型**: 完整支持视频资源类型
  - `ResourceType.video` 枚举定义
  - `QuestionBankV2.has_video` 题库级别视频标记
  - `QuestionV2.has_video` 题目级别视频标记
  - `QuestionResourceV2` 包含视频专用字段（宽度、高度、时长）

- **文件存储**:
  - 存储路径: `storage/question_banks/{bank_id}/video/{question_id}/`
  - 支持本地存储 + 云存储（S3/OSS/七牛）

- **API 端点**:
  - `POST /api/v1/qbank/resources/upload` - 视频上传
  - `GET /api/v1/qbank/resources/{resource_id}/download` - 视频下载/播放
  - `DELETE /api/v1/qbank/resources/{resource_id}` - 删除视频
  - `POST /api/v1/qbank/resources/batch-upload` - 批量上传

- **文件格式支持**:
  - `.mp4` (推荐，最佳兼容性)
  - `.webm` (Web优化格式)
  - `.avi` (传统格式)
  - `.mov` (Apple格式)
  - `.mkv` (高清视频)

- **文件大小限制**:
  - 默认: 100MB
  - 可在 `backend/app/api/v1/qbank/resources.py` 修改 `MAX_FILE_SIZES['video']`

#### 2. 前端支持（已更新）
- **文件上传**:
  - 支持通过文件选择器上传视频 (`accept="video/*"`)
  - 支持批量上传（多选）
  - 上传按钮文字更新为"上传图片/音频/视频"

- **视频预览**:
  - 资源列表中显示视频缩略图播放器
  - 支持直接在列表中播放预览
  - 显示文件名和文件大小

- **视频插入**:
  - 点击"插入题干"按钮可将视频引用插入到题目内容
  - Markdown 格式: `[视频](视频URL)`

#### 3. 元数据记录
每个视频文件会记录以下信息：
```python
{
    "resource_type": "video",
    "resource_path": "question_banks/{bank_id}/video/{question_id}/demo.mp4",
    "resource_url": "https://cdn.example.com/...",  # 可选CDN
    "file_name": "experiment_demo.mp4",
    "file_size": 52428800,  # 字节
    "mime_type": "video/mp4",
    "width": 1920,
    "height": 1080,
    "duration": 120,  # 秒
    "position": "stem",  # 题干、选项、解析等
    "alt_text": "实验演示视频",
    "caption": "牛顿第二定律实验"
}
```

## 使用方法

### 1. 通过管理后台上传视频

#### 编辑题目时上传：
1. 进入题目编辑页面
2. 找到"资源管理"卡片
3. 点击"上传图片/音频/视频"按钮
4. 选择视频文件（支持多选）
5. 点击"上传"按钮
6. 等待上传完成，视频会显示在资源列表中

#### 插入到题干：
1. 在资源列表中找到已上传的视频
2. 点击"插入题干"按钮
3. 视频引用会自动添加到题干文本框

### 2. 通过 API 上传视频

```bash
# 单个视频上传
curl -X POST "http://localhost:8000/api/v1/qbank/resources/upload" \
  -H "Authorization: Bearer {token}" \
  -F "file=@experiment.mp4" \
  -F "question_id={question_id}" \
  -F "description=实验演示视频"

# 批量上传
curl -X POST "http://localhost:8000/api/v1/qbank/resources/batch-upload" \
  -H "Authorization: Bearer {token}" \
  -F "files=@video1.mp4" \
  -F "files=@video2.mp4" \
  -F "question_id={question_id}"
```

### 3. 下载/播放视频

```bash
# 获取视频文件
curl -X GET "http://localhost:8000/api/v1/qbank/resources/{resource_id}/download" \
  -H "Authorization: Bearer {token}" \
  --output video.mp4

# 或在浏览器中直接访问（需要登录）
# http://localhost:8000/api/v1/qbank/resources/{resource_id}/download
```

### 4. 在前端渲染视频

如果题干包含视频链接 `[视频](URL)`，前端需要解析并渲染为 HTML5 video 标签：

```html
<video controls style="max-width: 100%; height: auto;">
    <source src="{VIDEO_URL}" type="video/mp4">
    您的浏览器不支持视频播放。
</video>
```

## 使用场景示例

### 1. 物理实验题
```json
{
    "stem": "观看以下实验视频，回答问题：\n[视频](/api/v1/qbank/resources/xxx/download)\n\n实验中小球的加速度约为多少？",
    "type": "single",
    "options": [
        {"label": "A", "content": "9.8 m/s²"},
        {"label": "B", "content": "4.9 m/s²"},
        {"label": "C", "content": "19.6 m/s²"}
    ]
}
```

### 2. 英语听力题（视频+音频）
```json
{
    "stem": "观看以下对话视频并回答问题：\n[视频](/api/v1/qbank/resources/xxx/download)",
    "type": "multiple",
    "explanation": "解析视频：\n[视频](/api/v1/qbank/resources/yyy/download)"
}
```

### 3. 计算机操作题
```json
{
    "stem": "观看操作演示，按照相同步骤完成任务：\n[视频](/api/v1/qbank/resources/xxx/download)",
    "type": "essay",
    "meta_data": {
        "reference_answer": "需要完成以下步骤：...",
        "scoring_rules": {...}
    }
}
```

## 技术细节

### 文件存储结构
```
storage/
└── question_banks/
    └── {bank_id}/
        └── video/
            └── {question_id}/
                ├── experiment.mp4
                ├── explanation.webm
                └── tutorial.mov
```

### 数据库表结构

#### QuestionResourceV2 表
```sql
CREATE TABLE question_resources_v2 (
    id VARCHAR(36) PRIMARY KEY,
    question_id VARCHAR(36) NOT NULL,
    resource_type ENUM('image', 'audio', 'video', 'document', 'formula'),
    resource_path VARCHAR(255) NOT NULL,
    resource_url VARCHAR(500),
    file_name VARCHAR(255),
    file_size INTEGER,
    mime_type VARCHAR(50),
    position VARCHAR(50),
    alt_text VARCHAR(255),
    caption VARCHAR(255),
    width INTEGER,
    height INTEGER,
    duration INTEGER,
    created_at DATETIME
);
```

### API 响应示例

```json
{
    "id": "abc-123-def",
    "question_id": "q_123",
    "resource_type": "video",
    "file_path": "video/bank_id/abc-123-def.mp4",
    "file_name": "experiment.mp4",
    "file_size": 52428800,
    "mime_type": "video/mp4",
    "width": 1920,
    "height": 1080,
    "duration": 120,
    "url": "/api/v1/qbank/resources/abc-123-def/download",
    "created_at": "2025-08-11T10:30:00"
}
```

## 性能优化建议

### 1. 视频压缩
- 使用 H.264 编码（最佳兼容性）
- 推荐分辨率: 720p (1280x720) 或 1080p (1920x1080)
- 推荐码率: 2-5 Mbps

### 2. CDN 加速
配置云存储和 CDN：
```python
# backend/app/core/config.py
storage_config = {
    "type": "s3",
    "bucket": "exam-master-videos",
    "region": "us-west-1",
    "cdn_url": "https://cdn.example.com"
}
```

### 3. 流式播放
- 使用 MP4 Fast Start (moov atom 在文件开头)
- 使用 FFmpeg 优化:
  ```bash
  ffmpeg -i input.mp4 -c copy -movflags +faststart output.mp4
  ```

### 4. 自适应码率（HLS/DASH）
对于长视频，建议转换为 HLS 格式：
```bash
ffmpeg -i input.mp4 \
  -c:v libx264 -c:a aac \
  -hls_time 10 -hls_playlist_type vod \
  -hls_segment_filename "segment%03d.ts" \
  playlist.m3u8
```

## 安全考虑

### 1. 文件类型验证
- 后端验证文件扩展名
- 使用 `python-magic` 验证真实文件类型（MIME）
- 防止恶意文件伪装

### 2. 文件大小限制
- 默认 100MB，可根据需求调整
- 防止磁盘空间耗尽

### 3. 访问权限控制
- 需要登录才能上传/下载
- 基于题库权限控制访问
- Admin/Teacher 可上传，Student 只能查看

### 4. 文件名安全
- 使用 UUID 生成唯一文件名
- 防止路径遍历攻击
- 防止文件名冲突

## 故障排查

### 问题1: 上传失败 "File too large"
**解决方法**: 修改文件大小限制
```python
# backend/app/api/v1/qbank/resources.py
MAX_FILE_SIZES = {
    'video': 200 * 1024 * 1024,  # 改为 200MB
}
```

### 问题2: 视频无法播放
**可能原因**:
- 浏览器不支持该视频格式 → 转换为 MP4
- 视频编码不兼容 → 使用 H.264 编码
- 文件损坏 → 重新上传

### 问题3: 上传速度慢
**解决方法**:
- 启用 Nginx 上传模块
- 配置 CDN 直传
- 使用分片上传（断点续传）

### 问题4: 存储空间不足
**解决方法**:
- 清理未使用的视频资源
- 迁移到云存储（S3/OSS）
- 启用视频压缩

## 未来改进计划

- [ ] 视频自动转码（多码率）
- [ ] 视频截图生成封面
- [ ] 视频时长/分辨率自动提取
- [ ] 字幕文件支持（.srt, .vtt）
- [ ] 视频水印添加
- [ ] 播放统计和分析
- [ ] 视频预加载策略
- [ ] 倍速播放控制
- [ ] 视频章节标记

## 相关文件

- 后端模型: `backend/app/models/question_models_v2.py`
- API 路由: `backend/app/api/v1/qbank/resources.py`
- 前端模板: `backend/templates/admin/question_edit.html`
- 配置文件: `backend/app/core/config.py`
- Schema 定义: `backend/app/schemas/question_schemas.py`

## 联系支持

如有问题或建议，请通过以下方式联系：
- GitHub Issues: https://github.com/your-repo/EXAM-MASTER/issues
- 邮箱: support@example.com

---

**更新日期**: 2025-08-11
**版本**: 2.0.0
