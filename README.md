# EXAM-MASTER

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)

一款基于 **Flask** 实现的在线刷题系统，提供从题库管理、用户注册登录，到随机出题、顺序答题、定时模式、模拟考试，以及收藏、标记、统计分析等多种功能，帮助用户高效提升学习和练习效果。

## 🌟 功能特性

### 📝 用户管理
- **注册与登录**: 安全的用户账户创建与登录系统
- **个人数据跟踪**: 自动保存学习进度与题目记录

### 📚 题库管理
- **CSV导入题库**: 便捷的题库导入功能
- **多种题型支持**: 单选题、多选题等多种题型
- **分类与难度系统**: 按类别和难度对题目进行组织

### 📋 答题模式
- **随机答题**: 快速练习，从题库随机抽题
- **顺序答题**: 从上次停止的位置开始，系统实时记录进度，保证下次访问时能无缝继续
- **错题本**: 专注复习做错的题目
- **定时模式**: 在规定时间内完成题目，提高效率
- **模拟考试**: 模拟真实考试环境，一次性提交所有答案

### 🔍 查找与筛选
- **关键词搜索**: 通过题干内容快速查找题目
- **分类筛选**: 按类别、难度等条件筛选题目

### 🔖 个性化学习
- **收藏与标记**: 将重要题目加入收藏夹，添加个性化标记
- **答题历史**: 完整记录所有已答题目及正确情况
- **统计分析**: 详细的答题统计，包括正确率、难度分布和易错题排行

## 💻 技术栈

- **后端**: Python + Flask
- **数据库**: SQLite
- **前端**: HTML/CSS + Jinja2模板引擎
- **数据格式**: CSV导入题库、JSON存储选项

## 🚀 快速开始

### 安装与部署

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

### 顺序答题功能改进
- **进度记忆优化**: 顺序答题现在会始终从上次停止的位置继续，不再总是从第一题开始
- **实时位置更新**: 即使浏览某个题目但未作答，系统也会记录当前位置
- **完善循环逻辑**: 当所有题目做完后，系统会自动从第一题重新开始，而不是显示完成信息

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
