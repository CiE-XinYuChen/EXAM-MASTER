# API 文档结构说明

本文档说明了整理后的 FastAPI 文档 (/api/docs) 的结构和组织方式。

## 文档访问地址

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## API 路由结构

### 1. API v1 (`/api/v1`) - 核心业务接口

#### 🔐 Authentication (认证)
- `/api/v1/auth` - 用户登录、注册、令牌管理

#### 👥 Users (用户管理)
- `/api/v1/users` - 用户信息、权限管理

#### 📚 Question Banks (题库管理)
- `/api/v1/qbank/banks` - 题库 CRUD 操作
- `/api/v1/qbank/questions` - 题目管理
- `/api/v1/qbank/options` - 选项管理
- `/api/v1/qbank/resources` - 多媒体资源管理
- `/api/v1/qbank/import` - 导入导出功能

#### ✏️ Practice Sessions (练习会话)
- `/api/v1/practice` - 创建、继续、提交练习会话

#### ⭐ Favorites (收藏功能)
- `/api/v1/favorites` - 收藏题目管理

#### ❌ Wrong Questions (错题本)
- `/api/v1/wrong-questions` - 错题记录和复习

#### 📊 Statistics (统计分析)
- `/api/v1/statistics` - 学习数据统计

#### 🤖 LLM Management (AI 功能)
- `/api/v1/llm` - LLM 配置和管理
- `/api/v1/ai-chat` - AI 对话功能

#### 🔑 Activation Codes (激活码)
- `/api/v1/activation` - 激活码验证和管理

---

### 2. API v2 (`/api/v2`) - 新版接口

#### 🔐 Authentication
- `/api/v2/auth` - 认证接口（复用 v1）

#### 👥 Users
- `/api/v2/users` - 用户管理（复用 v1）

#### 📚 Question Banks
- `/api/v2/qbank` - 题库管理（V2 重构版本）

#### 📝 Exams & Practice
- `/api/v2/exams` - 考试和练习功能

#### 📥 Import/Export
- `/api/v2/import-export` - 导入导出操作

#### 🤖 LLM Management
- `/api/v2/llm` - AI 功能管理

#### 🔧 System Administration
- `/api/v2/` - 系统管理接口

---

### 3. MCP API (`/api/mcp`) - AI 集成

- `/api/mcp` - Model Context Protocol 接口

---

### 4. Admin Panel (管理后台) - 前端页面

#### 🏠 Admin - Dashboard (仪表盘)
- `/admin` - 管理后台首页
- `/admin/login` - 登录/登出

#### 👥 Admin - Users (用户管理)
- `/admin/users` - 用户列表
- `/admin/users/create` - 创建用户
- `/admin/users/{id}/edit` - 编辑用户
- `/admin/users/{id}/password` - 修改密码
- `/admin/users/{id}/statistics` - 用户统计

#### 📚 Admin - Question Banks (题库管理)
- `/admin/qbanks` - 题库列表
- `/admin/qbanks/create` - 创建题库
- `/admin/qbanks/{id}/edit` - 编辑题库
- `/admin/qbanks/{id}/delete` - 删除题库

#### ❓ Admin - Questions (题目管理)
- `/admin/questions` - 题目列表
- `/admin/questions/create` - 创建题目
- `/admin/questions/{id}/edit` - 编辑题目
- `/admin/questions/{id}/preview` - 预览题目
- `/admin/questions/{id}/resources/upload` - 上传多媒体

#### 🔑 Admin - Activation (激活码管理)
- `/admin/activation-codes` - 激活码列表（页面）
- `/admin/api/activation-codes` - 激活码 API（CRUD）

#### 🤖 Admin - AI Config (AI 配置)
- `/admin/ai-configs` - AI 配置列表
- `/admin/ai-configs/test-api` - 测试 API
- `/admin/ai-configs/test-chat` - 测试对话

#### 🧪 Admin - Agent Testing (Agent 测试)
- `/admin/agent-test` - Agent 测试页面

#### 📦 Admin - Legacy Import/Export (旧版导入导出)
- `/admin/v2/imports/{bank_id}` - 导入题目
- `/admin/v2/exports/{bank_id}` - 导出题目

---

### 5. System & Public (系统和公共接口)

#### 🔧 System Status (系统状态)
- `/` - API 根路径信息
- `/health` - 健康检查

#### 📁 Public Resources (公共资源)
- `/resources/{resource_id}` - 访问公共资源文件

---

## 整理内容总结

### ✅ 已完成的整理

1. **移除重复路由**
   - 删除了 v1 API 中重复注册的 MCP 路由
   - MCP 现在只在 `/api/mcp` 路径注册一次

2. **统一标签命名**
   - 所有 Admin 路由使用 `Admin - XXX` 格式
   - API 路由使用简洁的 emoji + 名称格式
   - 标签命名保持一致性

3. **优化分组**
   - Admin 后台按功能模块分组
   - API 按业务逻辑分组
   - 便于在 Swagger UI 中查找

4. **清理冗余**
   - 移除过长的描述
   - 统一 emoji 使用
   - 保持简洁明了

### 📋 标签规范

- **API 接口**: `🔐 Authentication`, `📚 Question Banks` 等
- **管理后台**: `🏠 Admin - Dashboard`, `👥 Admin - Users` 等
- **系统接口**: `🔧 System Status`
- **公共资源**: `📁 Public Resources`

### 🎯 最佳实践

1. **新增路由时**，请按照现有的命名规范添加 tags
2. **Admin 路由** 必须以 `Admin -` 开头
3. **API 路由** 使用 emoji + 简短英文名称
4. **避免重复注册** 同一个 router

---

## 维护建议

1. 定期检查是否有重复的路由注册
2. 新增功能时保持标签命名一致性
3. 使用有意义的 emoji 帮助视觉识别
4. 保持文档结构清晰，便于 API 使用者理解

---

**更新时间**: 2025-11-06
**整理人**: Claude Code
