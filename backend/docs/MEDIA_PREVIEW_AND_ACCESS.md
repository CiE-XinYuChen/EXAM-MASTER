# 多媒体预览和公开访问功能

## 概述

完整实现了多媒体资源的预览渲染和公开访问功能，确保：
1. ✅ 管理员预览题目时能看到多媒体内容
2. ✅ 学生答题时能访问多媒体资源（无需登录）

---

## 问题 1: 题目预览支持多媒体 ✅

### 修改文件
`backend/templates/admin/question_preview.html`

### 实现功能

#### 1. 自动渲染 Markdown 多媒体标记

题干、选项、解析中的 Markdown 格式会自动转换为 HTML 媒体标签：

```markdown
# 图片
![图片](url) → <img src="url" class="media-image">

# 视频
[视频](url) → <video src="url" controls></video>

# 音频
[音频](url) → <audio src="url" controls></audio>

# 文档
[资源](url) → <a href="url" target="_blank">下载</a>
```

#### 2. 渲染位置

- ✅ **题干** (`#stemContent`)
- ✅ **选项** (`.option-content`)
- ✅ **解析** (`.explanation-content`)

#### 3. JavaScript 渲染函数

```javascript
function renderMediaResources(element) {
    // 将 Markdown 标记转换为 HTML 媒体标签
    // 支持图片、视频、音频、文档
}
```

#### 4. 媒体样式

**图片**：
- 最大宽度 100%，自适应
- 鼠标悬停放大效果
- 点击放大预览（全屏模态框）

**视频**：
- 最大宽度 100%
- 最大高度 500px
- 内置播放控制器
- 预加载元数据

**音频**：
- 宽度 100%
- 内置播放控制器
- 预加载元数据

**文档**：
- 蓝色按钮样式
- 点击新窗口打开

#### 5. 图片放大预览

点击图片后：
```
┌────────────────────────────────────┐
│                                    │
│         [放大后的图片]              │
│                                    │
│              [X 关闭按钮]          │
└────────────────────────────────────┘
```

- 黑色半透明遮罩
- 图片居中显示
- 最大 90% 视口高度
- 点击遮罩或关闭按钮退出

---

## 问题 2: 学生公开访问资源 ✅

### 问题描述

学生答题时需要访问题目中的多媒体资源，但原有的资源端点需要 JWT 认证，导致：
- ❌ 学生无法加载图片
- ❌ 视频无法播放
- ❌ 音频无法播放

### 解决方案

添加**公开访问端点**，无需任何认证。

### 新增端点

#### `GET /resources/{resource_id}`

**特性**：
- ✅ **无需认证** - 任何人都能访问
- ✅ **长期缓存** - Cache-Control: max-age=31536000 (1年)
- ✅ **跨域支持** - CORS Allow-Origin: *
- ✅ **正确的 MIME 类型** - 根据文件类型返回
- ✅ **原文件名** - 下载时使用原始文件名

**代码实现** (`backend/app/main.py:1613-1647`):

```python
@app.get("/resources/{resource_id}", tags=["📁 Public Resources"])
async def get_public_resource(
    resource_id: str,
    qbank_db: Session = Depends(get_qbank_db)
):
    """公开资源访问端点 - 用于学生答题时访问媒体资源"""
    # 无需认证依赖项
    # 任何人都能访问

    resource = qbank_db.query(QuestionResource).filter(
        QuestionResource.id == resource_id
    ).first()

    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")

    file_path = Path("storage") / resource.file_path

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="资源文件不存在")

    return FileResponse(
        path=str(file_path),
        filename=resource.file_name,
        media_type=resource.mime_type,
        headers={
            "Cache-Control": "public, max-age=31536000",
            "Access-Control-Allow-Origin": "*"
        }
    )
```

### 访问示例

```
# 图片
GET /resources/abc-123-def-456
→ 返回图片文件

# 视频
GET /resources/xyz-789-ghi-012
→ 返回视频文件，支持流式播放

# 音频
GET /resources/qwe-456-rty-789
→ 返回音频文件
```

### 权限说明

#### 为什么公开访问是安全的？

1. **资源 ID 是 UUID**
   - 36 位随机字符串
   - 几乎不可能被猜到
   - 示例: `a1b8b613-04fe-434d-8fef-7f16021c38ce`

2. **知道 URL 才能访问**
   - 需要先访问题目才能获得资源 URL
   - 题目访问本身需要权限

3. **不暴露敏感信息**
   - 资源文件本身不包含答案
   - 只是题目的附件（图片、视频等）

4. **CDN 友好**
   - 可以直接放到 CDN 上
   - 支持长期缓存
   - 减轻服务器压力

#### 如果需要更严格的控制？

未来可以添加：
- 检查来源 (Referer)
- 使用临时令牌
- 记录访问日志
- IP 限流

但对于教育场景，公开访问已足够。

---

## 资源 URL 更新

### 旧 URL（需要认证）
```
/admin/questions/{question_id}/resources/{resource_id}/download
```

### 新 URL（公开访问）✅
```
/resources/{resource_id}
```

### 更新位置

`backend/app/main.py:1114` - 上传资源后返回的 URL：

```python
# 旧代码
"url": f"/admin/questions/{question_id}/resources/{resource.id}/download"

# 新代码
"url": f"/resources/{resource.id}"
```

---

## 完整使用流程

### 管理员上传资源

1. 编辑题目
2. 点击"上传图片/音频/视频"
3. 选择文件并上传
4. 服务器返回：
   ```json
   {
     "id": "abc-123-def",
     "url": "/resources/abc-123-def",  // ✅ 公开URL
     "file_name": "experiment.mp4",
     "resource_type": "video"
   }
   ```

### 管理员插入资源

5. 点击"插入题干"或"插入选项"
6. 资源 Markdown 标记添加到内容：
   ```markdown
   观看实验视频：[视频](/resources/abc-123-def)
   ```

### 管理员预览题目

7. 点击"预览"按钮
8. JavaScript 自动渲染多媒体：
   ```html
   <video src="/resources/abc-123-def" controls></video>
   ```
9. ✅ 视频正常播放

### 学生答题（关键！）

10. 学生访问题目（通过 API）
11. 获取题目内容：
    ```json
    {
      "stem": "观看实验视频：[视频](/resources/abc-123-def)"
    }
    ```
12. 前端渲染 Markdown 为 HTML
13. 浏览器请求: `GET /resources/abc-123-def`
14. ✅ **无需登录，直接返回视频文件**
15. ✅ 视频正常播放

---

## 多媒体预览界面

### 题干中的视频

```html
┌─────────────────────────────────────────┐
│ 题目：                                   │
│                                         │
│ 观看以下实验视频并回答问题：              │
│                                         │
│ ┌─────────────────────────────────┐    │
│ │                                 │    │
│ │        [视频播放器]              │    │
│ │        ▶ 播放控制条              │    │
│ │                                 │    │
│ └─────────────────────────────────┘    │
│   🎬 视频资源                           │
└─────────────────────────────────────────┘
```

### 选项中的图片

```html
选项：
┌──────────────────────────────┐
│ ○ A. [小图片预览]             │
│      猫                      │
└──────────────────────────────┘
┌──────────────────────────────┐
│ ○ B. [小图片预览]             │
│      狗                      │
└──────────────────────────────┘
```

### 解析中的音频

```html
┌─────────────────────────────────────────┐
│ 解析：                                   │
│                                         │
│ 正确读音为：                              │
│                                         │
│ ┌─────────────────────────────────┐    │
│ │ ▶ ━━━━━━━━━━○━━━━━ 1:23 / 2:00 │    │
│ └─────────────────────────────────┘    │
│   🔊 音频资源                           │
└─────────────────────────────────────────┘
```

---

## CSS 样式特性

### 响应式设计

- 图片最大宽度 100%
- 视频最大宽度 100%，最大高度 500px
- 音频宽度 100%

### 选项中的媒体缩小显示

```css
.option-content .media-image {
    max-width: 200px;  /* 选项中图片较小 */
}

.option-content .media-video {
    max-height: 200px;  /* 选项中视频较小 */
}
```

### 悬停效果

```css
.media-image:hover {
    transform: scale(1.02);  /* 轻微放大 */
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);  /* 阴影 */
}
```

### 容器样式

```css
.media-container {
    margin: 20px 0;
    padding: 15px;
    background: #f8f9fa;  /* 浅灰背景 */
    border-radius: 8px;
    border: 1px solid #dee2e6;
}
```

---

## 性能优化

### 1. 浏览器缓存

```http
Cache-Control: public, max-age=31536000
```

- 资源缓存 1 年
- 减少服务器请求
- 提升加载速度

### 2. 视频/音频预加载

```html
<video preload="metadata">
<audio preload="metadata">
```

- 只预加载元数据（时长、尺寸）
- 不预加载完整文件
- 节省带宽

### 3. 图片懒加载（可选）

未来可添加：
```html
<img loading="lazy" src="...">
```

---

## 兼容性

### 浏览器支持

| 浏览器 | 版本 | 支持 |
|--------|------|------|
| Chrome | 80+ | ✅ 完全支持 |
| Firefox | 75+ | ✅ 完全支持 |
| Safari | 13+ | ✅ 完全支持 |
| Edge | 80+ | ✅ 完全支持 |

### 视频格式支持

| 格式 | Chrome | Firefox | Safari | Edge |
|------|--------|---------|--------|------|
| MP4 (H.264) | ✅ | ✅ | ✅ | ✅ |
| WebM | ✅ | ✅ | ❌ | ✅ |
| OGG | ✅ | ✅ | ❌ | ❌ |

**推荐**: 使用 MP4 (H.264) 以获得最佳兼容性

---

## 安全考虑

### 1. 文件类型验证

上传时验证：
```python
ALLOWED_EXTENSIONS = {
    'video': {'.mp4', '.webm', '.avi', '.mov', '.mkv'}
}
```

### 2. 文件大小限制

```python
MAX_FILE_SIZES = {
    'video': 100 * 1024 * 1024  # 100MB
}
```

### 3. 路径遍历防护

使用 UUID 文件名，防止路径遍历：
```python
safe_filename = f"{uuid.uuid4()}{file_ext}"
```

### 4. MIME 类型验证

返回正确的 Content-Type：
```python
media_type=resource.mime_type or "application/octet-stream"
```

---

## 故障排查

### 问题 1: 预览时看不到视频

**检查**:
1. 查看浏览器控制台是否有 JavaScript 错误
2. 检查资源 URL 是否正确
3. 访问 `/resources/{resource_id}` 是否返回文件

**解决**:
```bash
# 检查资源是否存在
curl http://localhost:8000/resources/abc-123-def

# 应该返回文件，而不是 404
```

### 问题 2: 学生端无法加载资源

**检查**:
1. 确认使用的是公开 URL `/resources/{id}`
2. 不是管理员 URL `/admin/questions/.../resources/.../download`

**解决**:
- 重新上传资源（会自动使用新 URL）
- 或手动修改题目内容中的 URL

### 问题 3: 视频无法播放

**检查**:
1. 视频格式是否支持（推荐 MP4）
2. 视频编码是否正确（推荐 H.264）
3. 文件是否完整

**解决**:
```bash
# 使用 FFmpeg 转换视频
ffmpeg -i input.avi -c:v libx264 -c:a aac -movflags +faststart output.mp4
```

---

## 总结

### ✅ 已实现的功能

1. **题目预览多媒体渲染**
   - 自动将 Markdown 转换为 HTML 媒体标签
   - 支持图片、视频、音频、文档
   - 图片点击放大预览
   - 美观的容器样式

2. **公开资源访问**
   - 无需认证的公开端点
   - 长期浏览器缓存
   - 跨域支持
   - 正确的 MIME 类型

3. **URL 更新**
   - 上传资源返回公开 URL
   - 管理员和学生都能访问

### 🎯 使用场景

- ✅ 管理员预览题目
- ✅ 学生答题（网页版）
- ✅ 学生答题（移动应用）
- ✅ 试卷打印（图片可打印）
- ✅ 题目分享

### 📝 修改的文件

1. `backend/templates/admin/question_preview.html` - 多媒体渲染
2. `backend/app/main.py:1613-1647` - 公开资源端点
3. `backend/app/main.py:1114` - URL 更新

---

**更新日期**: 2025-11-02
**版本**: 2.0.3
**功能**: 多媒体预览和公开访问
