# API调试指南 - Debug Guide

## 当前问题总结

根据用户反馈的截图，存在以下问题：

1. ✅ **错题本500错误** - 已修复（需要部署到远程服务器）
   - 文件: `backend/app/api/v1/wrong_questions.py`
   - 修复: 添加 `hasattr()` 检查和 `question_number` 字段

2. ✅ **收藏/错题列表题号显示问题** - 已修复（需要部署）
   - 文件: `backend/app/api/v1/favorites.py`, `backend/app/api/v1/wrong_questions.py`
   - 文件: `backend/app/schemas/favorites_schemas.py`, `backend/app/schemas/wrong_questions_schemas.py`
   - 修复: 添加 `question_number` 字段

3. ❌ **收藏练习显示"暂无题目"** - 需要调试
   - 症状: 点击收藏列表的"开始练习"后显示"暂无题目"
   - 可能原因:
     - 数据库中没有收藏数据
     - API返回的收藏列表为空
     - favorite_only模式的逻辑有问题

4. ❌ **进度条显示0%** - 需要调试
   - 症状: 进度条显示 "0/863, 0% 已完成"
   - 可能原因:
     - 统计API返回的数据不正确
     - 数据库中没有统计数据
     - 统计计算逻辑有问题

## 部署步骤

### 1. 确认代码已推送到Git

```bash
# 在本地机器上检查
git status
git log --oneline -5

# 确认所有更改已提交并推送
git push origin dev_2.0
```

### 2. 在远程服务器上更新代码

```bash
# SSH到远程服务器
ssh user@exam.shaynechen.tech

# 进入项目目录
cd /path/to/EXAM-MASTER

# 拉取最新代码
git fetch origin
git checkout dev_2.0
git pull origin dev_2.0

# 检查是否有新的更改
git log --oneline -5

# 重启后端服务
# 方法1: 如果使用systemd
sudo systemctl restart exam-backend

# 方法2: 如果使用supervisor
sudo supervisorctl restart exam-backend

# 方法3: 如果使用screen/tmux
# 先找到进程并kill，然后重新启动
ps aux | grep uvicorn
kill <PID>
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# 检查服务是否正常运行
curl -I https://exam.shaynechen.tech/api/v1/health
```

## 使用测试脚本调试API

我已经创建了一个测试脚本 `test_api.py`，可以帮助你快速测试远程API的各个功能。

### 运行测试脚本

```bash
cd /Users/shaynechen/shayne/demo/EXAM-MASTER

# 安装依赖（如果需要）
pip install requests

# 编辑脚本，填入你的token和bank_id
# 或者在运行时输入

# 运行测试
python3 test_api.py
```

### 测试脚本会检查以下功能：

1. **收藏列表API** (`/api/v1/favorites`)
   - 检查是否能获取收藏列表
   - 查看 `question_number` 字段是否存在
   - 确认收藏数量

2. **错题列表API** (`/api/v1/wrong-questions`)
   - 检查是否能获取错题列表
   - 查看 `question_number` 字段是否存在
   - 确认错题数量和未订正数量

3. **题库统计API** (`/api/v1/statistics/bank/{bankId}`)
   - 检查统计数据是否正确
   - 查看 `practiced_questions` 和 `total_questions`

4. **创建练习会话** (`/api/v1/practice/sessions`)
   - 测试 `favorite_only` 模式
   - 测试 `wrong_only` 模式
   - 检查返回的 `total_questions` 数量

## 手动测试API

### 获取Token

从Flutter应用中获取当前用户的token，或者使用登录API获取：

```bash
curl -X POST https://exam.shaynechen.tech/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

### 测试收藏列表

```bash
TOKEN="your_token_here"
BANK_ID="your_bank_id_here"

curl -X GET "https://exam.shaynechen.tech/api/v1/favorites?bank_id=$BANK_ID&limit=100" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### 测试错题列表

```bash
curl -X GET "https://exam.shaynechen.tech/api/v1/wrong-questions?bank_id=$BANK_ID&limit=100" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### 测试创建收藏练习会话

```bash
curl -X POST "https://exam.shaynechen.tech/api/v1/practice/sessions?resume_if_exists=true" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"bank_id\": \"$BANK_ID\",
    \"mode\": \"favorite_only\"
  }"
```

### 测试题库统计

```bash
curl -X GET "https://exam.shaynechen.tech/api/v1/statistics/bank/$BANK_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## 调试步骤

### Step 1: 验证后端部署

1. SSH到远程服务器
2. 检查后端代码是否是最新的
3. 查看后端日志是否有错误

```bash
# 查看最近的日志
tail -f /var/log/exam-backend.log

# 或者如果使用systemd
journalctl -u exam-backend -f

# 或者直接查看uvicorn输出
tail -f /path/to/backend/logs/uvicorn.log
```

### Step 2: 测试收藏功能

1. 使用测试脚本或curl命令测试收藏列表API
2. 检查返回的数据：
   - `total` 是否大于0？
   - `favorites` 数组是否有数据？
   - 每个favorite是否有 `question_number` 字段？

3. 如果收藏列表为空：
   - 检查数据库中是否有收藏数据
   - 确认用户ID和bank_id是否正确

### Step 3: 测试练习会话创建

1. 使用测试脚本测试创建 `favorite_only` 模式的会话
2. 检查响应：
   - 状态码是否为200或201？
   - `total_questions` 是否大于0？
   - 是否返回了 `session_id`？

3. 如果返回404 "没有找到符合条件的题目"：
   - 问题：数据库查询没有找到收藏的题目
   - 检查 `user_favorites` 表中是否有该用户和该题库的数据

### Step 4: 测试统计功能

1. 使用测试脚本测试统计API
2. 检查响应：
   - `total_questions` 是否正确（应该是863）？
   - `practiced_questions` 是否大于0？
   - `accuracy_rate` 是否有数值？

## 数据库检查

如果API返回的数据不正确，可能需要检查数据库：

```bash
# SSH到远程服务器
ssh user@exam.shaynechen.tech

# 进入项目目录
cd /path/to/EXAM-MASTER

# 使用SQLite命令行工具
sqlite3 qbank.db

# 检查收藏表
SELECT COUNT(*) FROM user_favorites WHERE user_id = YOUR_USER_ID;
SELECT * FROM user_favorites WHERE user_id = YOUR_USER_ID LIMIT 5;

# 检查错题表
SELECT COUNT(*) FROM user_wrong_questions WHERE user_id = YOUR_USER_ID;
SELECT * FROM user_wrong_questions WHERE user_id = YOUR_USER_ID LIMIT 5;

# 检查题目表
SELECT COUNT(*) FROM questions_v2 WHERE bank_id = 'YOUR_BANK_ID';

# 检查统计表
SELECT * FROM user_bank_statistics WHERE user_id = YOUR_USER_ID;

# 退出SQLite
.exit
```

## 常见问题排查

### 问题1: 收藏练习显示"暂无题目"

**可能原因:**
1. 数据库中没有该用户的收藏数据
2. favorite_only模式查询逻辑有问题
3. 用户token解析的user_id不正确

**排查步骤:**
1. 查看backend日志，确认收到的请求参数
2. 使用curl测试收藏列表API，确认有收藏数据
3. 使用curl测试创建favorite_only会话，查看返回结果
4. 检查数据库中的user_favorites表

### 问题2: 进度条显示0%

**可能原因:**
1. 统计数据没有被正确计算
2. user_bank_statistics表为空
3. API endpoint不正确

**排查步骤:**
1. 使用curl测试统计API
2. 检查数据库中的user_bank_statistics表
3. 如果表为空，可能需要触发统计计算（答题后自动更新）

### 问题3: 题号显示1,2,3而不是真实题号

**已修复，需要部署**

确认后端代码已经包含以下修改：
- `backend/app/schemas/favorites_schemas.py:40` 有 `question_number: Optional[int]`
- `backend/app/schemas/wrong_questions_schemas.py:32` 有 `question_number: Optional[int]`
- `backend/app/api/v1/favorites.py:131` 有 `question_number=question.number if hasattr(question, 'number') else None`
- `backend/app/api/v1/wrong_questions.py:101` 有 `question_number=question.number if hasattr(question, 'number') else None`

## 下一步

1. 首先在远程服务器上部署最新的后端代码
2. 运行test_api.py脚本，查看所有API的响应
3. 根据测试结果确定具体问题所在
4. 如果需要修改代码，修改后提交并重新部署

## 联系方式

如果遇到问题，请提供：
1. 测试脚本的完整输出
2. 后端日志的相关错误信息
3. 数据库查询的结果（如果可以访问）
4. Flutter应用的错误日志（AppLogger输出）
