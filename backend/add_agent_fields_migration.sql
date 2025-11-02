-- 添加Agent相关字段到ai_configs表
-- Add Agent-related fields to ai_configs table

-- 添加 enable_agent 字段
ALTER TABLE ai_configs
ADD COLUMN enable_agent BOOLEAN DEFAULT TRUE;

-- 添加 max_tool_iterations 字段
ALTER TABLE ai_configs
ADD COLUMN max_tool_iterations INTEGER DEFAULT 5;

-- 更新现有记录
UPDATE ai_configs
SET enable_agent = TRUE,
    max_tool_iterations = 5
WHERE enable_agent IS NULL;
