"""
Preset Prompt Templates for Question Parsing
预设的提示词模板
"""

PRESET_TEMPLATES = [
    {
        "id": "default_question_parser",
        "name": "通用题目解析器",
        "type": "question_parser",
        "category": "default",
        "is_system": True,
        "content": """你是一个专业的题目解析专家。请将以下文本解析成标准的题目格式。

解析规则：
1. 自动识别题目类型：
   - 单选题：有多个选项，只有一个正确答案
   - 多选题：有多个选项，有多个正确答案
   - 判断题：答案为对/错、正确/错误、true/false
   - 填空题：题目中有空白需要填写，标记为____、{}、[]等
   - 问答题：需要文字回答的开放性题目

2. 对于填空题：
   - 将空位用{}标记，从0开始编号
   - 提取每个空的正确答案
   - 如果有多个可接受的答案，列为alternatives

3. 对于选择题：
   - 提取所有选项，标记为A、B、C、D等
   - 标记正确答案

4. 输出格式：
{output_format}

需要解析的文本：
{input_text}

重要：请直接返回JSON数组格式的结果，不要包含任何其他说明文字、思考过程或markdown标记。只返回纯JSON数组。""",
        "variables": ["input_text", "output_format"],
        "example_input": """1. Python中定义函数使用____关键字。（答案：def）
2. 以下哪个是Python的数据类型？
   A. integer
   B. string  
   C. list（正确）
   D. array""",
        "example_output": """[
    {
        "type": "fill",
        "stem": "Python中定义函数使用{}关键字。",
        "stem_display": "Python中定义函数使用____关键字。",
        "blanks": [{"position": 0, "answer": "def"}],
        "difficulty": "easy"
    },
    {
        "type": "single",
        "stem": "以下哪个是Python的数据类型？",
        "options": [
            {"label": "A", "content": "integer", "is_correct": false},
            {"label": "B", "content": "string", "is_correct": false},
            {"label": "C", "content": "list", "is_correct": true},
            {"label": "D", "content": "array", "is_correct": false}
        ],
        "difficulty": "easy"
    }
]"""
    },
    {
        "id": "fill_blank_parser",
        "name": "填空题专用解析器",
        "type": "question_parser",
        "category": "specific",
        "is_system": True,
        "content": """你是填空题解析专家。请将以下文本解析为填空题格式。

解析规则：
1. 识别所有空位标记：____、___、【】、[]、{}、（）等
2. 将所有空位统一转换为{}格式
3. 提取每个空的答案（通常在题目后的括号中或"答案："后）
4. 支持多个空位的题目
5. 如果答案有多种可能，都要列出

特殊处理：
- 如果空位在句子开头或结尾，保持原样
- 如果有提示词（如"请填写"），保留在题干中
- 数字、日期、专有名词等答案要精确匹配

输出格式：
{output_format}

需要解析的文本：
{input_text}

请直接返回JSON数组。""",
        "variables": ["input_text", "output_format"],
        "example_input": "中华人民共和国成立于____年____月____日。（答案：1949，10，1）",
        "example_output": """[{
    "type": "fill",
    "stem": "中华人民共和国成立于{}年{}月{}日。",
    "stem_display": "中华人民共和国成立于____年____月____日。",
    "blanks": [
        {"position": 0, "answer": "1949"},
        {"position": 1, "answer": "10"},
        {"position": 2, "answer": "1"}
    ],
    "difficulty": "easy",
    "category": "历史"
}]"""
    },
    {
        "id": "choice_parser",
        "name": "选择题专用解析器",
        "type": "question_parser",
        "category": "specific",
        "is_system": True,
        "content": """你是选择题解析专家。请将以下文本解析为选择题格式。

解析规则：
1. 识别题型：
   - 如果标注"多选"、"多项选择"、有多个正确答案 → multiple
   - 否则 → single

2. 选项识别：
   - A. B. C. D. 或 A、B、C、D、或 (A) (B) (C) (D)
   - 选项内容直到下一个选项标记或题目结束

3. 答案识别：
   - 括号中标注：（正确）、（√）、（答案）
   - 题目后标注：答案：A、正确答案：BC
   - 加粗、标星等特殊标记

4. 格式化：
   - 清理选项中的答案标记
   - 保持选项内容的完整性

输出格式：
{output_format}

需要解析的文本：
{input_text}

请直接返回JSON数组。""",
        "variables": ["input_text", "output_format"]
    },
    {
        "id": "batch_mixed_parser",
        "name": "批量混合题型解析器",
        "type": "batch_parser",
        "category": "batch",
        "is_system": True,
        "content": """你是题库解析专家。请将以下包含多道不同类型题目的文本解析成标准格式。

解析规则：
1. 题目分隔：
   - 数字编号：1. 2. 3. 或 1、2、3、
   - 题号标记：第1题、题目1、Q1等
   - 空行分隔

2. 自动识别每道题的类型并正确解析

3. 保持题目顺序

4. 忽略无关内容（如页眉、页脚、说明文字）

{user_custom_rules}

输出格式：
{output_format}

需要解析的文本：
{input_text}

请直接返回JSON数组，包含所有解析成功的题目。""",
        "variables": ["input_text", "output_format", "user_custom_rules"]
    },
    {
        "id": "judge_parser",
        "name": "判断题专用解析器",
        "type": "question_parser",
        "category": "specific",
        "is_system": True,
        "content": """你是判断题解析专家。请将以下文本解析为判断题格式。

解析规则：
1. 识别判断题标志：
   - 题目后有（对）（错）、（√）（×）、（T）（F）
   - 题目要求判断正误
   - 题干是陈述句，需要判断真假

2. 答案标准化：
   - 对、正确、√、T、True → "true"
   - 错、错误、×、F、False → "false"

3. 如果没有明确答案，根据事实判断

输出格式：
{output_format}

需要解析的文本：
{input_text}

请直接返回JSON数组。""",
        "variables": ["input_text", "output_format"]
    }
]


def get_preset_template(template_id: str) -> dict:
    """获取预设模板"""
    for template in PRESET_TEMPLATES:
        if template["id"] == template_id:
            return template
    return None


def get_all_preset_templates() -> list:
    """获取所有预设模板"""
    return PRESET_TEMPLATES