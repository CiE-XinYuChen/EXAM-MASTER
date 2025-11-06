-- 修复题库中重复或缺失的题号
-- 为每个题库的题目重新分配连续的题号（按创建时间和ID排序）

-- 步骤1: 备份当前的question_number（可选）
-- CREATE TABLE questions_v2_backup AS SELECT * FROM questions_v2;

-- 步骤2: 使用窗口函数重新分配题号
WITH ranked_questions AS (
    SELECT
        id,
        bank_id,
        ROW_NUMBER() OVER (
            PARTITION BY bank_id
            ORDER BY
                CASE WHEN question_number IS NOT NULL AND question_number > 0
                     THEN question_number
                     ELSE 999999
                END,
                created_at,
                id
        ) as new_question_number
    FROM questions_v2
)
UPDATE questions_v2 q
SET question_number = rq.new_question_number
FROM ranked_questions rq
WHERE q.id = rq.id;

-- 步骤3: 验证修复结果
SELECT
    bank_id,
    COUNT(*) as total_questions,
    MIN(question_number) as min_number,
    MAX(question_number) as max_number,
    COUNT(DISTINCT question_number) as unique_numbers
FROM questions_v2
GROUP BY bank_id
ORDER BY bank_id;
