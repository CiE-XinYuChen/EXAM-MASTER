# 题库大师 Android 版

基于原有 Flask Web 应用重新开发的 Android 原生应用，采用最新的 Material Design 3 设计规范，提供完整的题库练习和考试功能。

## 🌟 功能特性

### 📱 原生 Android 体验
- **Material Design 3**: 遵循 Google 最新设计规范
- **响应式布局**: 适配各种屏幕尺寸
- **深色模式**: 支持系统主题切换
- **离线优先**: 所有数据本地存储，无需网络连接

### 📚 完整题库功能
- **题库管理**: 内置完整题库，支持 CSV 导入
- **多种题型**: 单选题、多选题等
- **分类系统**: 按类别和难度组织题目
- **搜索筛选**: 强大的搜索和筛选功能

### 📋 丰富答题模式
- **随机练习**: 从题库随机抽取题目练习
- **顺序练习**: 按顺序练习所有题目，自动记录进度
- **错题本**: 专门练习做错的题目
- **限时模式**: 在规定时间内完成答题
- **模拟考试**: 完整的考试流程和评分

### 🔖 个性化功能
- **收藏系统**: 收藏重要题目，支持标签管理
- **答题历史**: 完整记录所有答题记录
- **统计分析**: 详细的学习统计和进度跟踪
- **个性设置**: 丰富的个性化设置选项

## 💻 技术架构

### 核心技术栈
- **Kotlin**: 100% Kotlin 开发
- **Jetpack Compose**: 现代化 UI 框架
- **Material Design 3**: 最新设计系统
- **Architecture Components**: MVVM 架构

### 主要依赖
- **Room**: 本地数据库
- **Hilt**: 依赖注入
- **Navigation Compose**: 导航框架
- **DataStore**: 偏好设置存储
- **Coroutines**: 异步处理

### 项目结构
```
app/src/main/kotlin/com/exammaster/
├── data/                           # 数据层
│   ├── database/                   # 数据库相关
│   │   ├── entities/              # 数据库实体
│   │   ├── dao/                   # 数据访问对象
│   │   └── ExamMasterDatabase.kt  # 数据库配置
│   ├── datastore/                 # 偏好设置
│   ├── models/                    # 数据模型
│   └── repository/                # 仓储层
├── di/                            # 依赖注入
├── ui/                            # UI 层
│   ├── components/                # 通用组件
│   ├── navigation/                # 导航
│   ├── screens/                   # 屏幕页面
│   └── theme/                     # 主题设置
├── utils/                         # 工具类
├── ExamMasterApplication.kt       # 应用入口
└── MainActivity.kt                # 主活动
```

## 🚀 构建和运行

### 环境要求
- Android Studio Iguana | 2023.2.1 或更高版本
- Kotlin 1.9.22 或更高版本
- Gradle 8.4
- Android SDK 34
- 最低支持 Android 7.0 (API 24)

### 构建步骤
1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd EXAM-MASTER/ExamMasterAndroid
   ```

2. **在 Android Studio 中打开项目**
   - 选择 "Open an existing Android Studio project"
   - 选择 ExamMasterAndroid 文件夹

3. **同步项目**
   - Android Studio 会自动同步 Gradle 依赖

4. **运行应用**
   - 连接 Android 设备或启动模拟器
   - 点击 "Run" 按钮或使用快捷键 Shift+F10

### 构建变体
- **Debug**: 开发版本，包含调试信息
- **Release**: 发布版本，经过代码混淆和优化

## 📊 数据库设计

### 核心表结构
- **questions**: 题目信息
- **history**: 答题历史
- **favorites**: 收藏题目
- **exam_sessions**: 考试会话

### 数据导入
应用首次启动时会自动从 `assets/questions.csv` 导入题库数据。

## 🎨 UI/UX 设计

### Material Design 3
- 采用最新的 Material Design 3 设计语言
- 支持动态取色和自适应主题
- 优雅的动画和交互效果

### 响应式设计
- 支持手机和平板设备
- 自适应屏幕方向变化
- 优化的触摸交互体验

## 🔧 开发指南

### 代码规范
- 遵循 Kotlin 官方编码规范
- 使用 MVVM 架构模式
- 单一职责原则

### 测试策略
- 单元测试：核心业务逻辑
- 集成测试：数据库操作
- UI 测试：关键用户流程

### 性能优化
- 懒加载和分页
- 图片缓存和压缩
- 内存泄漏检测

## 📝 许可证

本项目基于 MIT 许可证开源。

---

**开发者**: ShayneChen  
**联系方式**: xinyu-c@outlook.com  
**项目主页**: [GitHub](https://github.com/CiE-XinYuChen/EXAM-MASTER)