# 考试系统管理控制台

基于Flask的管理后台，用于管理考试系统的用户、题库和题目。

## 功能特性

- **用户管理**: 创建、编辑、删除用户，角色管理（管理员/教师/学生）
- **权限管理**: 分配和管理用户对题库的访问权限
- **题库管理**: 创建、编辑、删除题库，设置公开/私有状态
- **题目管理**: 添加、编辑、删除题目，支持多种题型
- **导入导出**: 支持CSV和JSON格式的题目批量导入导出
- **统计分析**: 系统概览和使用统计

## 安装运行

### 1. 安装依赖

```bash
cd backend_admin
pip install -r requirements.txt
```

### 2. 配置环境变量

编辑 `.env` 文件，设置以下配置：

```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
API_BASE_URL=http://localhost:8000/api/v1
```

### 3. 启动后端API服务

确保后端API服务正在运行：

```bash
cd ../backend
python run.py
```

### 4. 启动管理控制台

```bash
cd backend_admin
python app.py
```

访问 http://localhost:5000

## 默认账户

- 用户名: admin
- 密码: admin123

## 技术栈

- **后端框架**: Flask 3.0
- **认证**: Flask-Login
- **模板引擎**: Jinja2
- **样式**: 纯CSS（无框架依赖）
- **API通信**: Requests

## 项目结构

```
backend_admin/
├── app.py              # Flask主应用
├── requirements.txt    # Python依赖
├── .env               # 环境配置
├── app/
│   ├── routes/        # 路由模块
│   │   ├── auth.py    # 认证路由
│   │   ├── users.py   # 用户管理
│   │   ├── qbanks.py  # 题库管理
│   │   ├── questions.py # 题目管理
│   │   └── imports.py # 导入导出
│   ├── services/      # 服务层
│   │   └── api_client.py # API客户端
│   └── utils/         # 工具模块
│       └── auth.py    # 认证工具
├── templates/         # HTML模板
│   ├── base.html     # 基础模板
│   ├── dashboard.html # 仪表盘
│   ├── auth/         # 认证页面
│   ├── users/        # 用户管理页面
│   ├── qbanks/       # 题库管理页面
│   └── imports/      # 导入导出页面
└── static/           # 静态资源
    ├── css/          # 样式文件
    └── js/           # JavaScript文件
```

## API对接

管理控制台通过HTTP API与后端服务通信，主要接口包括：

- `/api/v1/auth/*` - 认证相关
- `/api/v1/users/*` - 用户管理
- `/api/v1/qbank/banks/*` - 题库管理
- `/api/v1/qbank/questions/*` - 题目管理
- `/api/v1/qbank/import/*` - 导入导出

## 开发说明

### 添加新功能

1. 在 `app/routes/` 中创建新的路由模块
2. 在 `templates/` 中创建对应的HTML模板
3. 在 `app.py` 中注册新的Blueprint
4. 更新导航菜单（`templates/base.html`）

### 自定义样式

所有样式定义在 `static/css/style.css` 中，可根据需要修改。

## 注意事项

1. 生产环境请修改 `SECRET_KEY`
2. 确保后端API服务可访问
3. 建议使用HTTPS部署
4. 定期备份数据库