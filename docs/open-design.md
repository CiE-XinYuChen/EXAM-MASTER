# Open Design 设计来源

本次前端由 Open Design 桌面应用生成原生 HTML / CSS / JavaScript 设计，再接入 Flask 的真实题库与学习记录。

- 项目名称：EXAM MASTER 中文学习工作台
- 项目 ID：`f679bddc-9162-40aa-89eb-bf8ebf3d2c47`
- 会话 ID：`29556d23-a3a4-405b-a3f5-a464bbea4e5d`
- 生成日期：2026-09-05
- 原始交付：`index.html`、`styles.css`、`app.js`、`DESIGN.md`
- 本机设计源目录：`/Users/shaynechen/Library/Application Support/Open Design/namespaces/release-stable/data/projects/f679bddc-9162-40aa-89eb-bf8ebf3d2c47/`

## 采用的设计

冷白背景、深墨文字、蓝色主操作和系统字体；220px 桌面侧栏，手机底部导航与展开菜单。题库用表格组织信息，600px 以下改为题目卡片；答题区保留较大的字号与清晰的正确/错误反馈。

`static/style.css` 以 Open Design 的共享样式为基础；`templates/_icons.html` 使用它生成的 SVG 图标。登录、概览、题库、练习、考试和记录页沿用同一套布局、颜色与组件。

## 接入真实应用

原型的示例题、浏览器模拟登录和客户端数据管理已替换为 Python / SQLite。列表使用 Jinja 循环，导航使用真实页面地址，提交、判分、导入和记录持久化集中在后端。JavaScript 负责导航、输入辅助、删除确认、手机考试翻题、计时与练习/考试共用草稿。

实际业务以当前项目为准：

- 题库显示真实 881 题，不混入原型的 16 道示例题。
- 保留现有登录、多用户学习记录、随机未答、顺序续答、错题与收藏复习。
- CSV 同题号更新，结构错误整批拒绝；内容不完整的原题保留为待补全。
- 填空按原文字顺序匹配；多选不考虑选择顺序。
- 考试开始保存题目快照，提交结果保存在数据库中，刷新可重新查看。

原型完整源文件保留在 Open Design 项目中，应用不再携带原型的客户端数据实现。

## 手机单手操作迭代

根据用户后续要求，在项目内调整现有设计：常见题目一屏作答，短题选项靠近下半屏，底部固定收藏与主操作；考试一次显示一道题，答题卡从底部展开。统计移到题库列表后，筛选按需展开，新增/导入/导出放在底部更多菜单。沿用上述 Open Design 视觉基础，没有新增前端框架或后端接口。

具体尺寸、交互验证与实机边界见 [手机适配验收](superpowers/plans/2026-09-05-mobile-ergonomics.md)。
