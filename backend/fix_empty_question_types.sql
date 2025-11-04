-- Fix questions with empty type values
-- 修复题目类型为空的问题

-- First, check how many questions have empty type
SELECT COUNT(*) as empty_type_count
FROM questions_v2
WHERE type = '' OR type IS NULL;

-- Show the affected questions
SELECT id, stem, type, created_at
FROM questions_v2
WHERE type = '' OR type IS NULL
LIMIT 10;

-- Update all questions with empty type to 'single' as default
-- You may want to manually review and set proper types based on the question content
UPDATE questions_v2
SET type = 'single'
WHERE type = '' OR type IS NULL;

-- Verify the fix
SELECT type, COUNT(*) as count
FROM questions_v2
GROUP BY type;
