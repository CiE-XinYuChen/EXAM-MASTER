# EXAM-MASTER

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)
![Android](https://img.shields.io/badge/Android-v3.0-green.svg)
![Platform](https://img.shields.io/badge/Platform-Web%20%7C%20Mobile-blue.svg)

一款基于 **Flask** 实现的全平台在线刷题系统，现已支持 **Web端** 和 **Android移动端**。提供从题库管理、用户注册登录，到随机出题、顺序答题、定时模式、模拟考试，以及收藏、标记、统计分析等多种功能，帮助用户随时随地高效提升学习和练习效果。

## 🌟 功能特性

### 📱 多平台支持
- **Web端**: 现代化响应式设计，支持桌面和移动浏览器
- **Android端**: 原生Android应用 (v3.0)，流畅的移动体验
- **同步数据**: 跨平台数据同步，随时切换设备继续学习

### 📝 用户管理
- **注册与登录**: 安全的用户账户创建与登录系统
- **个人数据跟踪**: 自动保存学习进度与题目记录
- **智能续答**: 系统记忆答题进度，无缝继续学习

### 📚 题库管理
- **CSV导入题库**: 便捷的题库导入功能
- **多种题型支持**: 单选题、多选题、判断题、填空题等
- **分类与难度系统**: 按类别和难度对题目进行组织
- **题目浏览**: 分页浏览所有题目，支持快速定位

### 📋 答题模式
- **随机答题**: 快速练习，从题库随机抽题
- **顺序答题**: 从上次停止的位置开始，系统实时记录进度，保证下次访问时能无缝继续
- **错题本**: 专注复习做错的题目，针对性提升
- **定时模式**: 在规定时间内完成题目，提高效率
- **模拟考试**: 模拟真实考试环境，一次性提交所有答案

### 🔍 查找与筛选
- **关键词搜索**: 通过题干内容或题号快速查找题目
- **智能筛选**: 按题型、类别、难度等条件筛选题目
- **全站搜索**: 支持跨页面搜索，不限于当前页面
- **筛选芯片**: 移动端友好的筛选界面，一键切换题型

### 🔖 个性化学习
- **收藏与标记**: 将重要题目加入收藏夹，添加个性化标记
- **答题历史**: 完整记录所有已答题目及正确情况
- **统计分析**: 详细的答题统计，包括正确率、难度分布和学习进度
- **学习轨迹**: 追踪学习路径，了解知识掌握情况

## 💻 技术栈

### Web端
- **后端**: Python + Flask
- **数据库**: SQLite
- **前端**: HTML/CSS + JavaScript + Jinja2模板引擎
- **UI框架**: Bootstrap工具类 + 自定义CSS
- **数据格式**: CSV导入题库、JSON存储选项

### Android端
- **开发语言**: Kotlin
- **UI框架**: Jetpack Compose
- **架构模式**: MVVM + Repository Pattern
- **数据库**: Room (SQLite)
- **网络请求**: Retrofit + OkHttp

## 🚀 快速开始

### Web端部署

1. **克隆仓库**
   ```bash
   git clone https://github.com/CiE-XinYuChen/EXAM-MASTER.git
   cd EXAM-MASTER
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **启动应用**
   ```bash
   python app.py
   ```
   应用将在 http://localhost:32220 上运行

### Android端安装

1. **直接下载APK**
   - 访问项目首页或[Releases页面](https://github.com/CiE-XinYuChen/EXAM-MASTER/releases)
   - 下载最新版本 `exammaster-v3.0.apk`
   
2. **安装说明**
   - 允许"未知来源"应用安装
   - 安装后输入Web端相同的服务器地址即可同步数据

3. **本地编译**（可选）
   ```bash
   cd ExamMasterAndroid
   ./gradlew assembleDebug
   ```

### 题库格式

题库使用CSV格式，包含以下字段：
- 题号: 题目唯一标识
- 题干: 题目内容
- A, B, C, D, E: 选项（可选）
- 答案: 正确答案，如"A"或"ABCD"（多选）
- 难度: 题目难度级别
- 题型: 如"单选题"、"多选题"等
- 类别: 题目所属类别（可选）

## 📖 使用指南

### 基本操作

1. **注册/登录**: 首次使用需注册账号，之后直接登录
2. **导航菜单**: 页面顶部提供多种功能入口
3. **答题流程**: 
   - 选择答题模式（随机/顺序/错题等）
   - 选择答案后提交
   - 系统自动判断正确性并记录

### 特殊功能

- **搜索题目**: 在"搜索题目"页面输入关键词
- **收藏题目**: 在答题页面点击"收藏"按钮，在"我的收藏"中查看
- **顺序刷题**: 系统实时记录进度，随时退出后下次访问将自动从上次答题位置继续
- **统计分析**: 在"统计与反馈"页面查看个人学习数据

## 🔄 最近更新

### v3.0 - Android端正式发布 (2025-05)
- **🎉 Android应用上线**: 原生Android应用正式发布，支持离线使用
- **📱 移动端优化**: 完全重写移动端浏览题目UI，现代化卡片设计
- **🔍 全站搜索**: 搜索和筛选功能从前端改为后端实现，支持跨页面操作
- **🛠 UI修复**: 修复电脑端布局串位问题，完善CSS工具类定义
- **🎯 筛选增强**: 修复移动端筛选芯片显示问题，正确显示所有题型

### v2.1 - Web端功能完善 (2025-05)
- **🔧 顺序答题优化**: 智能记忆答题进度，从上次停止位置继续
- **📊 统计功能增强**: 更详细的学习数据分析和可视化
- **🎨 响应式优化**: 改进移动端浏览体验和交互设计

### v2.0 - 核心功能重构 (2025-04)
- **🏗 架构升级**: 重构核心答题逻辑，提升系统稳定性
- **💾 数据持久化**: 优化数据存储和查询性能
- **🎪 界面美化**: 全新UI设计，提升用户体验

## 📊 项目截图
![86e83be8fcebbb8110a59f5929e77f96](https://github.com/user-attachments/assets/0b41c79d-5a42-4136-ae2e-a4c5c37b5520)
![8d8919fb3dba32585d0e2e01d4378df0](https://github.com/user-attachments/assets/a2a7c83b-ab16-430a-92ed-2c71877d86a3)
![9c083e6f3509c0741c710f0140f08ae7](https://github.com/user-attachments/assets/91be6aaf-b1c0-4f06-a19b-ef713526a132)
![01b260ee29663d9f5e0236636785404e](https://github.com/user-attachments/assets/5cb79c3b-beaa-4fe6-af98-a2dc593ed79c)
![032c2c61fd1e51511bf03a83aae71e10](https://github.com/user-attachments/assets/e00a6d37-e086-42a0-92ac-028ad7e6298c)


## 🛠 开发者信息

- **作者**: ShayneChen
- **联系方式**: [xinyu-c@outlook.com](mailto:xinyu-c@outlook.com)
- **项目主页**: [GitHub](https://github.com/CiE-XinYuChen/EXAM-MASTER)

## 📄 许可证

本项目基于 MIT 许可证开源。

---

欢迎提交Issue或Pull Request，共同完善本系统！
