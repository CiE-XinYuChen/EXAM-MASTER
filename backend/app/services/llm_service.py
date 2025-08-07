"""
LLM Service Abstraction Layer
"""
import json
import time
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from app.models.llm_models import LLMInterface, PromptTemplate, LLMParseLog
from app.schemas.llm_schemas import (
    ParsedQuestion, ParsedOption, ParsedBlank,
    QuestionParseRequest, QuestionParseResponse,
    InterfaceType, ResponseParser
)
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class LLMService:
    """LLM服务抽象层"""
    
    def __init__(self, db: Session):
        self.db = db
        self.interfaces_cache = {}
        self.templates_cache = {}
    
    def parse_questions(
        self, 
        request: QuestionParseRequest,
        user_id: int
    ) -> QuestionParseResponse:
        """解析题目文本"""
        start_time = time.time()
        
        # 获取接口配置
        interface = self._get_interface(request.interface_id)
        if not interface or not interface.is_active:
            return QuestionParseResponse(
                success=False,
                parsed_questions=[],
                parse_errors=[{"error": "Interface not found or inactive"}]
            )
        
        # 获取提示词模板
        template_id = request.prompt_template_id or interface.prompt_template_id
        template = self._get_template(template_id)
        if not template:
            return QuestionParseResponse(
                success=False,
                parsed_questions=[],
                parse_errors=[{"error": "Template not found"}]
            )
        
        # 构建提示词
        prompt = self._build_prompt(template, request.raw_text, request.custom_variables)
        
        # 调用LLM接口
        try:
            response = self._call_interface(interface, prompt)
            
            # 解析响应
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
            
            # 更新使用统计
            interface.usage_count += 1
            interface.last_used_at = datetime.utcnow()
            template.usage_count += 1
            self.db.commit()
            
            return QuestionParseResponse(
                success=True,
                parsed_questions=parsed_questions,
                parse_errors=[],
                suggestions=self._generate_suggestions(parsed_questions)
            )
            
        except Exception as e:
            logger.error(f"LLM parsing error: {str(e)}")
            
            # 记录错误日志
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
    
    def _get_interface(self, interface_id: str) -> Optional[LLMInterface]:
        """获取接口配置"""
        if interface_id not in self.interfaces_cache:
            interface = self.db.query(LLMInterface).filter_by(id=interface_id).first()
            if interface:
                self.interfaces_cache[interface_id] = interface
        return self.interfaces_cache.get(interface_id)
    
    def _get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """获取提示词模板"""
        if template_id not in self.templates_cache:
            template = self.db.query(PromptTemplate).filter_by(id=template_id).first()
            if template:
                self.templates_cache[template_id] = template
        return self.templates_cache.get(template_id)
    
    def _build_prompt(
        self, 
        template: PromptTemplate, 
        raw_text: str,
        custom_variables: Dict[str, str]
    ) -> str:
        """构建提示词"""
        prompt = template.content
        
        # 替换默认变量
        prompt = prompt.replace("{input_text}", raw_text)
        prompt = prompt.replace("{output_format}", self._get_output_format())
        
        # 替换自定义变量
        for key, value in custom_variables.items():
            prompt = prompt.replace(f"{{{key}}}", value)
        
        return prompt
    
    def _get_output_format(self) -> str:
        """获取输出格式说明"""
        return """
返回JSON格式，每个题目包含：
{
    "type": "题目类型(single/multiple/fill/judge/essay)",
    "stem": "题干内容",
    "stem_display": "显示用题干（填空题用{}标记空位）",
    "blanks": [{"position": 0, "answer": "答案"}],  // 填空题专用
    "options": [{"label": "A", "content": "选项内容", "is_correct": true/false}],  // 选择题专用
    "correct_answer": "true/false",  // 判断题专用
    "difficulty": "easy/medium/hard",
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
        
        # 构建请求体
        request_body = {
            "model": config.get("model", "gpt-3.5-turbo"),
            "messages": [
                {"role": "system", "content": "You are a question parser expert."},
                {"role": "user", "content": prompt}
            ],
            "temperature": request_format.get("temperature", 0.3) if request_format else 0.3,
            "max_tokens": request_format.get("max_tokens", 2000) if request_format else 2000
        }
        
        # 构建API URL
        base_url = config['base_url']
        if base_url.endswith('/chat/completions'):
            api_url = base_url
        else:
            api_url = f"{base_url}/chat/completions"
        
        # 发送请求
        response = requests.post(
            api_url,
            headers=headers,
            json=request_body,
            timeout=config.get("timeout", 120)  # 增加到120秒
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
            timeout=config.get("timeout", 120)  # 增加到120秒
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
            timeout=config.get("timeout", 120)  # 增加到120秒
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
        
        # 使用自定义请求格式
        request_body = request_format.copy() if request_format else {}
        
        # 替换prompt变量
        request_body_str = json.dumps(request_body)
        request_body_str = request_body_str.replace("{prompt}", prompt)
        request_body = json.loads(request_body_str)
        
        response = requests.post(
            config['base_url'],
            headers=headers,
            json=request_body,
            timeout=config.get("timeout", 120)  # 增加到120秒
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
                content = response["choices"][0]["message"]["content"]
            elif parser_type == ResponseParser.ANTHROPIC_STANDARD:
                content = response["content"][0]["text"]
            else:
                # 自定义解析
                content = json.dumps(response)
            
            # 尝试从content中提取JSON
            json_start = content.find('[')
            json_end = content.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                questions_data = json.loads(json_str)
            else:
                # 尝试解析单个对象
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                json_str = content[json_start:json_end]
                questions_data = [json.loads(json_str)]
            
            # 转换为ParsedQuestion对象
            parsed_questions = []
            for q in questions_data:
                # 处理选项
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
                
                # 处理填空
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
            input_text=input_text[:1000],  # 限制长度
            parsed_result=parsed_result,
            success=success,
            error_message=error_message,
            response_time=response_time
        )
        self.db.add(log)
        self.db.commit()
    
    def test_interface(self, interface_id: str, test_prompt: str) -> Dict[str, Any]:
        """测试接口连通性"""
        try:
            interface = self._get_interface(interface_id)
            if not interface:
                return {"success": False, "error": "Interface not found"}
            
            start_time = time.time()
            response = self._call_interface(interface, test_prompt)
            response_time = int((time.time() - start_time) * 1000)
            
            return {
                "success": True,
                "response": str(response)[:500],  # 限制长度
                "response_time": response_time
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }