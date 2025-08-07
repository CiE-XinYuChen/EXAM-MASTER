"""
Enhanced LLM Service with Markdown Template Support
支持Markdown模板的增强版LLM服务
"""
import json
import time
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from pathlib import Path

from app.models.llm_models import LLMInterface, PromptTemplate, LLMParseLog
from app.schemas.llm_schemas import (
    ParsedQuestion, ParsedOption, ParsedBlank,
    QuestionParseRequest, QuestionParseResponse,
    InterfaceType, ResponseParser
)
from app.services.template_loader import template_loader
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class LLMServiceV2:
    """增强版LLM服务，支持Markdown模板"""
    
    def __init__(self, db: Session):
        self.db = db
        self.interfaces_cache = {}
        self.template_loader = template_loader
    
    def parse_questions_with_markdown(
        self,
        request: QuestionParseRequest,
        user_id: int,
        use_markdown_template: bool = True
    ) -> QuestionParseResponse:
        """使用Markdown模板解析题目"""
        start_time = time.time()
        
        # 获取接口配置
        interface = self._get_interface(request.interface_id)
        if not interface or not interface.is_active:
            return QuestionParseResponse(
                success=False,
                parsed_questions=[],
                parse_errors=[{"error": "Interface not found or inactive"}]
            )
        
        # 构建提示词
        if use_markdown_template and request.prompt_template_id:
            # 尝试从Markdown文件加载
            prompt = self._build_prompt_from_markdown(
                request.prompt_template_id,
                request.raw_text,
                request.custom_variables
            )
        else:
            # 从数据库加载
            template = self._get_template_from_db(request.prompt_template_id or interface.prompt_template_id)
            if not template:
                return QuestionParseResponse(
                    success=False,
                    parsed_questions=[],
                    parse_errors=[{"error": "Template not found"}]
                )
            prompt = self._build_prompt_from_db(template, request.raw_text, request.custom_variables)
        
        # 调用LLM接口
        try:
            response = self._call_interface(interface, prompt)
            parsed_questions = self._parse_response(response, interface.response_parser)
            
            # 记录日志
            response_time = int((time.time() - start_time) * 1000)
            self._log_parse(
                interface_id=interface.id,
                user_id=user_id,
                input_text=request.raw_text,
                parsed_result={"questions": [q.dict() for q in parsed_questions]},
                success=True,
                response_time=response_time
            )
            
            # 更新统计
            interface.usage_count += 1
            interface.last_used_at = datetime.utcnow()
            self.db.commit()
            
            return QuestionParseResponse(
                success=True,
                parsed_questions=parsed_questions,
                parse_errors=[],
                suggestions=self._generate_suggestions(parsed_questions)
            )
            
        except Exception as e:
            logger.error(f"LLM parsing error: {str(e)}")
            self._log_parse(
                interface_id=interface.id,
                user_id=user_id,
                input_text=request.raw_text,
                parsed_result=None,
                success=False,
                error_message=str(e),
                response_time=int((time.time() - start_time) * 1000)
            )
            
            return QuestionParseResponse(
                success=False,
                parsed_questions=[],
                parse_errors=[{"error": str(e)}]
            )
    
    def _build_prompt_from_markdown(
        self,
        template_id: str,
        raw_text: str,
        custom_variables: Dict[str, str]
    ) -> str:
        """从Markdown模板构建提示词"""
        try:
            # 尝试作为文件路径加载
            if template_id.endswith('.md'):
                template_data = self.template_loader.load_template(template_id)
            else:
                # 尝试从预设目录加载
                for subdir in ['system', 'user', 'shared']:
                    try:
                        path = f"{subdir}/{template_id}.md"
                        template_data = self.template_loader.load_template(path)
                        break
                    except FileNotFoundError:
                        continue
                else:
                    raise FileNotFoundError(f"Template {template_id} not found")
            
            # 准备变量
            variables = {
                'input_text': raw_text,
                'output_format': self._get_output_format(),
                **custom_variables
            }
            
            # 渲染模板
            return self.template_loader.render_template(template_data, variables)
            
        except Exception as e:
            logger.error(f"Failed to load markdown template: {e}")
            raise ValueError(f"Failed to load template: {str(e)}")
    
    def _build_prompt_from_db(
        self,
        template: PromptTemplate,
        raw_text: str,
        custom_variables: Dict[str, str]
    ) -> str:
        """从数据库模板构建提示词"""
        prompt = template.content
        
        # 替换默认变量
        prompt = prompt.replace("{input_text}", raw_text)
        prompt = prompt.replace("{output_format}", self._get_output_format())
        
        # 替换自定义变量
        for key, value in custom_variables.items():
            prompt = prompt.replace(f"{{{key}}}", value)
        
        return prompt
    
    def _get_interface(self, interface_id: str) -> Optional[LLMInterface]:
        """获取接口配置"""
        if interface_id not in self.interfaces_cache:
            interface = self.db.query(LLMInterface).filter_by(id=interface_id).first()
            if interface:
                self.interfaces_cache[interface_id] = interface
        return self.interfaces_cache.get(interface_id)
    
    def _get_template_from_db(self, template_id: str) -> Optional[PromptTemplate]:
        """从数据库获取模板"""
        return self.db.query(PromptTemplate).filter_by(id=template_id).first()
    
    def _get_output_format(self) -> str:
        """获取输出格式说明"""
        return """
返回JSON数组格式，每个题目包含：
{
    "type": "题目类型(single/multiple/fill/judge/essay)",
    "stem": "题干内容（填空题用{}标记空位）",
    "stem_display": "显示用题干（保留原始空位标记）",
    "blanks": [  // 填空题专用
        {
            "position": 0,
            "answer": "答案",
            "alternatives": ["其他可接受答案"]
        }
    ],
    "options": [  // 选择题专用
        {
            "label": "A",
            "content": "选项内容",
            "is_correct": true/false
        }
    ],
    "correct_answer": "true/false",  // 判断题专用
    "difficulty": "easy/medium/hard",
    "category": "分类",
    "tags": ["标签1", "标签2"],
    "explanation": "解析说明"
}
"""
    
    def _call_interface(self, interface: LLMInterface, prompt: str) -> Dict[str, Any]:
        """调用LLM接口"""
        config = interface.config
        
        if interface.type == InterfaceType.OPENAI_COMPATIBLE:
            return self._call_openai_compatible(config, interface.request_format, prompt)
        elif interface.type == InterfaceType.ANTHROPIC:
            return self._call_anthropic(config, interface.request_format, prompt)
        elif interface.type == InterfaceType.ZHIPU_AI:
            return self._call_zhipu_ai(config, interface.request_format, prompt)
        elif interface.type == InterfaceType.CUSTOM_HTTP:
            return self._call_custom_http(config, interface.request_format, prompt)
        else:
            raise ValueError(f"Unsupported interface type: {interface.type}")
    
    def _call_openai_compatible(
        self,
        config: Dict[str, Any],
        request_format: Dict[str, Any],
        prompt: str
    ) -> Dict[str, Any]:
        """调用OpenAI兼容接口"""
        headers = config.get("headers", {})
        if "api_key" in config:
            headers["Authorization"] = f"Bearer {config['api_key']}"
        
        request_body = {
            "model": config.get("model", "gpt-3.5-turbo"),
            "messages": [
                {"role": "system", "content": "You are a question parser expert."},
                {"role": "user", "content": prompt}
            ],
            "temperature": request_format.get("temperature", 0.3) if request_format else 0.3,
            "max_tokens": request_format.get("max_tokens", 2000) if request_format else 2000
        }
        
        response = requests.post(
            f"{config['base_url']}/chat/completions",
            headers=headers,
            json=request_body,
            timeout=config.get("timeout", 120)
        )
        response.raise_for_status()
        
        return response.json()
    
    def _call_anthropic(
        self,
        config: Dict[str, Any],
        request_format: Dict[str, Any],
        prompt: str
    ) -> Dict[str, Any]:
        """调用Anthropic接口"""
        headers = {
            "x-api-key": config.get("api_key"),
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        request_body = {
            "model": config.get("model", "claude-3-sonnet-20240229"),
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": request_format.get("max_tokens", 2000) if request_format else 2000,
            "temperature": request_format.get("temperature", 0.3) if request_format else 0.3
        }
        
        response = requests.post(
            f"{config['base_url']}/messages",
            headers=headers,
            json=request_body,
            timeout=config.get("timeout", 120)
        )
        response.raise_for_status()
        
        return response.json()
    
    def _call_zhipu_ai(
        self,
        config: Dict[str, Any],
        request_format: Dict[str, Any],
        prompt: str
    ) -> Dict[str, Any]:
        """调用智谱AI接口"""
        headers = {
            "Authorization": f"Bearer {config.get('api_key')}",
            "Content-Type": "application/json"
        }
        
        # 构建消息列表
        messages = [{"role": "user", "content": prompt}]
        
        # 如果有系统提示词，添加到消息列表开头
        if request_format and "system_prompt" in request_format:
            messages.insert(0, {"role": "system", "content": request_format["system_prompt"]})
        
        request_body = {
            "model": config.get("model", "glm-4"),
            "messages": messages,
            "temperature": request_format.get("temperature", 0.3) if request_format else 0.3,
            "max_tokens": request_format.get("max_tokens", 2000) if request_format else 2000,
            "top_p": request_format.get("top_p", 1.0) if request_format else 1.0
        }
        
        # 添加可选参数
        if request_format:
            if "stop" in request_format and request_format["stop"]:
                request_body["stop"] = request_format["stop"]
            if "tools" in request_format:
                request_body["tools"] = request_format["tools"]
            if "tool_choice" in request_format:
                request_body["tool_choice"] = request_format["tool_choice"]
        
        # 构建API地址
        base_url = config.get("base_url", "https://open.bigmodel.cn/api/paas/v4")
        
        # 如果base_url已经包含完整路径，直接使用
        if base_url.endswith("/chat/completions"):
            api_url = base_url
        # 如果是基础API地址，添加chat/completions端点
        elif base_url.endswith("/api/paas/v4") or base_url.endswith("/v4"):
            api_url = f"{base_url}/chat/completions"
        # 其他情况，假设需要添加完整路径
        else:
            api_url = f"{base_url.rstrip('/')}/api/paas/v4/chat/completions"
        
        response = requests.post(
            api_url,
            headers=headers,
            json=request_body,
            timeout=config.get("timeout", 120)
        )
        response.raise_for_status()
        
        return response.json()
    
    def _call_custom_http(
        self,
        config: Dict[str, Any],
        request_format: Dict[str, Any],
        prompt: str
    ) -> Dict[str, Any]:
        """调用自定义HTTP接口"""
        headers = config.get("headers", {})
        
        request_body = request_format.copy() if request_format else {}
        request_body_str = json.dumps(request_body)
        request_body_str = request_body_str.replace("{prompt}", prompt)
        request_body = json.loads(request_body_str)
        
        response = requests.post(
            config['base_url'],
            headers=headers,
            json=request_body,
            timeout=config.get("timeout", 120)
        )
        response.raise_for_status()
        
        return response.json()
    
    def _parse_response(
        self,
        response: Dict[str, Any],
        parser_type: str
    ) -> List[ParsedQuestion]:
        """解析LLM响应"""
        try:
            if parser_type == ResponseParser.OPENAI_STANDARD:
                # 支持OpenAI和Zhipu AI的响应格式
                content = response["choices"][0]["message"]["content"]
            elif parser_type == ResponseParser.ANTHROPIC_STANDARD:
                content = response["content"][0]["text"]
            else:
                content = json.dumps(response)
            
            # 提取JSON
            json_start = content.find('[')
            json_end = content.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                questions_data = json.loads(json_str)
            else:
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                json_str = content[json_start:json_end]
                questions_data = [json.loads(json_str)]
            
            # 转换为ParsedQuestion对象
            parsed_questions = []
            for q in questions_data:
                options = None
                if q.get("options"):
                    options = [
                        ParsedOption(
                            label=opt.get("label", ""),
                            content=opt.get("content", ""),
                            is_correct=opt.get("is_correct", False)
                        )
                        for opt in q["options"]
                    ]
                
                blanks = None
                if q.get("blanks"):
                    blanks = [
                        ParsedBlank(
                            position=blank.get("position", 0),
                            answer=blank.get("answer", ""),
                            alternatives=blank.get("alternatives", [])
                        )
                        for blank in q["blanks"]
                    ]
                
                parsed_questions.append(ParsedQuestion(
                    type=q.get("type", "single"),
                    stem=q.get("stem", ""),
                    stem_display=q.get("stem_display"),
                    blanks=blanks,
                    options=options,
                    correct_answer=q.get("correct_answer"),
                    difficulty=q.get("difficulty", "medium"),
                    category=q.get("category"),
                    tags=q.get("tags", []),
                    explanation=q.get("explanation")
                ))
            
            return parsed_questions
            
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {str(e)}")
            raise ValueError(f"Failed to parse response: {str(e)}")
    
    def _generate_suggestions(self, questions: List[ParsedQuestion]) -> List[str]:
        """生成建议"""
        suggestions = []
        
        for i, q in enumerate(questions):
            if q.type in ["single", "multiple"] and not q.options:
                suggestions.append(f"题目{i+1}：选择题缺少选项")
            if q.type == "fill" and not q.blanks:
                suggestions.append(f"题目{i+1}：填空题缺少空位标记")
            if not q.stem:
                suggestions.append(f"题目{i+1}：缺少题干")
        
        return suggestions
    
    def _log_parse(
        self,
        interface_id: str,
        user_id: int,
        input_text: str,
        parsed_result: Optional[Dict[str, Any]],
        success: bool,
        error_message: Optional[str] = None,
        response_time: int = 0
    ):
        """记录解析日志"""
        log = LLMParseLog(
            interface_id=interface_id,
            user_id=user_id,
            input_text=input_text[:1000],
            parsed_result=parsed_result,
            success=success,
            error_message=error_message,
            response_time=response_time
        )
        self.db.add(log)
        self.db.commit()