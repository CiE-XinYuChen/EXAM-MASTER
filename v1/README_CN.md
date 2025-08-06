# EXAM-MASTER 题库大师

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)
![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)
![Android](https://img.shields.io/badge/Android-v3.0-green.svg)
![Kotlin](https://img.shields.io/badge/Kotlin-1.9.22-purple.svg)
![Platform](https://img.shields.io/badge/Platform-Web%20%7C%20Android-blue.svg)

[English](README.md) | [中文](README_CN.md)

一款功能完善的跨平台考试题库管理系统，提供 **Web端** 和 **Android原生应用** 双平台支持。Web端基于Flask框架开发，Android端采用Kotlin和Jetpack Compose技术栈，为用户提供题库管理、多种练习模式、统计分析和学习进度跟踪的完整解决方案。

## 🌟 核心功能

### 📱 多平台支持
- **Web应用**: 现代化响应式设计，支持桌面和移动浏览器访问
- **Android应用**: 原生Android应用（v3.0），提供流畅的移动体验
- **离线功能**: 完全支持离线使用，数据本地存储
- **数据互通**: 兼容的数据格式，为未来跨平台同步做准备

### 📝 用户管理
- **身份认证**: 安全的用户注册和登录系统
- **进度跟踪**: 自动保存学习进度和答题历史
- **智能续答**: 系统记忆答题位置，无缝继续上次的学习
- **个人仪表板**: 个人统计数据和成绩指标展示

### 📚 题库管理
- **CSV导入**: 批量导入CSV格式的题目
- **多题型支持**: 单选题、多选题、判断题等
- **分类管理**: 按类别和难度级别组织题目
- **题目浏览**: 分页浏览，支持筛选和快速导航
- **灵活格式**: 支持可变数量的选项（A-E）

### 📋 练习模式
- **随机练习**: 随机选择题目进行快速练习
- **顺序练习**: 按顺序练习，自动保存位置
- **错题练习**: 专注练习做错的题目，针对性提高
- **限时模式**: 在设定时间内完成题目，提高答题效率
- **模拟考试**: 完整考试环境，批量提交和综合评分
- **浏览模式**: 查看所有题目，支持展开详情

### 🔍 搜索与筛选
- **关键词搜索**: 通过内容或题号快速查找题目
- **智能筛选**: 按题型、类别和难度级别筛选
- **全局搜索**: 跨页面搜索，不限于当前视图
- **筛选芯片**: 移动端友好的筛选界面，一键切换
- **高级查询**: 支持复杂搜索模式

### 🔖 个性化学习
- **收藏系统**: 收藏重要题目，支持自定义标签
- **答题历史**: 完整记录所有尝试过的题目和结果
- **统计分析**: 详细统计包括正确率、难度分布和进度
- **学习分析**: 跟踪学习模式和知识掌握情况
- **成绩洞察**: 识别优势和需要改进的领域

## 💻 技术架构

### Web应用
- **后端**: Python 3.6+ 配合 Flask 2.3.3
- **数据库**: SQLite3，包含5个主要数据表
- **前端**: HTML5/CSS3 + JavaScript + Jinja2模板引擎
- **UI框架**: Bootstrap工具类 + 自定义CSS（Material Design风格）
- **身份认证**: 基于Session的安全密码哈希认证
- **数据格式**: CSV导入，JSON字段存储灵活选项

### Android应用
- **开发语言**: 100% Kotlin 1.9.22
- **UI框架**: Jetpack Compose 配合 Material Design 3
- **架构模式**: MVVM + Repository模式 + 清洁架构
- **数据库**: Room持久化库（SQLite）
- **依赖注入**: Hilt
- **异步处理**: Kotlin协程 + Flow
- **导航**: Navigation Compose
- **状态管理**: StateFlow + Compose State
- **最低SDK**: API 24（Android 7.0）

## 🚀 快速开始

### Web应用部署

1. **克隆仓库**
   ```bash
   git clone https://github.com/CiE-XinYuChen/EXAM-MASTER.git
   cd EXAM-MASTER
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **初始化数据库**（首次运行时自动执行）
   应用将自动：
   - 创建SQLite数据库
   - 初始化数据表
   - 从`questions.csv`导入题目

4. **运行应用**
   ```bash
   python app.py
   ```
   应用将在 http://localhost:32220 上运行

### Android应用安装

1. **直接下载APK**
   - 访问 [Releases页面](https://github.com/CiE-XinYuChen/EXAM-MASTER/releases)
   - 下载最新版本 `exammaster-v4-debug.apk`
   
2. **安装步骤**
   - 在设置中启用"允许安装未知来源应用"
   - 安装APK文件
   - 应用完全支持离线使用

3. **从源码构建**（可选）
   ```bash
   cd ExamMasterAndroid
   ./gradlew assembleDebug
   # APK文件将生成在 app/build/outputs/apk/debug/
   ```

4. **构建环境要求**
   - Android Studio Iguana 2023.2.1+
   - Kotlin 1.9.22+
   - Gradle 8.4
   - Android SDK 34

### 题库格式

题目使用CSV格式，包含以下字段：

| 字段 | 描述 | 示例 |
|-------|-------------|---------|  
| 题号 | 题目唯一标识符 | "001" |
| 题干 | 题目内容 | "2+2等于多少？" |
| A, B, C, D, E | 答案选项（可选） | "2", "3", "4", "5" |
| 答案 | 正确答案 | "C" 或 "ABC"（多选） |
| 难度 | 难度级别 | "简单", "中等", "困难" |
| 题型 | 题目类型 | "单选题", "多选题", "判断题" |
| 类别 | 题目分类（可选） | "数学", "科学" |

**注意**：判断题使用"正确"和"错误"作为答案。

## 📖 使用指南

### 基本操作

1. **注册/登录**：首次使用需注册账号，之后使用凭据登录
2. **导航**: 
   - **Web端**：顶部导航栏配合下拉菜单
   - **Android端**：底部导航栏包含5个主要部分
3. **答题流程**: 
   - 选择练习模式（随机/顺序/错题/限时/考试）
   - 选择答案
   - 提交获得即时反馈
   - 系统自动跟踪进度

### 高级功能

- **搜索题目**：使用搜索页面通过关键词或题号查找特定题目
- **收藏题目**：点击星标图标收藏，在"我的收藏"中查看
- **顺序练习**：自动保存位置，从上次离开的地方继续
- **错题复习**：自动收集错题，练习直到掌握
- **统计仪表板**：查看综合学习分析和进度图表
- **限时练习**：设置自定义时间限制进行速度训练
- **考试模式**：模拟真实考试环境，包含计时和最终评分

## 🔄 最近更新

### v4.0 - 完整架构升级 (2025-08)
- **🚀 Android应用v3.0**：采用Jetpack Compose的完整原生Android应用
- **🎨 Material Design 3**：现代UI设计，支持动态主题
- **📊 增强分析**：包含可视化图表的综合统计
- **🔄 性能优化**：优化数据库查询和懒加载
- **🎯 智能功能**：自适应学习推荐

### v3.0 - 移动优先设计 (2025-05)
- **📱 移动优化**：完全重写移动UI，采用卡片式设计
- **🔍 后端搜索**：服务器端搜索和筛选，提高性能
- **🛠 UI修复**：修复桌面布局问题，改进CSS工具类
- **🎯 增强筛选**：修复移动端筛选芯片，正确显示所有题型

### v2.0 - 核心功能实现 (2025-04)
- **🏗 架构**：重构核心逻辑提高稳定性
- **💾 数据持久化**：优化存储和查询性能
- **🎪 UI增强**：新设计系统实现
- **🔧 顺序模式**：智能进度记忆系统
- **📊 统计**：详细的学习分析

## 📊 应用截图
![86e83be8fcebbb8110a59f5929e77f96](https://github.com/user-attachments/assets/0b41c79d-5a42-4136-ae2e-a4c5c37b5520)
![8d8919fb3dba32585d0e2e01d4378df0](https://github.com/user-attachments/assets/a2a7c83b-ab16-430a-92ed-2c71877d86a3)
![9c083e6f3509c0741c710f0140f08ae7](https://github.com/user-attachments/assets/91be6aaf-b1c0-4f06-a19b-ef713526a132)
![01b260ee29663d9f5e0236636785404e](https://github.com/user-attachments/assets/5cb79c3b-beaa-4fe6-af98-a2dc593ed79c)
![032c2c61fd1e51511bf03a83aae71e10](https://github.com/user-attachments/assets/e00a6d37-e086-42a0-92ac-028ad7e6298c)

## 🏗 项目结构

### Web应用结构
```
EXAM-MASTER/
├── app.py                 # Flask主应用
├── database.db           # SQLite数据库
├── questions.csv         # 题库数据
├── requirements.txt      # Python依赖
├── static/              # CSS和静态文件
├── templates/           # Jinja2 HTML模板
└── tools/               # 数据转换工具
```

### Android应用结构
```
ExamMasterAndroid/
├── app/src/main/kotlin/com/exammaster/
│   ├── data/            # 数据层（Room、Repository）
│   ├── di/              # 依赖注入（Hilt）
│   ├── ui/              # UI层（Compose界面）
│   └── MainActivity.kt  # 入口点
└── build.gradle.kts     # 构建配置
```

## 🔧 开发工具

### 题目转换工具
项目包含用于转换不同格式题目的工具：

- `tools/convert_txt_csv.py` - 将文本格式转换为CSV
- `tools/convert_gongtongt_txt_to_csv.py` - 转换特定格式

使用示例：
```bash
python tools/convert_txt_csv.py input.txt output.csv
```

## 🤝 参与贡献

欢迎贡献代码！请随时提交Pull Request。

1. Fork本仓库
2. 创建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个Pull Request

## 👥 作者

- **开发者**: ShayneChen
- **邮箱**: [xinyu-c@outlook.com](mailto:xinyu-c@outlook.com)
- **GitHub**: [CiE-XinYuChen](https://github.com/CiE-XinYuChen)
- **项目主页**: [EXAM-MASTER](https://github.com/CiE-XinYuChen/EXAM-MASTER)

## 📄 许可证

本项目基于MIT许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- Material Design 3 设计指南
- Jetpack Compose社区的UI组件
- Flask社区的Web框架支持
- 所有贡献者和使用者

---

⭐ **如果您觉得这个项目有帮助，请给它一个星标！**

欢迎提交问题或Pull Request来帮助改进系统！