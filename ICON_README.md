# EXAM-MASTER 应用图标说明

## 🎨 图标设计

**设计理念**：
- 蓝色背景：代表专业、可信赖的学习平台
- 白色纸张：象征考试卷/题库
- 绿色对勾：表示正确答案、通过考试
- 横线纹理：模拟真实考卷的样式

**配色方案**：
- 主蓝色：`#4361EE` - 专业、现代
- 绿色对勾：`#34D399` - 成功、通过
- 白色纸张：`#FFFFFF` - 简洁、清晰

## 📁 生成的文件

### 后端网页图标
```
backend/static/favicon.ico
```
- 包含多个尺寸：16x16, 32x32, 48x48, 64x64
- 浏览器标签页图标
- 书签图标

### Flutter App 图标

#### Android
```
flutter_app/android/app/src/main/res/
├── mipmap-mdpi/ic_launcher.png      (48x48)
├── mipmap-hdpi/ic_launcher.png      (72x72)
├── mipmap-xhdpi/ic_launcher.png     (96x96)
├── mipmap-xxhdpi/ic_launcher.png    (144x144)
└── mipmap-xxxhdpi/ic_launcher.png   (192x192)
```

#### iOS
```
flutter_app/ios/Runner/Assets.xcassets/AppIcon.appiconset/
├── Icon-20@2x.png       (40x40)
├── Icon-20@3x.png       (60x60)
├── Icon-29@2x.png       (58x58)
├── Icon-29@3x.png       (87x87)
├── Icon-40@2x.png       (80x80)
├── Icon-40@3x.png       (120x120)
├── Icon-60@2x.png       (120x120)
├── Icon-60@3x.png       (180x180)
├── Icon-76.png          (76x76)
├── Icon-76@2x.png       (152x152)
├── Icon-83.5@2x.png     (167x167)
├── Icon-1024.png        (1024x1024)
└── Contents.json
```

#### Flutter Web
```
flutter_app/web/
├── favicon.png
└── icons/
    ├── Icon-192.png
    └── Icon-512.png
```

### 预览图
```
icon_preview.png (1024x1024)
```

## 🔧 如何使用

### 后端 favicon 已自动配置

在 `backend/templates/admin/base.html` 中已添加：
```html
<link rel="icon" type="image/x-icon" href="/static/favicon.ico">
<link rel="shortcut icon" type="image/x-icon" href="/static/favicon.ico">
```

### Flutter App 配置

#### Android（已完成）
图标已放置在正确的 mipmap 文件夹中，无需额外配置。

#### iOS（已完成）
图标和 `Contents.json` 已生成，Xcode 会自动识别。

#### Flutter Web（已完成）
确保 `web/manifest.json` 中包含：
```json
{
  "icons": [
    {
      "src": "icons/Icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "icons/Icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

## 🔄 重新生成图标

如需修改图标设计，运行：

```bash
cd /path/to/EXAM-MASTER
python3 generate_icons.py
```

脚本会重新生成所有尺寸的图标。

## 🎯 图标尺寸参考

| 平台 | 尺寸 | 用途 |
|------|------|------|
| **Web** | 16x16, 32x32 | 浏览器标签 |
| **Web** | 48x48 | 书签栏 |
| **Android** | 48-192px | 应用图标（各密度） |
| **iOS** | 20-1024px | 应用图标（各场景） |
| **PWA** | 192px, 512px | Web应用图标 |

## ✨ 特性

- ✅ 矢量风格，缩放不失真
- ✅ 支持所有主流平台
- ✅ 自动生成多种尺寸
- ✅ 专业的设计风格
- ✅ 符合各平台设计规范

## 📝 修改建议

如需调整图标，可修改 `generate_icons.py` 中的：
- `bg_color`: 背景颜色
- `check_color`: 对勾颜色
- `line_color`: 纸张线条颜色
- 调整元素大小和位置

---

**生成时间**: 2025-11-06
**工具**: Python + Pillow
**设计**: EXAM-MASTER Team
