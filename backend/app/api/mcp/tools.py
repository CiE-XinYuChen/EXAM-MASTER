"""
MCP Tools - 题库系统的MCP工具定义
让AI模型能够通过标准化工具访问题库数据
"""

from typing import List, Optional, Dict, Any, Callable
from pydantic import BaseModel, Field
from enum import Enum


# ==================== MCP Tool Definitions ====================

class MCPToolParameter(BaseModel):
    """MCP工具参数定义"""
    name: str
    type: str  # "string", "number", "boolean", "object", "array"
    description: str
    required: bool = False
    enum: Optional[List[str]] = None
    properties: Optional[Dict[str, Any]] = None  # For object types


class MCPTool(BaseModel):
    """MCP工具定义"""
    name: str
    description: str
    parameters: List[MCPToolParameter]
    handler: Optional[Callable] = None  # 工具的处理函数

    class Config:
        arbitrary_types_allowed = True


# ==================== Tool Definitions ====================

# 工具1: 获取题库列表
GET_QUESTION_BANKS = MCPTool(
    name="get_question_banks",
    description="获取用户有权限访问的题库列表",
    parameters=[
        MCPToolParameter(
            name="user_id",
            type="number",
            description="用户ID",
            required=True
        ),
        MCPToolParameter(
            name="include_stats",
            type="boolean",
            description="是否包含统计信息（总题数、已练习等）",
            required=False
        )
    ]
)

# 工具2: 获取题目列表
GET_QUESTIONS = MCPTool(
    name="get_questions",
    description="从指定题库获取题目列表，支持筛选和搜索",
    parameters=[
        MCPToolParameter(
            name="user_id",
            type="number",
            description="用户ID",
            required=True
        ),
        MCPToolParameter(
            name="bank_id",
            type="string",
            description="题库ID",
            required=True
        ),
        MCPToolParameter(
            name="question_types",
            type="array",
            description="题型筛选：single(单选), multiple(多选), judge(判断), fill(填空), essay(问答)",
            required=False
        ),
        MCPToolParameter(
            name="difficulty",
            type="string",
            description="难度筛选",
            required=False,
            enum=["easy", "medium", "hard", "expert"]
        ),
        MCPToolParameter(
            name="mode",
            type="string",
            description="获取模式",
            required=False,
            enum=["all", "wrong_only", "favorite_only", "unpracticed"]
        ),
        MCPToolParameter(
            name="search",
            type="string",
            description="关键词搜索（题干内容）",
            required=False
        ),
        MCPToolParameter(
            name="limit",
            type="number",
            description="返回题目数量限制",
            required=False
        )
    ]
)

# 工具3: 获取单个题目详情
GET_QUESTION_DETAIL = MCPTool(
    name="get_question_detail",
    description="获取指定题目的完整信息，不包含答案（用于答题）",
    parameters=[
        MCPToolParameter(
            name="user_id",
            type="number",
            description="用户ID",
            required=True
        ),
        MCPToolParameter(
            name="question_id",
            type="string",
            description="题目ID",
            required=True
        ),
        MCPToolParameter(
            name="include_history",
            type="boolean",
            description="是否包含用户的答题历史",
            required=False
        )
    ]
)

# 工具4: 提交答案
SUBMIT_ANSWER = MCPTool(
    name="submit_answer",
    description="提交用户答案，获取判分结果和解析",
    parameters=[
        MCPToolParameter(
            name="user_id",
            type="number",
            description="用户ID",
            required=True
        ),
        MCPToolParameter(
            name="question_id",
            type="string",
            description="题目ID",
            required=True
        ),
        MCPToolParameter(
            name="session_id",
            type="string",
            description="答题会话ID（可选，用于记录答题进度）",
            required=False
        ),
        MCPToolParameter(
            name="user_answer",
            type="object",
            description="用户答案（格式根据题型不同）",
            required=True,
            properties={
                "answer": {"type": "string", "description": "单选/判断答案"},
                "answers": {"type": "array", "description": "多选答案列表"},
                "fill_answers": {"type": "array", "description": "填空答案列表"},
                "essay_answer": {"type": "string", "description": "问答答案"}
            }
        ),
        MCPToolParameter(
            name="time_spent",
            type="number",
            description="答题用时（秒）",
            required=False
        )
    ]
)

# 工具5: 获取错题列表
GET_WRONG_QUESTIONS = MCPTool(
    name="get_wrong_questions",
    description="获取用户的错题列表，用于错题订正",
    parameters=[
        MCPToolParameter(
            name="user_id",
            type="number",
            description="用户ID",
            required=True
        ),
        MCPToolParameter(
            name="bank_id",
            type="string",
            description="题库ID（可选，不指定则返回所有题库的错题）",
            required=False
        ),
        MCPToolParameter(
            name="corrected",
            type="boolean",
            description="是否只看已订正/未订正的错题",
            required=False
        ),
        MCPToolParameter(
            name="min_error_count",
            type="number",
            description="最小错误次数（筛选高频错题）",
            required=False
        ),
        MCPToolParameter(
            name="limit",
            type="number",
            description="返回题目数量限制",
            required=False
        )
    ]
)

# 工具6: 搜索题目
SEARCH_QUESTIONS = MCPTool(
    name="search_questions",
    description="跨题库搜索题目（通过关键词、标签等）",
    parameters=[
        MCPToolParameter(
            name="user_id",
            type="number",
            description="用户ID",
            required=True
        ),
        MCPToolParameter(
            name="query",
            type="string",
            description="搜索关键词",
            required=True
        ),
        MCPToolParameter(
            name="search_in",
            type="array",
            description="搜索范围",
            required=False,
            enum=["stem", "options", "explanation", "tags"]
        ),
        MCPToolParameter(
            name="bank_ids",
            type="array",
            description="限定题库范围（可选）",
            required=False
        ),
        MCPToolParameter(
            name="limit",
            type="number",
            description="返回题目数量限制",
            required=False
        )
    ]
)

# 工具7: 获取用户统计
GET_USER_STATISTICS = MCPTool(
    name="get_user_statistics",
    description="获取用户的学习统计数据",
    parameters=[
        MCPToolParameter(
            name="user_id",
            type="number",
            description="用户ID",
            required=True
        ),
        MCPToolParameter(
            name="bank_id",
            type="string",
            description="题库ID（可选，不指定则返回总体统计）",
            required=False
        ),
        MCPToolParameter(
            name="date_range",
            type="string",
            description="时间范围",
            required=False,
            enum=["today", "week", "month", "all"]
        )
    ]
)

# 工具8: 添加收藏
ADD_FAVORITE = MCPTool(
    name="add_favorite",
    description="将题目添加到收藏夹",
    parameters=[
        MCPToolParameter(
            name="user_id",
            type="number",
            description="用户ID",
            required=True
        ),
        MCPToolParameter(
            name="question_id",
            type="string",
            description="题目ID",
            required=True
        ),
        MCPToolParameter(
            name="note",
            type="string",
            description="收藏备注（可选）",
            required=False
        )
    ]
)

# 工具9: 获取收藏列表
GET_FAVORITES = MCPTool(
    name="get_favorites",
    description="获取用户的收藏题目列表",
    parameters=[
        MCPToolParameter(
            name="user_id",
            type="number",
            description="用户ID",
            required=True
        ),
        MCPToolParameter(
            name="bank_id",
            type="string",
            description="题库ID（可选）",
            required=False
        ),
        MCPToolParameter(
            name="limit",
            type="number",
            description="返回题目数量限制",
            required=False
        )
    ]
)

# 工具10: 创建答题会话
CREATE_PRACTICE_SESSION = MCPTool(
    name="create_practice_session",
    description="创建新的答题会话，用于跟踪答题进度",
    parameters=[
        MCPToolParameter(
            name="user_id",
            type="number",
            description="用户ID",
            required=True
        ),
        MCPToolParameter(
            name="bank_id",
            type="string",
            description="题库ID",
            required=True
        ),
        MCPToolParameter(
            name="mode",
            type="string",
            description="答题模式",
            required=True,
            enum=["sequential", "random", "wrong_only", "favorite_only"]
        ),
        MCPToolParameter(
            name="question_types",
            type="array",
            description="题型筛选（可选）",
            required=False
        ),
        MCPToolParameter(
            name="difficulty",
            type="string",
            description="难度筛选（可选）",
            required=False,
            enum=["easy", "medium", "hard", "expert"]
        )
    ]
)

# 工具11: 获取题目解析
GET_QUESTION_EXPLANATION = MCPTool(
    name="get_question_explanation",
    description="获取题目的详细解析（包含正确答案和解释）",
    parameters=[
        MCPToolParameter(
            name="user_id",
            type="number",
            description="用户ID",
            required=True
        ),
        MCPToolParameter(
            name="question_id",
            type="string",
            description="题目ID",
            required=True
        ),
        MCPToolParameter(
            name="include_related",
            type="boolean",
            description="是否包含相关知识点和类似题目",
            required=False
        )
    ]
)

# 工具12: 标记错题已订正
MARK_WRONG_QUESTION_CORRECTED = MCPTool(
    name="mark_wrong_question_corrected",
    description="标记错题为已订正",
    parameters=[
        MCPToolParameter(
            name="user_id",
            type="number",
            description="用户ID",
            required=True
        ),
        MCPToolParameter(
            name="question_id",
            type="string",
            description="题目ID",
            required=True
        )
    ]
)


# ==================== Tool Registry ====================

# 所有可用的MCP工具
ALL_MCP_TOOLS: List[MCPTool] = [
    GET_QUESTION_BANKS,
    GET_QUESTIONS,
    GET_QUESTION_DETAIL,
    SUBMIT_ANSWER,
    GET_WRONG_QUESTIONS,
    SEARCH_QUESTIONS,
    GET_USER_STATISTICS,
    ADD_FAVORITE,
    GET_FAVORITES,
    CREATE_PRACTICE_SESSION,
    GET_QUESTION_EXPLANATION,
    MARK_WRONG_QUESTION_CORRECTED
]


def get_tool_by_name(tool_name: str) -> Optional[MCPTool]:
    """根据名称获取工具定义"""
    for tool in ALL_MCP_TOOLS:
        if tool.name == tool_name:
            return tool
    return None


def get_tools_schema() -> List[Dict[str, Any]]:
    """获取所有工具的OpenAI Function Calling格式的Schema"""
    schemas = []

    for tool in ALL_MCP_TOOLS:
        # 构建参数schema
        properties = {}
        required = []

        for param in tool.parameters:
            prop_schema = {
                "type": param.type,
                "description": param.description
            }

            # Array类型需要指定items
            if param.type == "array":
                prop_schema["items"] = {"type": "string"}

            if param.enum:
                prop_schema["enum"] = param.enum

            if param.properties:
                # 处理嵌套properties中的array类型
                fixed_properties = {}
                for prop_name, prop_def in param.properties.items():
                    if isinstance(prop_def, dict):
                        fixed_prop = prop_def.copy()
                        if fixed_prop.get("type") == "array" and "items" not in fixed_prop:
                            fixed_prop["items"] = {"type": "string"}
                        fixed_properties[prop_name] = fixed_prop
                    else:
                        fixed_properties[prop_name] = prop_def
                prop_schema["properties"] = fixed_properties

            properties[param.name] = prop_schema

            if param.required:
                required.append(param.name)

        # 构建工具schema
        schema = {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }

        schemas.append(schema)

    return schemas


def get_tools_for_claude() -> List[Dict[str, Any]]:
    """获取Claude格式的工具定义"""
    tools = []

    for tool in ALL_MCP_TOOLS:
        # 构建输入schema
        properties = {}
        required = []

        for param in tool.parameters:
            prop_schema = {
                "type": param.type,
                "description": param.description
            }

            if param.enum:
                prop_schema["enum"] = param.enum

            properties[param.name] = prop_schema

            if param.required:
                required.append(param.name)

        # Claude工具格式
        tool_def = {
            "name": tool.name,
            "description": tool.description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }

        tools.append(tool_def)

    return tools
