#!/usr/bin/env python3
"""
生成 EXAM-MASTER 应用图标
- 后端网页 favicon.ico (16x16, 32x32, 48x48)
- Flutter App 图标 (各种尺寸)
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon_base(size=1024):
    """创建基础图标 - 考试卷子 + 对勾设计"""
    # 创建画布
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 配色方案 - 专业的蓝绿色调
    bg_color = (67, 97, 238)  # 主蓝色
    paper_color = (255, 255, 255)  # 白色
    check_color = (52, 211, 153)  # 绿色对勾
    shadow_color = (0, 0, 0, 30)  # 阴影
    line_color = (200, 200, 200)  # 纸张线条

    # 计算尺寸
    margin = size * 0.15
    paper_width = size - margin * 2
    paper_height = size - margin * 2

    # 绘制背景圆角矩形
    draw.rounded_rectangle(
        [(0, 0), (size, size)],
        radius=size * 0.15,
        fill=bg_color
    )

    # 绘制纸张阴影
    shadow_offset = size * 0.02
    draw.rounded_rectangle(
        [(margin + shadow_offset, margin + shadow_offset),
         (margin + paper_width + shadow_offset, margin + paper_height + shadow_offset)],
        radius=size * 0.05,
        fill=shadow_color
    )

    # 绘制白色纸张
    draw.rounded_rectangle(
        [(margin, margin), (margin + paper_width, margin + paper_height)],
        radius=size * 0.05,
        fill=paper_color
    )

    # 绘制纸张上的线条（模拟考卷）
    line_count = 5
    line_spacing = paper_height / (line_count + 1)
    line_y_start = margin + line_spacing
    line_x_start = margin + paper_width * 0.15
    line_x_end = margin + paper_width * 0.85

    for i in range(line_count):
        y = line_y_start + i * line_spacing
        draw.line(
            [(line_x_start, y), (line_x_end, y)],
            fill=line_color,
            width=int(size * 0.008)
        )

    # 绘制大对勾 (✓)
    check_size = size * 0.45
    check_x = size * 0.5
    check_y = size * 0.55
    check_width = int(size * 0.08)

    # 对勾的两条线
    # 短线（左下）
    draw.line(
        [(check_x - check_size * 0.3, check_y),
         (check_x - check_size * 0.05, check_y + check_size * 0.25)],
        fill=check_color,
        width=check_width
    )

    # 长线（右上）
    draw.line(
        [(check_x - check_size * 0.05, check_y + check_size * 0.25),
         (check_x + check_size * 0.4, check_y - check_size * 0.35)],
        fill=check_color,
        width=check_width
    )

    # 在顶部添加小标题点
    dot_y = margin + paper_height * 0.12
    dot_radius = size * 0.03
    for i in range(3):
        x = margin + paper_width * (0.25 + i * 0.25)
        draw.ellipse(
            [(x - dot_radius, dot_y - dot_radius),
             (x + dot_radius, dot_y + dot_radius)],
            fill=bg_color
        )

    return img

def save_favicon(base_img, output_path):
    """保存为 favicon.ico (多尺寸)"""
    sizes = [16, 32, 48, 64]
    icons = []

    for size in sizes:
        icon = base_img.resize((size, size), Image.Resampling.LANCZOS)
        icons.append(icon)

    # 保存为 ICO 文件（包含多个尺寸）
    icons[0].save(
        output_path,
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=icons[1:]
    )
    print(f"✓ Favicon saved: {output_path}")

def save_flutter_icons(base_img, flutter_dir):
    """保存 Flutter App 图标（各平台所需尺寸）"""

    # Android 图标尺寸
    android_sizes = {
        'mipmap-mdpi': 48,
        'mipmap-hdpi': 72,
        'mipmap-xhdpi': 96,
        'mipmap-xxhdpi': 144,
        'mipmap-xxxhdpi': 192,
    }

    # iOS 图标尺寸（AppIcon.appiconset）
    ios_sizes = {
        'Icon-20@2x': 40,
        'Icon-20@3x': 60,
        'Icon-29@2x': 58,
        'Icon-29@3x': 87,
        'Icon-40@2x': 80,
        'Icon-40@3x': 120,
        'Icon-60@2x': 120,
        'Icon-60@3x': 180,
        'Icon-76': 76,
        'Icon-76@2x': 152,
        'Icon-83.5@2x': 167,
        'Icon-1024': 1024,
    }

    # Android 图标
    android_base = os.path.join(flutter_dir, 'android', 'app', 'src', 'main', 'res')
    for folder, size in android_sizes.items():
        folder_path = os.path.join(android_base, folder)
        os.makedirs(folder_path, exist_ok=True)

        icon = base_img.resize((size, size), Image.Resampling.LANCZOS)
        icon_path = os.path.join(folder_path, 'ic_launcher.png')
        icon.save(icon_path, 'PNG')
        print(f"✓ Android icon saved: {folder}/ic_launcher.png ({size}x{size})")

    # iOS 图标
    ios_base = os.path.join(flutter_dir, 'ios', 'Runner', 'Assets.xcassets', 'AppIcon.appiconset')
    os.makedirs(ios_base, exist_ok=True)

    for name, size in ios_sizes.items():
        icon = base_img.resize((size, size), Image.Resampling.LANCZOS)
        icon_path = os.path.join(ios_base, f'{name}.png')
        icon.save(icon_path, 'PNG')
        print(f"✓ iOS icon saved: {name}.png ({size}x{size})")

    # 生成 Contents.json for iOS
    contents_json = {
        "images": [
            {"size": "20x20", "idiom": "iphone", "filename": "Icon-20@2x.png", "scale": "2x"},
            {"size": "20x20", "idiom": "iphone", "filename": "Icon-20@3x.png", "scale": "3x"},
            {"size": "29x29", "idiom": "iphone", "filename": "Icon-29@2x.png", "scale": "2x"},
            {"size": "29x29", "idiom": "iphone", "filename": "Icon-29@3x.png", "scale": "3x"},
            {"size": "40x40", "idiom": "iphone", "filename": "Icon-40@2x.png", "scale": "2x"},
            {"size": "40x40", "idiom": "iphone", "filename": "Icon-40@3x.png", "scale": "3x"},
            {"size": "60x60", "idiom": "iphone", "filename": "Icon-60@2x.png", "scale": "2x"},
            {"size": "60x60", "idiom": "iphone", "filename": "Icon-60@3x.png", "scale": "3x"},
            {"size": "76x76", "idiom": "ipad", "filename": "Icon-76.png", "scale": "1x"},
            {"size": "76x76", "idiom": "ipad", "filename": "Icon-76@2x.png", "scale": "2x"},
            {"size": "83.5x83.5", "idiom": "ipad", "filename": "Icon-83.5@2x.png", "scale": "2x"},
            {"size": "1024x1024", "idiom": "ios-marketing", "filename": "Icon-1024.png", "scale": "1x"}
        ],
        "info": {"version": 1, "author": "xcode"}
    }

    import json
    with open(os.path.join(ios_base, 'Contents.json'), 'w') as f:
        json.dump(contents_json, f, indent=2)
    print(f"✓ iOS Contents.json created")

    # Web 图标 (Flutter Web)
    web_base = os.path.join(flutter_dir, 'web')
    if os.path.exists(web_base):
        # favicon.png
        favicon = base_img.resize((32, 32), Image.Resampling.LANCZOS)
        favicon.save(os.path.join(web_base, 'favicon.png'), 'PNG')

        # icons for manifest
        for size in [192, 512]:
            icon = base_img.resize((size, size), Image.Resampling.LANCZOS)
            icon.save(os.path.join(web_base, f'icons', f'Icon-{size}.png'), 'PNG')
        print(f"✓ Flutter Web icons saved")

def main():
    # 项目路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(script_dir, 'backend')
    flutter_dir = os.path.join(script_dir, 'flutter_app')

    print("🎨 Generating EXAM-MASTER Icons...")
    print("=" * 50)

    # 生成基础图标 (1024x1024)
    print("\n1. Creating base icon (1024x1024)...")
    base_icon = create_icon_base(1024)

    # 保存预览图
    preview_path = os.path.join(script_dir, 'icon_preview.png')
    base_icon.save(preview_path, 'PNG')
    print(f"✓ Preview saved: icon_preview.png")

    # 保存后端 favicon
    print("\n2. Creating backend favicon.ico...")
    backend_static = os.path.join(backend_dir, 'static')
    os.makedirs(backend_static, exist_ok=True)
    favicon_path = os.path.join(backend_static, 'favicon.ico')
    save_favicon(base_icon, favicon_path)

    # 保存 Flutter 图标
    if os.path.exists(flutter_dir):
        print("\n3. Creating Flutter app icons...")
        save_flutter_icons(base_icon, flutter_dir)
    else:
        print(f"\n⚠️  Flutter directory not found: {flutter_dir}")
        print("   Skipping Flutter icons...")

    print("\n" + "=" * 50)
    print("✅ All icons generated successfully!")
    print("\nGenerated files:")
    print(f"  • Preview: {preview_path}")
    print(f"  • Backend favicon: {favicon_path}")
    if os.path.exists(flutter_dir):
        print(f"  • Flutter Android icons: flutter_app/android/app/src/main/res/mipmap-*/")
        print(f"  • Flutter iOS icons: flutter_app/ios/Runner/Assets.xcassets/AppIcon.appiconset/")
        print(f"  • Flutter Web icons: flutter_app/web/icons/")

if __name__ == '__main__':
    main()
