# EXAM-MASTER API 文档

## 概述

EXAM-MASTER 提供了完整的 RESTful API 接口，支持题库管理、用户管理、LLM集成等功能。

- **基础URL**: `http://localhost:8000`
- **API版本**: v2
- **API前缀**: `/api/v2`
- **文档地址**: `/api/docs` (Swagger UI)
- **管理面板**: `/admin`

## 认证方式

系统使用 JWT (JSON Web Token) 进行身份验证：

1. 通过 `/api/v2/auth/login` 获取令牌
2. 在请求头中添加: `Authorization: Bearer <token>`
3. 令牌有效期: 24小时

## API 端点分类

### 1. 公开端点（无需认证）

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/` | API状态信息 |
| GET | `/health` | 健康检查 |
| POST | `/api/v2/auth/login` | 用户登录 |
| POST | `/api/v2/auth/register` | 用户注册 |
| GET | `/api/v2/llm/templates/presets` | 获取预设模板 |

### 2. 用户端点（需要认证）

#### 认证相关
| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/v2/auth/me` | 获取当前用户信息 |
| POST | `/api/v2/auth/change-password` | 修改密码 |
| POST | `/api/v2/auth/logout` | 登出 |

#### 题库操作
| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/v2/qbank/banks` | 获取题库列表 |
| GET | `/api/v2/qbank/banks/{bank_id}` | 获取题库详情 |
| GET | `/api/v2/qbank/banks/{bank_id}/questions` | 获取题目列表 |
| GET | `/api/v2/qbank/questions/{question_id}` | 获取题目详情 |
| GET | `/api/v2/qbank/categories` | 获取分类列表 |
| GET | `/api/v2/qbank/search` | 搜索题目 |

#### 资源访问
| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/v2/qbank/resources/{resource_id}` | 获取资源文件 |

### 3. 题库创建者端点（需要认证 + 创建者权限）

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/v2/qbank/banks` | 创建题库 |
| PUT | `/api/v2/qbank/banks/{bank_id}` | 更新题库 |
| DELETE | `/api/v2/qbank/banks/{bank_id}` | 删除题库 |
| POST | `/api/v2/qbank/banks/{bank_id}/questions` | 添加题目 |
| PUT | `/api/v2/qbank/questions/{question_id}` | 更新题目 |
| DELETE | `/api/v2/qbank/questions/{question_id}` | 删除题目 |
| POST | `/api/v2/qbank/questions/{question_id}/images` | 上传题目图片 |
| POST | `/api/v2/qbank/banks/{bank_id}/export` | 导出题库 |
| POST | `/api/v2/qbank/import` | 导入题库 |
| POST | `/api/v2/qbank/banks/{bank_id}/duplicate` | 复制题库 |
| GET | `/api/v2/qbank/banks/{bank_id}/stats` | 题库统计 |

### 4. LLM 管理端点（需要认证）

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/v2/llm/interfaces` | 获取LLM接口列表 |
| POST | `/api/v2/llm/interfaces` | 创建LLM接口 |
| GET | `/api/v2/llm/interfaces/{interface_id}` | 获取接口详情 |
| PUT | `/api/v2/llm/interfaces/{interface_id}` | 更新接口配置 |
| DELETE | `/api/v2/llm/interfaces/{interface_id}` | 删除接口 |
| POST | `/api/v2/llm/interfaces/{interface_id}/test` | 测试接口 |
| GET | `/api/v2/llm/templates` | 获取模板列表 |
| POST | `/api/v2/llm/templates` | 创建模板 |
| GET | `/api/v2/llm/templates/{template_id}` | 获取模板详情 |
| PUT | `/api/v2/llm/templates/{template_id}` | 更新模板 |
| DELETE | `/api/v2/llm/templates/{template_id}` | 删除模板 |
| POST | `/api/v2/llm/parse` | 解析题目 |
| POST | `/api/v2/llm/import` | 批量导入解析题目 |

### 5. 管理员端点（需要管理员权限）

#### 用户管理 API
| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/v2/users/` | 获取用户列表 |
| GET | `/api/v2/users/{user_id}` | 获取用户详情 |
| PUT | `/api/v2/users/{user_id}` | 更新用户信息 |
| DELETE | `/api/v2/users/{user_id}` | 删除用户 |
| GET | `/api/v2/users/{user_id}/permissions` | 获取用户权限 |
| POST | `/api/v2/users/{user_id}/permissions` | 授予权限 |
| DELETE | `/api/v2/users/{user_id}/permissions/{bank_id}` | 撤销权限 |

#### 系统统计 API
| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/v2/qbank/stats/users` | 用户统计 |
| GET | `/api/v2/qbank/stats/banks` | 题库统计 |
| GET | `/api/v2/qbank/stats/questions` | 题目统计 |

### 6. 管理面板路由（Web界面）

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | `/admin` | 管理面板首页 | 管理员 |
| GET/POST | `/admin/login` | 管理员登录 | 公开 |
| GET | `/admin/logout` | 退出登录 | 管理员 |
| **用户管理** |
| GET | `/admin/users` | 用户列表 | 管理员 |
| GET/POST | `/admin/users/create` | 创建用户 | 管理员 |
| GET/POST | `/admin/users/{id}/edit` | 编辑用户 | 管理员 |
| GET/POST | `/admin/users/{id}/password` | 修改密码 | 管理员 |
| POST | `/admin/users/{id}/delete` | 删除用户 | 管理员 |
| **题库管理** |
| GET | `/admin/qbanks` | 题库列表 | 管理员 |
| GET/POST | `/admin/qbanks/create` | 创建题库 | 管理员 |
| GET/POST | `/admin/qbanks/{id}/edit` | 编辑题库 | 管理员 |
| POST | `/admin/qbanks/{id}/delete` | 删除题库 | 管理员 |
| **题目管理** |
| GET | `/admin/questions` | 题目列表 | 管理员 |
| GET/POST | `/admin/questions/create` | 创建题目 | 管理员 |
| GET | `/admin/questions/{id}/preview` | 预览题目 | 管理员 |
| GET/POST | `/admin/questions/{id}/edit` | 编辑题目 | 管理员 |
| POST | `/admin/questions/{id}/delete` | 删除题目 | 管理员 |
| **导入导出** |
| GET | `/admin/imports` | 导入导出页面 | 管理员 |
| POST | `/admin/imports/csv` | CSV导入 | 管理员 |
| GET | `/admin/imports/template` | 下载模板 | 管理员 |
| GET | `/admin/exports/{bank_id}` | 导出题库 | 管理员 |
| **LLM配置** |
| GET | `/admin/llm` | LLM配置页面 | 管理员 |

## 数据格式

### 请求格式
- Content-Type: `application/json`
- 文件上传: `multipart/form-data`

### 响应格式
```json
{
    "status": "success|error",
    "data": {},
    "message": "操作消息"
}
```

### 错误响应
```json
{
    "detail": "错误信息",
    "status_code": 400
}
```

## 权限说明

### 用户角色

1. **学生 (student)**
   - 查看公开题库
   - 答题练习
   - 查看个人记录

2. **教师 (teacher)**
   - 学生所有权限
   - 创建和管理自己的题库
   - 导入导出题目
   - 使用LLM功能

3. **管理员 (admin)**
   - 所有权限
   - 用户管理
   - 系统配置
   - 查看系统统计

### 题库权限

- **read**: 查看题库和题目
- **write**: 添加、修改题目
- **admin**: 完全控制题库

## 题目类型

系统支持以下题目类型：

- `single`: 单选题
- `multiple`: 多选题
- `judge`: 判断题
- `fill`: 填空题
- `essay`: 问答题

## 导入导出格式

### CSV格式
```csv
题号,题干,A,B,C,D,答案,难度,题型,解析
1,示例题目,选项A,选项B,选项C,选项D,A,easy,单选,这是解析
```

### JSON格式
```json
{
    "bank_info": {
        "name": "题库名称",
        "description": "题库描述"
    },
    "questions": [
        {
            "stem": "题目内容",
            "type": "single",
            "options": [
                {"label": "A", "content": "选项A", "is_correct": true},
                {"label": "B", "content": "选项B", "is_correct": false}
            ],
            "explanation": "解析"
        }
    ]
}
```

## 使用示例

### 1. 用户登录
```bash
curl -X POST http://localhost:8000/api/v2/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### 2. 获取题库列表
```bash
curl -X GET http://localhost:8000/api/v2/qbank/banks \
  -H "Authorization: Bearer <token>"
```

### 3. 创建题库
```bash
curl -X POST http://localhost:8000/api/v2/qbank/banks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "数学题库",
    "description": "高中数学练习题",
    "category": "数学",
    "is_public": true
  }'
```

## 注意事项

1. 所有需要认证的端点都需要在请求头中包含有效的JWT令牌
2. 文件上传大小限制：10MB
3. API请求频率限制：100次/分钟（可配置）
4. 建议在生产环境中使用HTTPS
5. 定期备份数据库

## 更新历史

- v2.0.0 (2024-01) - 完整重构，新增LLM支持
- v1.0.0 (2023-12) - 初始版本