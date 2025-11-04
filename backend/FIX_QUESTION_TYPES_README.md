# 修复题目类型问题

## 问题描述
数据库中存在一些题目的 `type` 字段为空字符串 `''`，导致查询时出现以下错误：
```
LookupError: '' is not among the defined enum values. Enum name: questiontype
```

## 已实施的代码修复

### 1. 服务器端验证（main.py）
在题目创建和编辑接口中添加了验证：
- 检查 type 字段不能为空
- 验证 type 必须是有效的枚举值之一

### 2. 枚举处理增强（question_models_v2.py）
增强了 `QuestionType` 枚举的 `_missing_` 方法：
- 处理空字符串，返回默认值（single）
- 记录警告日志
- 允许查询继续进行

## 数据库修复方案

### 方案1: 使用Python脚本（推荐）
```bash
cd /root/demo/EXAM-MASTER/backend
python fix_question_types.py
```

### 方案2: 使用SQL脚本
如果是SQLite数据库：
```bash
cd /root/demo/EXAM-MASTER/backend
sqlite3 qbank.db < fix_empty_question_types.sql
```

如果是PostgreSQL：
```bash
psql -d your_database_name -f fix_empty_question_types.sql
```

### 方案3: 手动SQL
连接数据库后执行：
```sql
-- 查看有多少题目类型为空
SELECT COUNT(*) FROM questions_v2 WHERE type = '' OR type IS NULL;

-- 更新所有空类型为 'single'
UPDATE questions_v2 SET type = 'single' WHERE type = '' OR type IS NULL;

-- 验证修复结果
SELECT type, COUNT(*) as count FROM questions_v2 GROUP BY type;
```

## 重启服务器
修复完数据库后，需要重启FastAPI服务器以应用代码更改：
```bash
# 停止当前服务
pkill -f uvicorn

# 重新启动服务
cd /root/demo/EXAM-MASTER/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 验证修复
1. 访问管理后台的题目列表页面
2. 尝试创建各种类型的题目（单选、多选、填空、问答等）
3. 确认不再出现 QuestionType 枚举错误

## 预防措施
代码已更新，后续不会再出现此问题：
- ✅ 前端表单验证要求选择题目类型
- ✅ 后端API验证拒绝空类型
- ✅ 枚举处理器优雅处理无效值
