# 用户端API验证报告

## 检查日期
2025-11-02

## 检查范围
验证普通用户（非管理员）通过API访问题目和多媒体资源的权限和功能是否正常。

---

## 1. 题目访问API

### 1.1 获取题库列表
**端点**: `GET /api/v1/qbank/banks`
**认证**: 需要JWT Token (`get_current_user`)
**权限检查**: ✅ 正常
- 返回用户可访问的题库（公开题库 + 用户创建的题库）
- 代码位置: `app/api/v1/qbank_v2.py:53-84`

### 1.2 获取题库详情
**端点**: `GET /api/v1/qbank/banks/{bank_id}`
**认证**: 需要JWT Token (`get_current_user`)
**权限检查**: ✅ 正常
- 检查题库是否公开或用户是否为创建者
- 代码位置: `app/api/v1/qbank_v2.py:84-124`

### 1.3 获取题库中的题目列表
**端点**: `GET /api/v1/qbank/banks/{bank_id}/questions`
**认证**: 需要JWT Token (`get_current_user`)
**权限检查**: ✅ 正常
```python
# 权限检查逻辑 (app/api/v1/qbank_v2.py:206-207)
if not bank.is_public and bank.creator_id != current_user.id:
    raise HTTPException(status_code=403, detail="无权访问该题库")
```
**支持参数**:
- `skip`: 分页偏移量
- `limit`: 返回数量限制 (1-200)
- `type`: 题目类型过滤
- `difficulty`: 难度过滤

**返回数据**: 包含题目的完整信息，包括：
- 题干 (`stem`)
- 选项 (`options`)
- 难度 (`difficulty`)
- 分类 (`category`)
- 元数据 (`meta_data`)
- 多媒体标识 (`has_images`, `has_audio`, `has_video`)

### 1.4 获取单个题目详情
**端点**: `GET /api/v1/qbank/questions/{question_id}`
**认证**: 需要JWT Token (`get_current_user`)
**权限检查**: ✅ 正常
```python
# 权限检查逻辑 (app/api/v1/qbank_v2.py:233-235)
bank = question.bank
if not bank.is_public and bank.creator_id != current_user.id:
    raise HTTPException(status_code=403, detail="无权访问该题目")
```

---

## 2. 多媒体资源访问

### 2.1 公共资源访问端点
**端点**: `GET /resources/{resource_id}`
**认证**: ❌ **无需认证** (公开访问)
**状态**: ✅ 正常工作
**代码位置**: `app/main.py:1921-1955`

**功能说明**:
- 通过资源UUID直接访问多媒体文件
- 支持图片、视频、音频等所有资源类型
- UUID (36字符) 提供了足够的安全性
- 适用于学生在考试/练习中访问题目资源

**响应头**:
```python
headers={
    "Cache-Control": "public, max-age=31536000",  # 缓存1年
    "Access-Control-Allow-Origin": "*"  # 允许跨域访问
}
```

### 2.2 资源URL格式
在题干、选项、解析中，资源以Markdown格式嵌入：
- 图片: `![图片](/resources/{resource_id})`
- 视频: `[视频](/resources/{resource_id})`
- 音频: `[音频](/resources/{resource_id})`

前端需要将Markdown转换为HTML媒体标签进行渲染。

---

## 3. 题目响应数据结构

### QuestionResponse Schema
```python
class QuestionResponse(QuestionBase):
    id: str                          # 题目UUID
    bank_id: str                     # 所属题库ID
    question_number: Optional[int]   # 题号
    stem: str                        # 题干（可能包含资源Markdown）
    type: QuestionTypeEnum           # 题目类型
    difficulty: DifficultyEnum       # 难度
    category: str                    # 分类
    explanation: str                 # 解析（可能包含资源Markdown）
    options: List[OptionData]        # 选项列表（选项内容可能包含资源）
    has_images: bool                 # 是否包含图片
    has_audio: bool                  # 是否包含音频
    has_video: bool                  # 是否包含视频
    meta_data: Optional[Dict]        # 元数据
    created_at: datetime
    updated_at: Optional[datetime]
```

### OptionData Schema
```python
class OptionData(BaseModel):
    label: str                       # 选项标签 (A, B, C, D...)
    content: str                     # 选项内容（可能包含资源Markdown）
    is_correct: bool                 # 是否正确答案
```

**注意**: 正确答案信息 (`is_correct`) 在题目API中默认返回。如果需要在考试场景下隐藏答案，需要前端或后端进行额外处理。

---

## 4. 安全性评估

### 4.1 权限控制 ✅
- ✅ 用户只能访问公开题库或自己创建的题库
- ✅ 题目访问会检查所属题库的权限
- ✅ 资源访问通过UUID实现安全隔离（UUID的随机性使得暴力枚举不可行）

### 4.2 资源访问安全 ✅
- ✅ 资源ID使用36字符UUID，难以猜测
- ✅ 资源URL不暴露文件系统路径
- ✅ 支持跨域访问，方便前端应用使用
- ✅ 长期缓存策略提升性能

### 4.3 潜在问题 ⚠️
**问题1**: 考试场景下答案泄露
- 当前API返回的题目数据包含 `is_correct` 字段
- 建议：考试场景下，后端应过滤掉正确答案信息

**建议修复**:
```python
# 在考试模式下，创建一个新的响应模型
class QuestionResponseNoAnswer(QuestionBase):
    # ... 其他字段相同
    options: List[OptionDataNoAnswer]  # 不包含is_correct字段
```

---

## 5. 使用流程示例

### 场景：学生答题流程

#### 步骤1: 用户登录获取Token
```bash
POST /api/v1/auth/login
{
  "username": "student@example.com",
  "password": "password123"
}

# 返回
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 步骤2: 获取可访问的题库列表
```bash
GET /api/v1/qbank/banks
Authorization: Bearer {token}

# 返回题库列表（包含公开题库和用户创建的题库）
```

#### 步骤3: 获取题库中的题目
```bash
GET /api/v1/qbank/banks/{bank_id}/questions?limit=10
Authorization: Bearer {token}

# 返回题目列表，包含题干、选项、资源引用
```

#### 步骤4: 渲染题目并访问资源
前端解析题干中的资源Markdown：
```javascript
// 题干内容示例
stem: "这是一道题目\n![图片](/resources/abc-123-uuid)\n请选择正确答案"

// 前端渲染为
<p>这是一道题目</p>
<img src="http://api.example.com/resources/abc-123-uuid" alt="图片">
<p>请选择正确答案</p>
```

资源请求：
```bash
GET /resources/abc-123-uuid
# 无需Token，直接返回图片文件
```

---

## 6. 测试建议

### 6.1 功能测试
1. ✅ 测试用户能否访问公开题库
2. ✅ 测试用户能否访问自己创建的题库
3. ✅ 测试用户无法访问其他用户的私有题库
4. ✅ 测试资源URL能否被未认证用户访问
5. ⚠️ 测试考试场景下答案是否被隐藏（需要实现）

### 6.2 性能测试
1. 测试资源缓存是否生效
2. 测试大量并发资源访问的性能
3. 测试视频/音频等大文件的加载速度

### 6.3 安全测试
1. 测试是否能通过猜测UUID访问未授权资源
2. 测试CORS策略是否正确配置
3. 测试资源访问的速率限制（如需要）

---

## 7. 总结

### ✅ 正常工作的功能
1. 用户API端点权限控制正确
2. 公共资源访问端点正常工作
3. 资源URL安全性良好（UUID保护）
4. 跨域访问配置正确
5. 缓存策略合理

### ⚠️ 需要注意的问题
1. **考试场景答案泄露**：当前API会返回正确答案，考试时需要过滤
2. **资源访问日志**：建议添加访问日志用于审计
3. **速率限制**：建议为资源访问添加速率限制防止滥用

### 📋 建议改进
1. 为考试场景创建专门的API端点，不返回答案
2. 添加资源访问统计功能
3. 考虑实现资源访问的临时Token机制（可选）
4. 添加资源文件类型和大小的白名单验证

---

## 8. 结论

**总体评估**: ✅ **用户端API工作正常**

普通用户通过API访问题目和资源的功能已经正确实现，权限控制合理，资源访问安全。主要需要在考试场景下额外处理答案隐藏的问题。

多媒体资源通过公共端点 `/resources/{resource_id}` 可以被任何人访问（包括未登录用户），这对于学生答题场景是合适的设计，因为：
1. UUID提供了足够的安全性（36字符，难以暴力枚举）
2. 简化了前端实现（无需在每个资源请求中携带Token）
3. 支持浏览器缓存，提升性能

如果需要更严格的访问控制，可以考虑：
1. 实现基于考试会话的临时访问Token
2. 记录资源访问日志用于审计
3. 添加IP白名单或速率限制
