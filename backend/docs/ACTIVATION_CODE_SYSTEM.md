# 激活码系统说明文档

## 系统概述

激活码系统用于管理用户对题库的访问权限。管理员可以生成激活码，用户使用激活码激活题库后即可获得访问权限。

## 数据模型

### ActivationCode（激活码表）
- `id`: 激活码ID（UUID）
- `code`: 激活码字符串（16位，大写字母+数字，避免易混淆字符）
- `bank_id`: 关联的题库ID
- `created_by`: 创建者用户ID
- `created_at`: 创建时间
- `expire_type`: 过期类型（permanent=永久，temporary=临时）
- `expire_days`: 有效天数（临时激活码使用）
- `is_used`: 是否已使用
- `used_by`: 使用者用户ID
- `used_at`: 使用时间
- `description`: 激活码描述

### UserBankAccess（用户题库访问权限表）
- `id`: 记录ID（UUID）
- `user_id`: 用户ID
- `bank_id`: 题库ID
- `activated_by_code`: 激活码ID
- `activated_at`: 激活时间
- `expire_at`: 过期时间（None表示永久有效）
- `is_active`: 是否激活状态

## API端点

### 用户端API（JWT Token认证）

用于客户端（如Flutter App）调用，需要在请求头中携带JWT Token。

#### 1. 使用激活码激活题库
```
POST /api/v1/activation/activate
Authorization: Bearer <token>

请求体:
{
  "code": "激活码字符串"
}

响应:
{
  "success": true,
  "message": "成功激活题库：题库名称",
  "bank_id": "题库ID",
  "bank_name": "题库名称",
  "expire_at": "2024-12-31T23:59:59" or null,
  "activated_at": "2024-01-01T00:00:00"
}
```

#### 2. 查看我的题库访问权限
```
GET /api/v1/activation/my-access
Authorization: Bearer <token>

响应:
{
  "access_list": [
    {
      "id": "访问记录ID",
      "user_id": 1,
      "bank_id": "题库ID",
      "bank_name": "题库名称",
      "bank_description": "题库描述",
      "activated_by_code": "激活码ID",
      "activated_at": "2024-01-01T00:00:00",
      "expire_at": "2024-12-31T23:59:59" or null,
      "is_active": true,
      "is_expired": false
    }
  ],
  "total": 10,
  "active_count": 8,
  "expired_count": 2
}
```

#### 3. 检查题库访问权限
```
GET /api/v1/activation/check-access/{bank_id}
Authorization: Bearer <token>

响应:
{
  "has_access": true,
  "message": "您有权限访问该题库",
  "expire_at": "2024-12-31T23:59:59" or null
}
```

### 管理员API（Session Cookie认证）

用于Admin Panel调用，通过session cookie进行认证。

#### 1. 获取激活码列表
```
GET /admin/api/activation-codes?skip=0&limit=20&bank_id=xxx&is_used=false&expire_type=permanent&search=xxx
Credentials: include (自动携带session cookie)

响应:
{
  "codes": [
    {
      "id": "激活码ID",
      "code": "ABCD1234EFGH5678",
      "bank_id": "题库ID",
      "bank_name": "题库名称",
      "created_by": 1,
      "created_at": "2024-01-01T00:00:00",
      "expire_type": "permanent",
      "expire_days": null,
      "is_used": false,
      "used_by": null,
      "used_at": null,
      "description": "描述信息"
    }
  ],
  "total": 100,
  "used_count": 30,
  "unused_count": 70
}
```

#### 2. 生成激活码
```
POST /admin/api/activation-codes
Credentials: include
Content-Type: application/json

请求体:
{
  "bank_id": "题库ID",
  "expire_type": "permanent" or "temporary",
  "expire_days": 30,  // 临时激活码必填
  "count": 5,  // 生成数量
  "description": "描述信息"
}

响应: 生成的激活码列表（同获取列表的格式）
```

#### 3. 删除激活码
```
DELETE /admin/api/activation-codes/{code_id}
Credentials: include

响应:
{
  "success": true,
  "message": "激活码已删除"
}

注意：已使用的激活码不能删除
```

### Admin面板页面
```
GET /admin/activation-codes
```
激活码管理页面，提供可视化界面管理激活码。

## 使用流程

### 管理员生成激活码
1. 登录Admin Panel
2. 访问"激活码管理"页面
3. 点击"生成激活码"按钮
4. 选择题库、过期类型、有效天数等参数
5. 生成激活码，复制分发给用户

### 用户使用激活码
1. 用户登录客户端（Flutter App）
2. 在激活码输入页面输入激活码
3. 调用 `POST /api/v1/activation/activate` 接口
4. 激活成功后，用户即可访问该题库

### 访问权限验证
1. 客户端请求访问题库时
2. 调用 `GET /api/v1/activation/check-access/{bank_id}` 检查权限
3. 如果有权限且未过期，允许访问
4. 否则提示用户需要激活

## 安全考虑

1. **激活码唯一性**：生成时检查唯一性，避免冲突
2. **防止重复使用**：一个激活码只能使用一次
3. **权限检查**：用户只能激活一次同一题库
4. **过期控制**：支持永久和临时两种类型
5. **数据库隔离**：激活码和访问权限存储在qbank数据库

## 技术细节

### 认证方式分离
- **用户API**：使用JWT Token（`Authorization: Bearer <token>`）
  - 适用于客户端（Flutter App）
  - 通过 `get_current_user` 依赖注入

- **管理员API**：使用Session Cookie
  - 适用于Admin Panel网页
  - 通过 `admin_required` 依赖注入
  - 前端使用 `credentials: 'include'` 自动携带cookie

### 激活码生成规则
- 长度：16位字符
- 字符集：大写字母（A-Z，排除O、I、L）+ 数字（2-9，排除0、1）
- 避免易混淆字符，方便手动输入

### 数据库设计
- 激活码和访问权限表在 qbank 数据库
- user_id 字段引用主库的 users 表，但不建立外键约束（跨库）
- 使用 UUID 作为主键，便于分布式扩展

## 前端集成

### Admin Panel（activation_codes.html）
- 自动加载激活码列表
- 支持筛选（题库、状态、类型、搜索）
- 生成激活码对话框
- 复制激活码功能
- 删除未使用的激活码

### Flutter App（需要实现）
```dart
// 示例：激活题库
Future<ActivationResult> activateBank(String code) async {
  final response = await http.post(
    Uri.parse('$baseUrl/api/v1/activation/activate'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({'code': code}),
  );

  if (response.statusCode == 200) {
    return ActivationResult.fromJson(jsonDecode(response.body));
  } else {
    throw Exception('激活失败');
  }
}

// 示例：检查访问权限
Future<bool> checkBankAccess(String bankId) async {
  final response = await http.get(
    Uri.parse('$baseUrl/api/v1/activation/check-access/$bankId'),
    headers: {'Authorization': 'Bearer $token'},
  );

  if (response.statusCode == 200) {
    final result = jsonDecode(response.body);
    return result['has_access'] == true;
  }
  return false;
}
```

## 测试建议

1. **单元测试**
   - 激活码生成唯一性测试
   - 激活码使用一次性测试
   - 过期时间计算测试

2. **集成测试**
   - 管理员生成激活码流程
   - 用户使用激活码激活题库流程
   - 权限验证流程

3. **UI测试**
   - Admin Panel激活码管理页面
   - Flutter App激活码输入页面
   - 题库访问权限显示

## 未来扩展

1. **批量激活码导出**：支持CSV格式导出
2. **激活码统计**：使用率、激活趋势等
3. **激活码组**：一次性激活多个题库
4. **用户访问日志**：记录用户访问题库的详细日志
5. **权限续期**：管理员可以延长用户的访问权限
