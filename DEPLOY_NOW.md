# 立即部署 - 关键Bug修复

## 修复总结

本次部署修复了3个关键问题：

### 1. ✅ 题号显示为null的问题（已修复）

**问题**：错题本和收藏列表中题号显示为null
**原因**：字段名不匹配 - 使用了 `question.number` 而不是 `question.question_number`
**影响文件**：
- `backend/app/api/v1/wrong_questions.py` - 2处修改
- `backend/app/api/v1/favorites.py` - 1处修改

### 2. ✅ 错题练习只显示2道题的问题（已修复）

**问题**：错题练习只显示未订正的题目，而不是所有错题
**原因**：代码中有 `UserWrongQuestion.corrected == False` 过滤条件
**影响文件**：
- `backend/app/api/v1/practice.py` - 移除了 `corrected == False` 过滤

### 3. ✅ 题目选项显示功能（已完成）

**新功能**：错题详情页面显示题目选项（A、B、C、D）
**影响文件**：
- `backend/app/api/v1/wrong_questions.py` - 添加选项序列化
- `backend/app/schemas/wrong_questions_schemas.py` - 添加 `question_options` 字段
- `flutter_app/lib/data/models/wrong_question_model.dart` - 添加字段
- `flutter_app/lib/presentation/screens/wrong_questions/question_review_screen.dart` - 添加UI

## 已修复的文件列表

### 后端文件（需要部署）

1. **backend/app/api/v1/wrong_questions.py**
   - 行111：`question.number` → `question.question_number`
   - 行177：`question.number` → `question.question_number`
   - 行90-121：添加选项序列化代码
   - 行156-186：添加选项序列化代码

2. **backend/app/api/v1/favorites.py**
   - 行131：`question.number` → `question.question_number`

3. **backend/app/api/v1/practice.py**
   - 行89-98：移除 `UserWrongQuestion.corrected == False` 过滤条件
   - 添加了调试日志

4. **backend/app/schemas/wrong_questions_schemas.py**
   - 行32：添加 `question_number: Optional[int]`
   - 行41：添加 `question_options: Optional[List[Dict[str, Any]]]`

5. **backend/app/schemas/favorites_schemas.py**
   - 行40：添加 `question_number: Optional[int]`

### Flutter文件（已生成代码）

1. **flutter_app/lib/data/models/wrong_question_model.dart**
   - 添加 `questionOptions` 字段

2. **flutter_app/lib/data/models/wrong_question_model.g.dart**
   - 自动生成的序列化代码（已更新）

3. **flutter_app/lib/presentation/screens/wrong_questions/question_review_screen.dart**
   - 添加 `_buildQuestionOptions()` 方法显示选项

## 部署步骤

### 步骤1: 提交代码到git

```bash
cd /Users/shaynechen/shayne/demo/EXAM-MASTER

# 查看修改的文件
git status

# 添加所有修改
git add backend/app/api/v1/wrong_questions.py
git add backend/app/api/v1/favorites.py
git add backend/app/api/v1/practice.py
git add backend/app/schemas/wrong_questions_schemas.py
git add backend/app/schemas/favorites_schemas.py
git add flutter_app/lib/data/models/wrong_question_model.dart
git add flutter_app/lib/data/models/wrong_question_model.g.dart
git add flutter_app/lib/presentation/screens/wrong_questions/question_review_screen.dart

# 提交
git commit -m "修复关键bug：题号显示、错题练习数量、选项显示

- 修复question_number字段名不匹配问题（question.number -> question.question_number）
- 修复错题练习只显示未订正题目的问题（移除corrected==False过滤）
- 添加题目选项显示功能（question_options字段和UI）
- 添加调试日志用于问题排查

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

# 推送到远程
git push origin dev_2.0
```

### 步骤2: 在测试服务器上部署

```bash
# SSH到测试服务器
ssh user@exam.shaynechen.tech

# 进入项目目录
cd /path/to/EXAM-MASTER

# 拉取最新代码
git fetch origin
git pull origin dev_2.0

# 查看最近的提交确认更新
git log --oneline -3

# 重启后端服务
sudo systemctl restart exam-backend

# 或使用supervisor
# sudo supervisorctl restart exam-backend

# 查看服务状态
sudo systemctl status exam-backend

# 查看日志确认启动成功
tail -f /var/log/exam-backend.log
# 或
journalctl -u exam-backend -f
```

### 步骤3: 验证修复

**验证1: 题号显示**
```bash
# 使用curl测试（替换YOUR_TOKEN）
TOKEN="your_token_here"
BANK_ID="9ccfb869-9d3c-4a4c-a114-3c21148c9e53"

curl -X GET "https://exam.shaynechen.tech/api/v1/wrong-questions?bank_id=$BANK_ID&limit=1" \
  -H "Authorization: Bearer $TOKEN" | jq '.wrong_questions[0].question_number'

# 应该返回一个数字（如32、25等），而不是null
```

**验证2: 错题练习数量**
```bash
curl -X POST "https://exam.shaynechen.tech/api/v1/practice/sessions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"bank_id":"'$BANK_ID'","mode":"wrong_only"}' | jq '.total_questions'

# 应该返回6（所有错题），而不是2（只有未订正的）
```

**验证3: 选项显示**
```bash
curl -X GET "https://exam.shaynechen.tech/api/v1/wrong-questions?bank_id=$BANK_ID&limit=1" \
  -H "Authorization: Bearer $TOKEN" | jq '.wrong_questions[0].question_options'

# 应该返回选项数组，包含label、content、is_correct字段
```

**验证4: 在Flutter应用中测试**

打开Flutter应用，测试以下功能：
- [ ] 错题本列表显示真实题号（第32题、第25题等）
- [ ] 错题练习显示所有6道题（进度1/6而不是1/2）
- [ ] 点击错题查看详情，显示选项A、B、C、D
- [ ] 正确答案显示绿色高亮
- [ ] 错题订正功能正常工作

## 关键代码变更

### 1. question_number字段修复

```python
# 修改前（错误）
question_number=question.number if hasattr(question, 'number') else None

# 修改后（正确）
question_number=question.question_number if hasattr(question, 'question_number') else None
```

### 2. 错题练习过滤修复

```python
# 修改前（只获取未订正的）
query = db.query(UserWrongQuestion.question_id).filter(
    and_(
        UserWrongQuestion.user_id == user_id,
        UserWrongQuestion.bank_id == bank_id,
        UserWrongQuestion.corrected == False  # ← 这行已删除
    )
)

# 修改后（获取所有错题）
query = db.query(UserWrongQuestion.question_id).filter(
    and_(
        UserWrongQuestion.user_id == user_id,
        UserWrongQuestion.bank_id == bank_id
        # 移除了 corrected == False 条件
    )
)
```

### 3. 选项显示功能

```python
# 添加选项序列化
options_list = []
if hasattr(question, 'options') and question.options:
    for opt in question.options:
        options_list.append({
            "label": opt.option_label,
            "content": opt.option_content,
            "is_correct": opt.is_correct if hasattr(opt, 'is_correct') else False
        })

# 在Response中包含选项
WrongQuestionWithDetailsResponse(
    # ... 其他字段
    question_options=options_list if options_list else None
)
```

## 预期结果

部署后，用户将看到：

1. ✅ 错题列表显示真实题号："第 32 题"、"第 25 题"、"第 21 题"
2. ✅ 错题练习包含所有6道题：进度 "1/6"、"2/6" ... "6/6"
3. ✅ 错题详情显示完整选项列表，正确答案绿色高亮
4. ✅ 收藏列表也显示真实题号

## 回滚方案

如果部署后出现问题，可以快速回滚：

```bash
# 回滚到上一个commit
git reset --hard HEAD~1

# 或回滚到特定commit
git log --oneline -10  # 查找之前的commit hash
git reset --hard <commit_hash>

# 重启服务
sudo systemctl restart exam-backend
```

## 辅助文件

以下文件已创建用于调试和文档：
- `DEPLOYMENT_CHECKLIST.md` - 完整部署检查清单
- `BUGFIX_SUMMARY.md` - Bug修复详细说明
- `diagnose_api.sh` - API诊断脚本
- `test_wrong_questions_api.sh` - 错题API测试脚本
- `DEBUG_GUIDE.md` - 调试指南

## 注意事项

⚠️ **重要**:
- 本次修复只涉及后端代码，Flutter端代码已经正确处理null值
- 部署后需要重启后端服务才能生效
- 建议先在测试环境验证，确认无误后再部署到生产环境
- 数据库中的 `question_number` 字段需要有值，否则仍会显示为null

## 数据库检查（可选）

如果部署后 `question_number` 仍然为null，检查数据库：

```sql
-- 检查题目表是否有question_number字段
PRAGMA table_info(questions_v2);

-- 检查是否有题目没有question_number
SELECT COUNT(*) FROM questions_v2 WHERE question_number IS NULL;

-- 如果很多题目的question_number为null，需要更新数据
-- （这需要根据实际情况处理，可能需要从导入数据中恢复）
```
