# EXAM-MASTER Backend API

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![API Version](https://img.shields.io/badge/API-v2.0-blue.svg)

[English](#english) | [中文](#中文)

---

## 中文

EXAM-MASTER 是一个基于 FastAPI 构建的现代化题库管理系统后端API服务。系统提供了完整的题库管理、用户认证、学习记录跟踪、AI辅助等功能的RESTful API接口。

### 🌟 核心特性

#### 🏗️ 架构设计
- **RESTful API**: 遵循REST设计原则的标准化API
- **模块化设计**: 清晰的模块划分，易于扩展和维护
- **异步处理**: 基于FastAPI的异步请求处理，高性能
- **自动文档**: 自动生成的交互式API文档（Swagger/ReDoc）
- **版本管理**: API版本控制，支持平滑升级

#### 🔐 安全认证
- **JWT认证**: 基于JWT Token的无状态认证
- **密码加密**: 使用bcrypt进行密码哈希
- **权限控制**: 基于角色的访问控制（RBAC）
- **会话管理**: 安全的会话管理和Token刷新机制

#### 📚 题库管理
- **多格式导入**: 支持CSV、Excel、Word、PDF等格式
- **题型支持**: 单选题、多选题、判断题、填空题、简答题
- **资源管理**: 支持题目包含图片、音频、视频等多媒体资源
- **版本控制**: 题库版本管理，支持回滚和对比
- **批量操作**: 批量导入、导出、更新、删除

#### 🤖 AI功能
- **LLM集成**: 集成大语言模型API
- **智能解析**: AI自动解析题目答案
- **题目生成**: 基于模板的AI题目生成
- **内容优化**: AI辅助题目内容优化
- **模板系统**: 可自定义的Prompt模板

#### 📊 数据管理
- **SQLAlchemy ORM**: 强大的ORM支持
- **数据库迁移**: Alembic数据库版本管理
- **事务管理**: 完善的事务处理机制
- **数据验证**: Pydantic模型验证
- **缓存支持**: Redis缓存层（可选）

### 💻 技术栈

- **框架**: FastAPI 0.104.1
- **语言**: Python 3.8+
- **ORM**: SQLAlchemy 2.0.23
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **认证**: python-jose[cryptography] 3.3.0
- **密码**: passlib[bcrypt] 1.7.4
- **验证**: pydantic 2.5.0
- **迁移**: alembic 1.12.1
- **文件处理**: pandas, openpyxl, python-docx, pymupdf
- **异步**: aiofiles 23.2.1
- **HTTP客户端**: httpx 0.25.2
- **任务队列**: celery 5.3.4 (可选)
- **缓存**: redis 5.0.1 (可选)

### 🚀 快速开始

#### 环境要求
- Python 3.8 或更高版本
- pip 包管理器
- SQLite3 (开发环境)
- PostgreSQL (生产环境，可选)

#### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/yourusername/EXAM-MASTER.git
   cd EXAM-MASTER/backend
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate  # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **环境配置**
   
   创建 `.env` 文件：
   ```env
   # 数据库配置
   DATABASE_URL=sqlite:///./databases/exam_master.db
   # DATABASE_URL=postgresql://user:password@localhost/exam_master  # PostgreSQL

   # 安全配置
   SECRET_KEY=your-secret-key-here-change-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # CORS配置
   BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

   # 文件上传
   MAX_UPLOAD_SIZE=10485760  # 10MB
   ALLOWED_EXTENSIONS=csv,xlsx,xls,docx,pdf,txt,json


   ```

5. **初始化数据库**
   ```bash
   # 创建数据库表
   python init_database_v2.py
   
   # 创建管理员账号
   python init_admin.py
   
   # 初始化LLM模板（如果使用AI功能）
   python init_llm_templates.py
   ```

6. **运行服务**
   ```bash
   # 开发模式
   python run.py
   
   # 或使用uvicorn直接运行
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # 生产模式
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

7. **访问API文档**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - 管理后台: http://localhost:8000/admin (简易HTML界面)

### 📂 项目结构

```
backend/
├── app/                        # 应用主目录
│   ├── __init__.py
│   ├── main.py                # FastAPI应用入口
│   ├── api/                   # API路由
│   │   ├── v1/                # API v1版本
│   │   │   ├── auth.py        # 认证相关接口
│   │   │   ├── users.py       # 用户管理接口
│   │   │   ├── llm.py         # AI功能接口
│   │   │   └── qbank/         # 题库相关接口
│   │   │       ├── banks.py   # 题库管理
│   │   │       ├── questions.py # 题目管理
│   │   │       ├── imports.py # 导入功能
│   │   │       └── resources.py # 资源管理
│   │   └── v2/                # API v2版本（开发中）
│   ├── core/                  # 核心配置
│   │   ├── config.py          # 应用配置
│   │   ├── database.py        # 数据库连接
│   │   └── security.py        # 安全相关
│   ├── models/                # 数据库模型
│   │   ├── user_models.py     # 用户模型
│   │   ├── question_models.py # 题目模型
│   │   ├── question_models_v2.py # 新版题目模型
│   │   └── llm_models.py      # AI相关模型
│   ├── schemas/               # Pydantic模式
│   │   ├── auth_schemas.py    # 认证模式
│   │   ├── user_schemas.py    # 用户模式
│   │   ├── question_schemas.py # 题目模式
│   │   └── llm_schemas.py     # AI模式
│   └── services/              # 业务逻辑
│       ├── question_bank_service.py # 题库服务
│       ├── llm_service.py      # AI服务
│       ├── llm_service_v2.py   # AI服务v2
│       └── template_loader.py  # 模板加载器
├── databases/                 # 数据库文件目录
├── storage/                   # 文件存储目录
│   └── question_banks/        # 题库资源存储
├── prompt_templates/          # AI Prompt模板
│   ├── system/               # 系统模板
│   └── user/                 # 用户模板
├── docs/                      # 项目文档
│   ├── API_USAGE_REPORT.md   # API使用报告
│   └── NEW_ARCHITECTURE.md   # 新架构设计
├── tests/                     # 测试文件
│   ├── test_all_apis.py      # API测试
│   └── TEST_REPORT.md        # 测试报告
├── requirements.txt           # Python依赖
├── init_database_v2.py        # 数据库初始化脚本
├── init_admin.py              # 管理员初始化脚本
├── init_llm_templates.py      # LLM模板初始化
└── run.py                     # 应用启动脚本
```

### 🔧 API接口文档

#### 认证模块 `/api/v1/auth`

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| POST | `/login` | 用户登录 | 否 |
| POST | `/register` | 用户注册 | 否 |
| POST | `/refresh` | 刷新Token | 是 |
| GET | `/me` | 获取当前用户信息 | 是 |
| POST | `/logout` | 用户登出 | 是 |

#### 用户管理 `/api/v1/users`

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| GET | `/` | 获取用户列表 | 是(管理员) |
| GET | `/{user_id}` | 获取用户详情 | 是 |
| PUT | `/{user_id}` | 更新用户信息 | 是 |
| DELETE | `/{user_id}` | 删除用户 | 是(管理员) |
| POST | `/{user_id}/password` | 修改密码 | 是 |

#### 题库管理 `/api/v1/qbank`

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| GET | `/banks` | 获取题库列表 | 是 |
| POST | `/banks` | 创建题库 | 是 |
| GET | `/banks/{bank_id}` | 获取题库详情 | 是 |
| PUT | `/banks/{bank_id}` | 更新题库 | 是 |
| DELETE | `/banks/{bank_id}` | 删除题库 | 是 |
| POST | `/banks/{bank_id}/import` | 导入题目 | 是 |
| GET | `/banks/{bank_id}/export` | 导出题库 | 是 |

#### 题目管理 `/api/v1/qbank/questions`

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| GET | `/` | 获取题目列表 | 是 |
| POST | `/` | 创建题目 | 是 |
| GET | `/{question_id}` | 获取题目详情 | 是 |
| PUT | `/{question_id}` | 更新题目 | 是 |
| DELETE | `/{question_id}` | 删除题目 | 是 |
| POST | `/{question_id}/resources` | 上传资源 | 是 |
| GET | `/search` | 搜索题目 | 是 |
| POST | `/batch` | 批量操作 | 是 |

#### AI功能 `/api/v1/llm`

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| POST | `/analyze` | 分析题目 | 是 |
| POST | `/generate` | 生成题目 | 是 |
| POST | `/optimize` | 优化题目 | 是 |
| GET | `/templates` | 获取模板列表 | 是 |
| POST | `/templates` | 创建模板 | 是 |

### 📊 数据模型

#### User Model
```python
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "is_active": "boolean",
  "is_admin": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### Question Bank Model
```python
{
  "id": "uuid",
  "name": "string",
  "description": "string",
  "version": "string",
  "category": "string",
  "total_questions": "integer",
  "created_by": "uuid",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### Question Model
```python
{
  "id": "uuid",
  "bank_id": "uuid",
  "question_number": "integer",
  "stem": "string",
  "stem_format": "text|markdown|latex|html",
  "type": "single|multiple|boolean|fill|essay",
  "options": [
    {
      "id": "string",
      "content": "string",
      "is_correct": "boolean"
    }
  ],
  "answer": "string",
  "explanation": "string",
  "difficulty": "easy|medium|hard",
  "tags": ["string"],
  "resources": [
    {
      "type": "image|audio|video",
      "url": "string"
    }
  ],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### 🧪 测试

运行测试：
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_all_apis.py

# 运行测试并生成覆盖率报告
pytest --cov=app tests/
```

### 🚢 部署

#### Docker部署
```dockerfile
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

构建并运行：
```bash
docker build -t exam-master-api .
docker run -d -p 8000:8000 --name exam-api exam-master-api
```

#### 使用Docker Compose
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db/exam_master
    depends_on:
      - db
    volumes:
      - ./storage:/app/storage

  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=exam_master
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 🔄 更新日志

#### v2.0.0 (2025-08)
- 🚀 完全重构为FastAPI框架
- 🏗️ 新的模块化架构设计
- 🔐 JWT认证系统
- 🤖 集成LLM功能
- 📚 新的题库管理系统
- 📊 增强的数据模型
- 🧪 完整的测试覆盖

#### v1.0.0 (2025-05)
- 初始版本发布
- 基础题库管理功能
- 用户认证系统
- CSV导入导出

### 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 📝 开发规范

- 遵循 PEP 8 Python 代码风格指南
- 使用 Black 进行代码格式化
- 使用 Flake8 进行代码检查
- 编写单元测试覆盖新功能
- 更新API文档

### 🐛 问题反馈

如果您发现任何问题或有改进建议，请：
1. 查看 [Issues](https://github.com/yourusername/EXAM-MASTER/issues) 是否已有相关问题
2. 创建新的 Issue 并详细描述问题
3. 如果可能，提供复现步骤

---

## English

EXAM-MASTER is a modern question bank management system backend API service built with FastAPI. The system provides complete RESTful API interfaces for question bank management, user authentication, learning record tracking, AI assistance, and more.

### 🌟 Core Features

#### 🏗️ Architecture Design
- **RESTful API**: Standardized API following REST design principles
- **Modular Design**: Clear module separation for easy extension and maintenance
- **Async Processing**: High-performance async request handling based on FastAPI
- **Auto Documentation**: Auto-generated interactive API documentation (Swagger/ReDoc)
- **Version Management**: API versioning for smooth upgrades

#### 🔐 Security & Authentication
- **JWT Authentication**: Stateless authentication based on JWT tokens
- **Password Encryption**: Password hashing using bcrypt
- **Access Control**: Role-Based Access Control (RBAC)
- **Session Management**: Secure session management and token refresh mechanism

#### 📚 Question Bank Management
- **Multi-format Import**: Support for CSV, Excel, Word, PDF formats
- **Question Types**: Single choice, multiple choice, true/false, fill-in-blank, essay
- **Resource Management**: Support for multimedia resources (images, audio, video)
- **Version Control**: Question bank versioning with rollback and comparison
- **Batch Operations**: Bulk import, export, update, delete

#### 🤖 AI Features
- **LLM Integration**: Integrated large language model APIs
- **Smart Analysis**: AI-powered automatic answer analysis
- **Question Generation**: Template-based AI question generation
- **Content Optimization**: AI-assisted question content optimization
- **Template System**: Customizable prompt templates

#### 📊 Data Management
- **SQLAlchemy ORM**: Powerful ORM support
- **Database Migration**: Alembic database version management
- **Transaction Management**: Complete transaction handling
- **Data Validation**: Pydantic model validation
- **Cache Support**: Redis cache layer (optional)

### 💻 Technology Stack

- **Framework**: FastAPI 0.104.1
- **Language**: Python 3.8+
- **ORM**: SQLAlchemy 2.0.23
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: python-jose[cryptography] 3.3.0
- **Password**: passlib[bcrypt] 1.7.4
- **Validation**: pydantic 2.5.0
- **Migration**: alembic 1.12.1
- **File Processing**: pandas, openpyxl, python-docx, pymupdf
- **Async**: aiofiles 23.2.1
- **HTTP Client**: httpx 0.25.2
- **Task Queue**: celery 5.3.4 (optional)
- **Cache**: redis 5.0.1 (optional)

### 🚀 Quick Start

#### Requirements
- Python 3.8 or higher
- pip package manager
- SQLite3 (development)
- PostgreSQL (production, optional)

#### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/EXAM-MASTER.git
   cd EXAM-MASTER/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   
   Create `.env` file:
   ```env
   # Database configuration
   DATABASE_URL=sqlite:///./databases/exam_master.db
   # DATABASE_URL=postgresql://user:password@localhost/exam_master  # PostgreSQL

   # Security configuration
   SECRET_KEY=your-secret-key-here-change-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # CORS configuration
   BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

   # File upload
   MAX_UPLOAD_SIZE=10485760  # 10MB
   ALLOWED_EXTENSIONS=csv,xlsx,xls,docx,pdf,txt,json

   # AI configuration (optional)
   OPENAI_API_KEY=your-openai-api-key
   LLM_MODEL=gpt-3.5-turbo
   ```

5. **Initialize database**
   ```bash
   # Create database tables
   python init_database_v2.py
   
   # Create admin account
   python init_admin.py
   
   # Initialize LLM templates (if using AI features)
   python init_llm_templates.py
   ```

6. **Run the service**
   ```bash
   # Development mode
   python run.py
   
   # Or run directly with uvicorn
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Production mode
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

7. **Access API documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Admin Panel: http://localhost:8000/admin (simple HTML interface)

### 🧪 Testing

Run tests:
```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_all_apis.py

# Run tests with coverage report
pytest --cov=app tests/
```

### 🚢 Deployment

#### Docker Deployment
```dockerfile
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t exam-master-api .
docker run -d -p 8000:8000 --name exam-api exam-master-api
```

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 👥 Author

- **Developer**: ShayneChen
- **Email**: [xinyu-c@outlook.com](mailto:xinyu-c@outlook.com)
- **GitHub**: [CiE-XinYuChen](https://github.com/CiE-XinYuChen)

---

⭐ **If you find this project helpful, please give it a star!**