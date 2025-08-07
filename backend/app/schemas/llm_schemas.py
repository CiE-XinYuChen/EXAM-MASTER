"""
LLM Interface and Prompt Template Schemas
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum


class InterfaceType(str, Enum):
    """支持的接口类型"""
    OPENAI_COMPATIBLE = "openai-compatible"
    ANTHROPIC = "anthropic"
    ZHIPU_AI = "zhipu-ai"


class ResponseParser(str, Enum):
    """响应解析器类型"""
    OPENAI_STANDARD = "openai_standard"
    ANTHROPIC_STANDARD = "anthropic_standard"
    CUSTOM_JSON = "custom_json"
    REGEX = "regex"


class TemplateType(str, Enum):
    """模板类型"""
    QUESTION_PARSER = "question_parser"
    BATCH_PARSER = "batch_parser"
    FORMATTER = "formatter"
    VALIDATOR = "validator"
    CUSTOM = "custom"


# ============ LLM Interface Schemas ============

class LLMInterfaceConfig(BaseModel):
    """接口配置"""
    base_url: str = Field(..., description="API基础URL")
    api_key: Optional[str] = Field(None, description="API密钥")
    model: str = Field(..., description="模型名称")
    headers: Optional[Dict[str, str]] = Field(default={}, description="自定义请求头")
    timeout: int = Field(default=120, description="超时时间（秒）")
    max_retries: int = Field(default=3, description="最大重试次数")


class LLMRequestFormat(BaseModel):
    """请求格式模板"""
    messages: Optional[List[Dict[str, str]]] = Field(None, description="消息格式（OpenAI风格）")
    prompt: Optional[str] = Field(None, description="提示词格式（简单文本）")
    temperature: float = Field(default=0.3, description="温度参数")
    max_tokens: int = Field(default=2000, description="最大token数")
    top_p: Optional[float] = Field(default=1.0, description="Top-p采样")
    stop: Optional[List[str]] = Field(default=[], description="停止词")


class LLMInterfaceBase(BaseModel):
    """接口基础信息"""
    name: str = Field(..., min_length=1, max_length=100, description="接口名称")
    type: InterfaceType = Field(..., description="接口类型")
    config: LLMInterfaceConfig = Field(..., description="接口配置")
    request_format: Optional[LLMRequestFormat] = Field(None, description="请求格式")
    response_parser: ResponseParser = Field(default=ResponseParser.OPENAI_STANDARD, description="响应解析器")
    prompt_template_id: Optional[str] = Field(None, description="默认提示词模板ID")
    is_active: bool = Field(default=True, description="是否启用")
    is_default: bool = Field(default=False, description="是否为默认接口")


class LLMInterfaceCreate(LLMInterfaceBase):
    """创建接口请求"""
    pass


class LLMInterfaceUpdate(BaseModel):
    """更新接口请求"""
    name: Optional[str] = None
    type: Optional[InterfaceType] = None
    config: Optional[LLMInterfaceConfig] = None
    request_format: Optional[LLMRequestFormat] = None
    response_parser: Optional[ResponseParser] = None
    prompt_template_id: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class LLMInterfaceResponse(LLMInterfaceBase):
    """接口响应"""
    id: str
    user_id: int
    usage_count: int = 0
    last_used_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============ Prompt Template Schemas ============

class PromptTemplateBase(BaseModel):
    """模板基础信息"""
    name: str = Field(..., min_length=1, max_length=100, description="模板名称")
    type: TemplateType = Field(..., description="模板类型")
    category: Optional[str] = Field(None, description="模板分类")
    content: str = Field(..., description="模板内容")
    variables: Optional[List[str]] = Field(default=[], description="模板变量")
    description: Optional[str] = Field(None, description="模板说明")
    example_input: Optional[str] = Field(None, description="示例输入")
    example_output: Optional[str] = Field(None, description="示例输出")
    is_public: bool = Field(default=False, description="是否公开")


class PromptTemplateCreate(PromptTemplateBase):
    """创建模板请求"""
    pass


class PromptTemplateUpdate(BaseModel):
    """更新模板请求"""
    name: Optional[str] = None
    content: Optional[str] = None
    variables: Optional[List[str]] = None
    description: Optional[str] = None
    example_input: Optional[str] = None
    example_output: Optional[str] = None
    is_public: Optional[bool] = None


class PromptTemplateResponse(PromptTemplateBase):
    """模板响应"""
    id: str
    user_id: Optional[int] = None
    is_system: bool = False
    usage_count: int = 0
    rating: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============ Question Parsing Schemas ============

class ParsedBlank(BaseModel):
    """填空题的单个空"""
    position: int = Field(..., description="空的位置（0开始）")
    answer: str = Field(..., description="正确答案")
    alternatives: Optional[List[str]] = Field(default=[], description="替代答案")
    hint: Optional[str] = Field(None, description="提示")


class ParsedOption(BaseModel):
    """选择题选项"""
    label: str = Field(..., description="选项标签（A、B、C等）")
    content: str = Field(..., description="选项内容")
    is_correct: bool = Field(default=False, description="是否正确")


class ParsedQuestion(BaseModel):
    """解析后的题目"""
    type: str = Field(..., description="题目类型：single, multiple, fill, judge, essay")
    stem: str = Field(..., description="题干")
    stem_display: Optional[str] = Field(None, description="显示用题干（带空格标记）")
    
    # 填空题专用
    blanks: Optional[List[ParsedBlank]] = Field(None, description="填空列表")
    
    # 选择题专用
    options: Optional[List[ParsedOption]] = Field(None, description="选项列表")
    
    # 判断题专用
    correct_answer: Optional[str] = Field(None, description="正确答案（true/false）")
    
    # 元数据
    difficulty: Optional[str] = Field(default="medium", description="难度")
    category: Optional[str] = Field(None, description="分类")
    tags: Optional[List[str]] = Field(default=[], description="标签")
    explanation: Optional[str] = Field(None, description="解析")


class QuestionParseRequest(BaseModel):
    """题目解析请求"""
    interface_id: str = Field(..., description="使用的接口ID")
    prompt_template_id: Optional[str] = Field(None, description="提示词模板ID")
    raw_text: str = Field(..., description="原始文本")
    hint_type: Optional[str] = Field(default="auto", description="类型提示：auto, single, multiple, fill, judge")
    bank_id: Optional[str] = Field(None, description="目标题库ID")
    custom_variables: Optional[Dict[str, str]] = Field(default={}, description="自定义变量")


class QuestionParseResponse(BaseModel):
    """题目解析响应"""
    success: bool
    parsed_questions: List[ParsedQuestion]
    parse_errors: Optional[List[Dict[str, Any]]] = Field(default=[], description="解析错误")
    token_used: Optional[int] = Field(None, description="使用的token数")
    cost: Optional[str] = Field(None, description="费用")
    suggestions: Optional[List[str]] = Field(default=[], description="建议")


class BatchImportRequest(BaseModel):
    """批量导入请求"""
    bank_id: str = Field(..., description="题库ID")
    questions: List[ParsedQuestion] = Field(..., description="解析后的题目列表")
    validate_before_import: bool = Field(default=True, description="导入前验证")
    skip_duplicates: bool = Field(default=True, description="跳过重复题目")


class BatchImportResponse(BaseModel):
    """批量导入响应"""
    success: bool
    imported_count: int
    skipped_count: int
    failed_count: int
    errors: Optional[List[Dict[str, Any]]] = Field(default=[], description="导入错误")


# ============ Test & Validation Schemas ============

class InterfaceTestRequest(BaseModel):
    """接口测试请求"""
    test_prompt: str = Field(default="Hello, please respond with 'OK' if you can hear me.", description="测试提示词")


class InterfaceTestResponse(BaseModel):
    """接口测试响应"""
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    response_time: Optional[int] = None  # 毫秒