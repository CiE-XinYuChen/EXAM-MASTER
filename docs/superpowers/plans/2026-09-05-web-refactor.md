# EXAM-MASTER Web Refactor Implementation Plan

**Goal:** 保留学习功能，补齐题库管理，以 Open Design 重设计网页，并减少至少 50% Web 源码。
**Architecture:** Flask 服务端模板。db.py 负责 SQLite 与 CSV，app.py 合并页面与学习流程，共用模板、CSS、少量 JavaScript。
**Tech Stack:** Python、Flask、sqlite3、Jinja、原生 CSS/JavaScript。
**Spec:** ../specs/2026-09-05-web-refactor-design.md

## Global Constraints

- 保留登录、多用户记录、全部现有学习模式。
- 原始数据库增量升级，原始 CSV 与 Android 文件不改动。
- 无 ORM、SPA 或额外安全子系统。
- Open Design 实际生成设计，主任务接入真实功能。

## 1. 数据与题库管理

- [x] 用临时数据库编写题目 CRUD、CSV 更新/错误回滚/往返测试；在旧实现上确认管理入口缺失。
- [x] 在 db.py 实现连接复用、原表创建/增量字段、题目规范化、CSV 导入导出。
- [x] 在 app.py 合并登录与注册、列表与筛选，增加题目编辑和导入导出页面。
- [x] 运行 `venv/bin/python -m unittest discover -s tests -v` 验证实际数据库状态。

## 2. 共用学习流程

- [x] 测试四种判题、随机未答、顺序进度、收藏标签/错题、多用户、考试持久化和重复提交。
- [x] 合并练习处理；考试开始保存题目快照，完成保存结果；统计使用集合查询。
- [x] 旧 URL 保留轻量入口或重定向，检查旧数据库记录仍可显示。

## 3. Open Design 页面落地

- [x] 等待 Open Design 完成，读取产物与设计说明并保存来源信息。
- [x] 使用设计的共享结构和样式替换旧模板，接入页面表单与真实数据。
- [x] JavaScript 只处理导航、确认、计时、草稿和输入辅助；移除旧重复模板与脚本。
- [x] 更新 README，运行桌面/窄屏浏览器流程，验证没有失效按钮和资源。

## 4. 交付验证

- [x] 功能测试、旧数据库迁移、全部页面、CSV 往返通过。
- [x] 源码行数对比、无 Android 修改、无意外本地文件进入改动。
- [x] 提供运行中的本地预览、准确改动摘要与验证结果。
