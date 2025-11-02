# 资源插入功能说明

## 修复的问题

### 1. ✅ 页面跳转问题已修复

**问题**：点击"插入题干"按钮后，页面会跳转到上一页

**原因**：按钮缺少 `type="button"` 属性，默认为 `type="submit"`，导致触发表单提交

**修复**：
- 所有按钮都添加了 `type="button"` 属性
- 所有 onclick 函数都返回 `false` 防止事件冒泡

```javascript
// 修复前 (会触发表单提交)
<button onclick="insertResourceToStem(...)">

// 修复后 (不会触发表单提交)
<button type="button" onclick="insertResourceToStem(...); return false;">
```

### 2. ✅ 新增"插入选项"功能

现在所有媒体资源（图片、视频、音频）都支持插入到选项中！

## 功能详解

### 插入题干

点击"插入题干"按钮，资源会以 Markdown 格式插入到题干文本框：

```markdown
# 图片
![图片](resource_url)

# 视频
[视频](resource_url)

# 音频
[音频](resource_url)
```

### 插入选项（新功能）⭐

点击"插入选项"按钮后：

1. **弹出选项选择菜单**
   - 显示当前题目的所有选项
   - 每个选项显示：选项标签（A、B、C...）和内容预览

2. **选择目标选项**
   - 点击要插入的选项
   - 资源会自动添加到该选项的内容中

3. **支持的题型**
   - ✅ 单选题
   - ✅ 多选题
   - ❌ 判断题（无选项）
   - ❌ 填空题（无选项）
   - ❌ 问答题（无选项）

## 界面示例

### 资源卡片

每个上传的资源都会显示：

```
┌─────────────────────────────────────────────────────────┐
│ [视频预览]  文件名.mp4                 [插入题干] [插入选项] [删除] │
│             5.2 MB                                        │
└─────────────────────────────────────────────────────────┘
```

### 按钮组

```html
<div class="btn-group btn-group-sm">
    <button type="button" class="btn btn-info">
        <i class="fas fa-plus"></i> 插入题干
    </button>
    <button type="button" class="btn btn-outline-info">
        <i class="fas fa-list"></i> 插入选项
    </button>
</div>
```

### 选项选择菜单

点击"插入选项"后弹出：

```
┌──────────────────────────────┐
│  选择要插入的选项              │
├──────────────────────────────┤
│  选项 A: 牛顿第一定律...      │
│  选项 B: 牛顿第二定律...      │
│  选项 C: 牛顿第三定律...      │
│  选项 D: 万有引力定律...      │
├──────────────────────────────┤
│         [取消]                │
└──────────────────────────────┘
```

## 使用场景

### 场景 1: 图片选择题

题干：下列哪个是猫？

- 选项 A: ![图片](cat.jpg)
- 选项 B: ![图片](dog.jpg)
- 选项 C: ![图片](bird.jpg)
- 选项 D: ![图片](fish.jpg)

### 场景 2: 视频实验题

题干：观看以下实验视频
[视频](experiment.mp4)

根据视频回答：小球的加速度约为多少？

- 选项 A: 9.8 m/s²
- 选项 B: 4.9 m/s²

### 场景 3: 听力题

题干：听音频并选择正确的发音

- 选项 A: [音频](pronunciation_a.mp3)
- 选项 B: [音频](pronunciation_b.mp3)
- 选项 C: [音频](pronunciation_c.mp3)

### 场景 4: 混合资源

题干：根据图片和视频回答问题
![图片](diagram.png)
[视频](demo.mp4)

选择正确的解释：
- 选项 A: 解释文字 + [音频](explain_a.mp3)
- 选项 B: 解释文字 + [音频](explain_b.mp3)

## 操作步骤

### 1. 上传资源

1. 点击"上传图片/音频/视频"
2. 选择文件
3. 点击"上传"
4. 等待上传完成

### 2. 插入到题干

1. 在资源列表中找到资源
2. 点击"插入题干"
3. 资源 URL 自动添加到题干文本框

### 3. 插入到选项（新功能）

1. 确保已添加选项（单选题或多选题）
2. 在资源列表中找到资源
3. 点击"插入选项"
4. 在弹出菜单中选择目标选项（A/B/C/D...）
5. 资源 URL 自动添加到选项内容

## 技术实现

### JavaScript 函数

#### insertResourceToStem(url, type)
插入资源到题干

```javascript
function insertResourceToStem(url, type) {
    const stemField = document.getElementById('stem');
    let markdownText = '';

    if (type === 'image') {
        markdownText = `\n![图片](${url})`;
    } else if (type === 'video') {
        markdownText = `\n[视频](${url})`;
    } else if (type === 'audio') {
        markdownText = `\n[音频](${url})`;
    }

    stemField.value += markdownText;
    return false; // 防止表单提交
}
```

#### showInsertToOptionMenu(url, type)
显示选项选择菜单

```javascript
function showInsertToOptionMenu(url, type) {
    const optionsContainer = document.getElementById('optionsContainer');

    // 验证题型
    if (!optionsContainer) {
        alert('只有单选题和多选题才能插入选项');
        return false;
    }

    // 获取所有选项
    const options = optionsContainer.querySelectorAll('.option-item');

    // 生成菜单
    // 创建浮层显示
    // ...

    return false; // 防止表单提交
}
```

#### insertResourceToOption(url, type, optionIndex)
插入资源到指定选项

```javascript
function insertResourceToOption(url, type, optionIndex) {
    const optionField = document.querySelector(`input[name="option_content_${optionIndex}"]`);

    let markdownText = '';
    if (type === 'image') {
        markdownText = `![图片](${url})`;
    } else if (type === 'video') {
        markdownText = `[视频](${url})`;
    } else if (type === 'audio') {
        markdownText = `[音频](${url})`;
    }

    optionField.value += ' ' + markdownText;
    return false; // 防止表单提交
}
```

#### closeInsertMenu()
关闭选项选择菜单

```javascript
function closeInsertMenu() {
    const menu = document.getElementById('insertOptionMenu');
    const backdrop = document.getElementById('insertOptionBackdrop');
    if (menu) menu.remove();
    if (backdrop) backdrop.remove();
    return false;
}
```

## 防止表单提交的措施

所有按钮和函数都采取了双重保护：

1. **HTML 属性**: `type="button"`
2. **JavaScript 返回**: `return false;`
3. **事件处理**: `onclick="...; return false;"`

```html
<!-- 三重保护 -->
<button type="button"
        onclick="insertResourceToStem('url', 'video'); return false;">
    插入题干
</button>
```

## 样式说明

### 按钮组样式

使用 Bootstrap 的 `btn-group` 实现按钮组：

```html
<div class="btn-group btn-group-sm" role="group">
    <button type="button" class="btn btn-info">插入题干</button>
    <button type="button" class="btn btn-outline-info">插入选项</button>
</div>
```

### 浮层菜单样式

```css
position: fixed;
top: 50%;
left: 50%;
transform: translate(-50%, -50%);
background: white;
padding: 20px;
border-radius: 8px;
box-shadow: 0 4px 20px rgba(0,0,0,0.3);
z-index: 10000;
```

### 遮罩层样式

```css
position: fixed;
top: 0;
left: 0;
width: 100%;
height: 100%;
background: rgba(0,0,0,0.5);
z-index: 9999;
```

## 注意事项

### 1. 选项顺序

选项索引从 0 开始：
- 选项 A = index 0
- 选项 B = index 1
- 选项 C = index 2
- ...

### 2. 动态选项

如果在插入资源后添加或删除选项，索引会变化，但已插入的资源不受影响。

### 3. Markdown 格式

前端插入的是 Markdown 格式，需要在渲染时转换为 HTML：

```markdown
![图片](url)  →  <img src="url">
[视频](url)   →  <video src="url"></video>
[音频](url)   →  <audio src="url"></audio>
```

### 4. URL 格式

资源 URL 格式：
```
/admin/questions/{question_id}/resources/{resource_id}/download
```

## 兼容性

- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 13+
- ✅ Edge 80+

## 未来改进

- [ ] 支持拖拽资源到题干或选项
- [ ] 资源预览放大功能
- [ ] 批量插入资源
- [ ] 资源位置管理（重新排序）
- [ ] 支持插入到解析中
- [ ] 资源使用统计

## 总结

现在的资源插入功能：

✅ **问题 1 已修复**: 点击按钮不再导致页面跳转
✅ **问题 2 已实现**: 支持插入资源到选项
✅ **用户体验**: 直观的按钮组和选项选择菜单
✅ **灵活性**: 支持图片、视频、音频三种资源类型
✅ **可扩展**: 易于添加更多资源类型和插入位置

---

**更新日期**: 2025-11-02
**版本**: 2.0.2
**功能**: 资源插入到题干和选项
