# Bug修复总结 - 题号显示问题

## 问题描述

错题本和收藏列表中的题号显示为 `null` 或列表序号（1, 2, 3），而不是题库中的真实题号（如45, 78等）。

## 根本原因

**字段名不匹配**：

- **数据库模型**（`question_models_v2.py`）中字段名是：`question_number`
- **后端API代码**中错误使用的是：`question.number`

```python
# ❌ 错误的代码
question_number=question.number if hasattr(question, 'number') else None

# ✅ 正确的代码
question_number=question.question_number if hasattr(question, 'question_number') else None
```

## 诊断过程

1. **检查API响应**：通过Flutter日志发现API返回的 `question_number` 字段为 `null`
2. **检查后端代码**：发现字段访问使用了错误的名称 `question.number`
3. **检查数据库模型**：确认正确的字段名是 `question_number`

## 修复的文件

### 1. `backend/app/api/v1/wrong_questions.py`

修复了两处：
- `list_wrong_questions` 函数（行111）
- `get_wrong_question` 函数（行177）

```python
# 修复前
question_number=question.number if hasattr(question, 'number') else None

# 修复后
question_number=question.question_number if hasattr(question, 'question_number') else None
```

### 2. `backend/app/api/v1/favorites.py`

修复了一处：
- `list_favorites` 函数（行131）

```python
# 修复前
question_number=question.number if hasattr(question, 'number') else None

# 修复后
question_number=question.question_number if hasattr(question, 'question_number') else None
```

## 验证结果

从API日志中可以看到：

**修复前**：
```json
{
  "question_number": null,  // ❌ 返回null
  "question_type": "multiple",
  "question_stem": "邓小平理论的历史地位是()。"
}
```

**预期修复后**：
```json
{
  "question_number": 45,  // ✅ 返回真实题号
  "question_type": "multiple",
  "question_stem": "邓小平理论的历史地位是()。"
}
```

## 其他发现

✅ **好消息**：`question_options` 字段已经正常工作，API返回了完整的选项数据：

```json
{
  "question_options": [
    {
      "label": "A",
      "content": "对马克思列宁主义的继承和发展",
      "is_correct": true
    },
    {
      "label": "B",
      "content": "对毛泽东思想的继承和发展",
      "is_correct": true
    },
    ...
  ]
}
```

这意味着：
1. **选项显示功能已经完全工作** ✅
2. **只需要修复字段名问题** ✅

## 影响范围

修复后，以下功能将正常工作：

1. ✅ 错题本列表显示真实题号
2. ✅ 错题详情页面标题显示正确题号
3. ✅ 收藏列表显示真实题号
4. ✅ 收藏详情页面标题显示正确题号
5. ✅ 错题详情页面显示题目选项（A、B、C、D）
6. ✅ 正确答案显示为绿色高亮

## 部署说明

**重要提示**：这个修复只需要更新后端代码，Flutter端代码不需要修改。

### 部署步骤

1. 提交代码到git仓库
2. SSH到远程服务器：`ssh user@exam.shaynechen.tech`
3. 拉取最新代码：`git pull origin dev_2.0`
4. 重启后端服务：`sudo systemctl restart exam-backend`
5. 验证API返回的 `question_number` 不再为 `null`

### 验证命令

```bash
# 替换YOUR_TOKEN为实际token
TOKEN="your_token_here"
BANK_ID="9ccfb869-9d3c-4a4c-a114-3c21148c9e53"

curl -X GET "https://exam.shaynechen.tech/api/v1/wrong-questions?bank_id=$BANK_ID&limit=1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.wrong_questions[0].question_number'

# 应该返回一个数字（如45、78等），而不是null
```

## 经验教训

1. **始终验证字段名称**：在访问数据库模型字段时，应该先查看模型定义确认正确的字段名
2. **使用IDE的自动补全**：现代IDE会提示正确的字段名，避免此类错误
3. **添加单元测试**：应该为API响应添加测试，确保所有必需字段都不为null
4. **实时监控API日志**：通过查看实际的API响应可以快速定位问题

## 相关文档

- [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) - 完整的部署检查清单
- [diagnose_api.sh](./diagnose_api.sh) - API诊断脚本
