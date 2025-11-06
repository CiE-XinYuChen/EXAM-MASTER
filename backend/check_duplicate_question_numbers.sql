-- 检查题库中重复的题号
-- 查找每个题库中是否有重复的question_number

SELECT
    bank_id,
    question_number,
    COUNT(*) as count
FROM questions_v2
WHERE question_number IS NOT NULL
  AND question_number > 0
GROUP BY bank_id, question_number
HAVING COUNT(*) > 1
ORDER BY bank_id, question_number;

-- 查看具体的重复题目详情
SELECT
    id,
    bank_id,
    question_number,
    type,
    stem,
    created_at
FROM questions_v2
WHERE (bank_id, question_number) IN (
    SELECT bank_id, question_number
    FROM questions_v2
    WHERE question_number IS NOT NULL AND question_number > 0
    GROUP BY bank_id, question_number
    HAVING COUNT(*) > 1
)
ORDER BY bank_id, question_number, created_at;
