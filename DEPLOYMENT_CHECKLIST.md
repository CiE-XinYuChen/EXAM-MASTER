# 部署检查清单 - Deployment Checklist

## 需要部署的后端更改

### 1. ✅ 错题本API修复 (backend/app/api/v1/wrong_questions.py)

**修改位置**: 行 90-110

**修改内容**:
```python
# 在 list_wrong_questions 函数中
wrong_questions_with_details.append(WrongQuestionWithDetailsResponse(
    # ... 其他字段
    question_number=question.number if hasattr(question, 'number') else None,  # 新增
    question_type=question.type.value if hasattr(question.type, 'value') else str(question.type),  # 修改
    question_stem=question.stem,
    question_difficulty=question.difficulty.value if (question.difficulty and hasattr(question.difficulty, 'value')) else (question.difficulty if isinstance(question.difficulty, str) else None),  # 修改
    # ... 其他字段
))
```

**修改位置**: 行 145-165

**修改内容**:
```python
# 在 get_wrong_question 函数中，返回时添加
return WrongQuestionWithDetailsResponse(
    # ... 其他字段
    question_number=question.number if hasattr(question, 'number') else None,  # 新增
    # ... 其他字段
)
```

### 2. ✅ 收藏API修复 (backend/app/api/v1/favorites.py)

**修改位置**: 行 124-139

**修改内容**:
```python
favorites_with_question.append(FavoriteWithQuestionResponse(
    # ... 其他字段
    question_number=question.number if hasattr(question, 'number') else None,  # 新增
    question_type=question.type.value if hasattr(question.type, 'value') else str(question.type),  # 修改
    question_difficulty=question.difficulty.value if (question.difficulty and hasattr(question.difficulty, 'value')) else (question.difficulty if isinstance(question.difficulty, str) else None),  # 修改
    # ... 其他字段
))
```

### 3. ✅ Schema更新

**文件**: backend/app/schemas/wrong_questions_schemas.py
- 行 32: 添加 `question_number: Optional[int]`

**文件**: backend/app/schemas/favorites_schemas.py
- 行 40: 添加 `question_number: Optional[int]`

### 4. ✅ 错题练习模式修复 (backend/app/api/v1/practice.py)

**修改位置**: 行 85-93

**修改内容**:
```python
if mode == PracticeMode.wrong_only:
    # 错题模式：获取所有错题（包括已订正和未订正）
    query = db.query(UserWrongQuestion.question_id).filter(
        and_(
            UserWrongQuestion.user_id == user_id,
            UserWrongQuestion.bank_id == bank_id
            # 移除了 UserWrongQuestion.corrected == False 这一行
        )
    )
```

### 5. ✅ 添加调试日志 (backend/app/api/v1/practice.py)

**修改位置**: 行 75-87

**修改内容**:
```python
def get_question_ids_for_session(
    db: Session,
    bank_id: str,
    user_id: int,
    mode: PracticeMode,
    question_types: Optional[List[str]] = None,
    difficulty: Optional[str] = None
) -> List[str]:
    """根据模式和筛选条件获取题目ID列表"""

    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Getting question IDs: mode={mode}, user_id={user_id}, bank_id={bank_id}")
```

**修改位置**: 行 97-98 和 108-114

**修改内容**:
```python
# 在 wrong_only 模式后添加
question_ids = [q[0] for q in query.all()]
logger.info(f"Wrong questions mode: found {len(question_ids)} questions")

# 在 favorite_only 模式后添加
question_ids = [q[0] for q in query.all()]
logger.info(f"Favorite mode: found {len(question_ids)} questions")

if not question_ids:
    total_favorites = db.query(UserFavorite).filter(UserFavorite.user_id == user_id).count()
    logger.warning(f"No favorites found for bank_id={bank_id}, but user has {total_favorites} total favorites")
```

## 部署步骤

### 第1步: 在远程服务器上更新代码

```bash
# SSH到远程服务器
ssh user@exam.shaynechen.tech

# 进入项目目录
cd /path/to/EXAM-MASTER

# 确认当前在dev_2.0分支
git branch

# 拉取最新代码
git fetch origin
git pull origin dev_2.0

# 查看最近的提交，确认更新已拉取
git log --oneline -5
```

### 第2步: 重启后端服务

```bash
# 方法1: 使用systemd
sudo systemctl restart exam-backend
sudo systemctl status exam-backend

# 方法2: 使用supervisor
sudo supervisorctl restart exam-backend
sudo supervisorctl status exam-backend

# 方法3: 如果使用screen/tmux
ps aux | grep uvicorn
kill <PID>
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
```

### 第3步: 验证部署

#### 测试1: 检查错题本API是否返回question_number

```bash
# 使用curl测试 (替换YOUR_TOKEN和BANK_ID)
TOKEN="your_token_here"
BANK_ID="9ccfb869-9d3c-4a4c-a114-3c21148c9e53"

curl -X GET "https://exam.shaynechen.tech/api/v1/wrong-questions?bank_id=$BANK_ID&limit=3" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.wrong_questions[0].question_number'

# 应该返回一个数字，而不是null
```

#### 测试2: 检查收藏API是否返回question_number

```bash
curl -X GET "https://exam.shaynechen.tech/api/v1/favorites?bank_id=$BANK_ID&limit=3" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.favorites[0].question_number'

# 应该返回一个数字，而不是null
```

#### 测试3: 检查错题练习会话创建

```bash
curl -X POST "https://exam.shaynechen.tech/api/v1/practice/sessions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"bank_id\": \"$BANK_ID\", \"mode\": \"wrong_only\"}" | jq '.total_questions'

# 应该返回所有错题的数量（例如10），而不是只有未订正的数量（例如2）
```

#### 测试4: 查看后端日志

```bash
# 查看最近的日志
tail -f /var/log/exam-backend.log

# 或使用journalctl
journalctl -u exam-backend -f

# 应该看到类似的日志:
# INFO: Getting question IDs: mode=PracticeMode.wrong_only, user_id=1, bank_id=...
# INFO: Wrong questions mode: found 10 questions
```

## 验证清单

部署完成后，在Flutter应用中测试：

- [ ] 错题本列表显示真实题号（不是1、2、3）
- [ ] 错题详情页面标题显示正确题号（不是"第 ? 题"）
- [ ] 错题练习显示所有错题（进度应该是"1/10"而不是"1/2"）
- [ ] 收藏列表显示真实题号
- [ ] 收藏详情页面标题显示正确题号
- [ ] 错题订正功能正常工作（可以标记为已订正/未订正）
- [ ] 收藏练习能正常加载题目（不显示"暂无题目"）

## 已知问题和解决方案

### 问题1: 题号显示为 "第 ? 题"

**原因**: 后端没有返回`question_number`字段，或返回为null

**解决方案**:
1. 确认远程服务器代码已更新
2. 检查数据库中的questions_v2表是否有number字段
3. 如果没有，运行数据库迁移或手动添加

```sql
-- 检查question表结构
PRAGMA table_info(questions_v2);

-- 如果没有number字段，添加（通常在创建题目时自动填充）
-- 这个字段应该在创建QuestionV2 model时就存在
```

### 问题2: 错题练习只显示2道题

**原因**: 后端代码中wrong_only模式仍然有`corrected == False`过滤条件

**解决方案**: 确认practice.py的修改已部署

### 问题3: 收藏练习显示"暂无题目"

**可能原因**:
1. 数据库中收藏记录的bank_id与当前题库不匹配
2. 用户没有收藏任何题目

**排查步骤**:
1. 查看后端日志中的调试信息
2. 检查数据库中的user_favorites表

```sql
-- 检查收藏记录
SELECT id, user_id, bank_id, question_id FROM user_favorites WHERE user_id = ?;

-- 检查是否有匹配的bank_id
SELECT COUNT(*) FROM user_favorites WHERE user_id = ? AND bank_id = ?;
```

## Flutter应用无需更改

所有Flutter端的代码已经正确实现，包括：
- 使用 `wrongQuestion.questionNumber ?? (index + 1)` 显示题号
- 使用 `favorite.questionNumber ?? (index + 1)` 显示题号
- 错题订正功能
- 收藏详情功能

只要后端API正确返回数据，Flutter应用就能正常工作。

## 紧急回滚方案

如果部署后出现问题，可以快速回滚：

```bash
# 回滚到上一个commit
git reset --hard HEAD~1

# 或回滚到特定commit
git reset --hard <commit_hash>

# 重启服务
sudo systemctl restart exam-backend
```
