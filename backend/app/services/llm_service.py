"""
LLM Service Abstraction Layer
"""
import json
import time
import requests
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
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
            
            # 记录响应结构以便调试
            logger.info(f"响应类型: {type(response)}")
            logger.info(f"响应键: {response.keys() if isinstance(response, dict) else 'Not a dict'}")
            if isinstance(response, dict):
                # 记录每个键的值类型和部分内容
                for key in list(response.keys())[:5]:  # 只看前5个键
                    value = response[key]
                    if isinstance(value, str):
                        logger.info(f"  {key}: string[{len(value)}] = {value[:100]}...")
                    elif isinstance(value, (list, dict)):
                        logger.info(f"  {key}: {type(value).__name__} with {len(value)} items")
                    else:
                        logger.info(f"  {key}: {type(value).__name__} = {value}")
            
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
            
            # 获取原始响应内容用于调试
            raw_response = None
            if isinstance(response, dict):
                if 'choices' in response and response['choices']:
                    msg = response['choices'][0].get('message', {})
                    raw_response = msg.get('content', '') or msg.get('reasoning_content', '')
            
            return QuestionParseResponse(
                success=True,
                parsed_questions=parsed_questions,
                parse_errors=[],
                suggestions=self._generate_suggestions(parsed_questions),
                raw_response=raw_response  # 即使成功也返回原始响应，方便用户查看
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
            
            # 尝试返回原始响应供手动编辑
            raw_response = None
            if 'response' in locals():
                # 如果有响应对象，尝试提取内容
                try:
                    if isinstance(response, dict):
                        # 提取响应内容
                        if 'choices' in response and response['choices']:
                            msg = response['choices'][0].get('message', {})
                            # 优先使用content，如果为空则使用reasoning_content
                            raw_response = msg.get('content', '') or msg.get('reasoning_content', '')
                        elif 'content' in response:
                            raw_response = str(response['content'])
                        else:
                            raw_response = json.dumps(response, ensure_ascii=False)
                except:
                    raw_response = str(response)
            
            # 如果错误信息中包含JSON解析错误，尝试提取部分JSON
            if raw_response and 'JSON' in str(e):
                logger.info(f"JSON解析失败，返回原始响应供手动编辑，长度: {len(raw_response)}")
            
            return QuestionParseResponse(
                success=False,
                parsed_questions=[],
                parse_errors=[{"error": str(e)}],
                raw_response=raw_response,  # 添加原始响应
                needs_manual_edit=True if raw_response else False  # 标记需要手动编辑
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
        
        # 对于智谱AI，添加额外的JSON输出提示
        if "glm" in str(self.interfaces_cache.values()):
            prompt += "\n\n请确保输出纯JSON数组，不要包含任何解释或思考过程。"
        
        return prompt
    
    def _get_output_format(self) -> str:
        """获取输出格式说明"""
        return """
请直接返回JSON数组格式，不要包含任何其他文字说明或思考过程。
JSON格式要求，每个题目包含：
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
            "temperature": request_format.get("temperature", 0.3) if request_format else 0.3
        }
        
        # 不设置max_tokens，除非明确指定
        # OpenAI API会使用模型的默认最大值
        if request_format and "max_tokens" in request_format and request_format["max_tokens"] is not None:
            request_body["max_tokens"] = request_format["max_tokens"]
        
        # 构建API URL
        base_url = config['base_url']
        if base_url.endswith('/chat/completions'):
            api_url = base_url
        else:
            api_url = f"{base_url}/chat/completions"
        
        # 发送请求
        try:
            logger.info(f"请求URL: {api_url}")
            response = requests.post(
                api_url,
                headers=headers,
                json=request_body,
                timeout=config.get("timeout", 120)  # 增加到120秒
            )
            
            logger.info(f"响应状态: {response.status_code}")
            
            # 检查响应状态
            if response.status_code != 200:
                logger.error(f"API错误: {response.status_code} - {response.text[:500]}")
                response.raise_for_status()
            
            # 获取响应文本
            response_text = response.text
            logger.info(f"原始响应长度: {len(response_text)}")
            
            # 尝试解析JSON
            if not response_text:
                raise ValueError("Empty response")
                
            result = response.json()
            logger.info(f"JSON解析成功")
            
            # 记录完整响应结构（仅用于调试）
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"完整响应: {json.dumps(result, ensure_ascii=False, indent=2)[:1000]}")
            else:
                # 在INFO级别记录关键字段
                if isinstance(result, dict):
                    logger.info(f"响应包含的键: {list(result.keys())}")
                    if 'choices' in result and result['choices']:
                        first_choice = result['choices'][0]
                        logger.info(f"第一个choice的键: {list(first_choice.keys())}")
                        if 'message' in first_choice:
                            msg = first_choice['message']
                            logger.info(f"message的键: {list(msg.keys()) if isinstance(msg, dict) else type(msg)}")
                            if isinstance(msg, dict):
                                if 'content' in msg:
                                    logger.info(f"message.content长度: {len(msg['content'])}, 前100字符: {msg['content'][:100] if msg['content'] else 'EMPTY'}")
                                if 'reasoning_content' in msg:
                                    logger.info(f"message.reasoning_content长度: {len(msg['reasoning_content']) if msg['reasoning_content'] else 0}, 前100字符: {msg['reasoning_content'][:100] if msg['reasoning_content'] else 'EMPTY'}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}, 响应: {response.text[:500] if 'response' in locals() else 'N/A'}")
            raise ValueError(f"Failed to parse response: {e}")
    
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
            "max_tokens": 4096,  # Anthropic API要求必须设置，使用最大值
            "temperature": request_format.get("temperature", 0.3) if request_format else 0.3
        }
        
        # 如果用户指定了max_tokens，使用用户的值
        if request_format and "max_tokens" in request_format and request_format["max_tokens"] is not None:
            request_body["max_tokens"] = request_format["max_tokens"]
        
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
        api_key = config.get('api_key', '').strip()
        if not api_key:
            raise ValueError("智谱AI API密钥未配置")
            
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"调用智谱AI，模型: {config.get('model', 'glm-4')}")
        
        # 对于智谱AI，强调只返回JSON
        enhanced_prompt = prompt + "\n\n重要：直接输出JSON数组，不要包含任何解释、思考过程或其他文字。"
        
        # 构建消息列表
        messages = [{"role": "user", "content": enhanced_prompt}]
        
        # 添加系统提示词，强调JSON输出
        system_prompt = "你是一个专业的题目解析助手。请直接输出JSON格式的结果，不要包含任何其他解释或思考过程。"
        if request_format and "system_prompt" in request_format:
            system_prompt = request_format["system_prompt"] + "\n" + system_prompt
        messages.insert(0, {"role": "system", "content": system_prompt})
        
        request_body = {
            "model": config.get("model", "glm-4"),
            "messages": messages,
            "temperature": request_format.get("temperature", 0.3) if request_format else 0.3,
            "top_p": request_format.get("top_p", 1.0) if request_format else 1.0
            # 不设置max_tokens，让模型自由输出完整内容
        }
        
        # 只有在用户明确指定max_tokens时才添加限制
        if request_format and "max_tokens" in request_format and request_format["max_tokens"] is not None:
            request_body["max_tokens"] = request_format["max_tokens"]
        
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
        
        try:
            logger.info(f"请求URL: {api_url}")
            response = requests.post(
                api_url,
                headers=headers,
                json=request_body,
                timeout=config.get("timeout", 120)  # 增加到120秒
            )
            
            logger.info(f"响应状态: {response.status_code}")
            
            # 检查响应状态
            if response.status_code != 200:
                logger.error(f"API错误: {response.status_code} - {response.text[:500]}")
                response.raise_for_status()
            
            # 获取响应文本
            response_text = response.text
            logger.info(f"原始响应长度: {len(response_text)}")
            
            # 尝试解析JSON
            if not response_text:
                raise ValueError("Empty response")
                
            result = response.json()
            logger.info(f"JSON解析成功")
            
            # 记录完整响应结构（仅用于调试）
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"完整响应: {json.dumps(result, ensure_ascii=False, indent=2)[:1000]}")
            else:
                # 在INFO级别记录关键字段
                if isinstance(result, dict):
                    logger.info(f"响应包含的键: {list(result.keys())}")
                    if 'choices' in result and result['choices']:
                        first_choice = result['choices'][0]
                        logger.info(f"第一个choice的键: {list(first_choice.keys())}")
                        if 'message' in first_choice:
                            msg = first_choice['message']
                            logger.info(f"message的键: {list(msg.keys()) if isinstance(msg, dict) else type(msg)}")
                            if isinstance(msg, dict):
                                if 'content' in msg:
                                    logger.info(f"message.content长度: {len(msg['content'])}, 前100字符: {msg['content'][:100] if msg['content'] else 'EMPTY'}")
                                if 'reasoning_content' in msg:
                                    logger.info(f"message.reasoning_content长度: {len(msg['reasoning_content']) if msg['reasoning_content'] else 0}, 前100字符: {msg['reasoning_content'][:100] if msg['reasoning_content'] else 'EMPTY'}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}, 响应: {response.text[:500] if 'response' in locals() else 'N/A'}")
            raise ValueError(f"Failed to parse response: {e}")
    
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
            content = ""
            if parser_type == ResponseParser.OPENAI_STANDARD:
                # 处理OpenAI格式响应
                if "choices" in response and len(response["choices"]) > 0:
                    choice = response["choices"][0]
                    if "message" in choice:
                        msg = choice["message"]
                        # 优先使用content字段
                        content = msg.get("content", "")
                        # 如果content为空，尝试reasoning_content（智谱AI特有）
                        if not content and "reasoning_content" in msg:
                            content = msg.get("reasoning_content", "")
                            logger.info(f"使用reasoning_content字段，长度: {len(content)}")
                    elif "text" in choice:
                        content = choice["text"]
                    elif "delta" in choice and "content" in choice["delta"]:
                        content = choice["delta"]["content"]
            elif parser_type == ResponseParser.ANTHROPIC_STANDARD:
                if "content" in response:
                    if isinstance(response["content"], list) and len(response["content"]) > 0:
                        content = response["content"][0].get("text", "")
                    elif isinstance(response["content"], str):
                        content = response["content"]
            else:
                # 自定义解析
                content = json.dumps(response)
            
            # 如果content仍然为空，尝试其他字段
            if not content:
                if "result" in response:
                    content = response["result"]
                elif "data" in response:
                    content = response["data"]
                elif "message" in response:
                    content = response["message"]
                elif "text" in response:
                    content = response["text"]
                elif "output" in response:
                    content = response["output"]
                elif "response" in response:
                    content = response["response"]
            
            logger.info(f"准备解析内容长度: {len(content) if content else 0}, 前100字符: {content[:100] if content else 'EMPTY'}")
            
            # 清理content，移除可能的markdown代码块标记
            if '```json' in content:
                # 提取```json和```之间的内容
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                if json_match:
                    content = json_match.group(1)
                else:
                    content = content.replace('```json', '').replace('```', '')
            elif '```' in content:
                # 提取普通代码块
                import re
                code_match = re.search(r'```\s*(.*?)\s*```', content, re.DOTALL)
                if code_match:
                    content = code_match.group(1)
            
            # 尝试从content中提取JSON
            json_str = None
            
            # 方法1: 查找标记了JSON代码块的内容
            json_block_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
            if json_block_match:
                json_str = json_block_match.group(1)
                logger.info("从代码块中提取JSON")
            else:
                # 方法2: 查找最后一个完整的JSON数组
                # 从后往前找，因为通常实际结果在最后
                all_arrays = re.findall(r'\[(?:[^[\]]*|\[(?:[^[\]]*|\[[^[\]]*\])*\])*\]', content)
                if all_arrays:
                    # 选择最长的数组（通常是最完整的）
                    json_str = max(all_arrays, key=len)
                    logger.info(f"找到{len(all_arrays)}个JSON数组，选择最长的")
                else:
                    # 方法3: 简单查找[到]
                    json_start = content.find('[')
                    json_end = content.rfind(']') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = content[json_start:json_end]
            
            if json_str:
                # 清理可能的非法字符和注释
                json_str = json_str.strip()
                # 移除可能的尾随逗号
                json_str = re.sub(r',\s*}', '}', json_str)
                json_str = re.sub(r',\s*]', ']', json_str)
                logger.info(f"提取的JSON长度: {len(json_str)}")
                logger.info(f"提取的JSON数组前200字符: {json_str[:200]}")
                logger.info(f"提取的JSON数组后200字符: {json_str[-200:] if len(json_str) > 200 else 'N/A'}")
                try:
                    questions_data = json.loads(json_str)
                except json.JSONDecodeError as e:
                    # 如果还是失败，尝试修复常见的JSON错误
                    logger.warning(f"JSON解析失败: {e}, 尝试修复")
                    
                    # 方法1：尝试补全不完整的JSON
                    if "Expecting" in str(e) or "Unterminated" in str(e):
                        # 计算需要的闭合符号
                        open_braces = json_str.count('{') - json_str.count('}')
                        open_brackets = json_str.count('[') - json_str.count(']')
                        
                        # 尝试智能补全
                        fixed_json = json_str
                        
                        # 如果最后一个字符不是逗号或闭合符号，可能需要补全对象
                        if fixed_json and fixed_json[-1] not in ',}]':
                            # 检查是否在字符串中
                            if '"' not in fixed_json[-10:]:
                                fixed_json += '"'
                        
                        # 补全缺失的大括号
                        for _ in range(open_braces):
                            fixed_json += '}'
                        
                        # 补全缺失的方括号  
                        for _ in range(open_brackets):
                            fixed_json += ']'
                        
                        logger.info(f"尝试补全JSON，添加了 {open_braces} 个 }} 和 {open_brackets} 个 ]")
                        
                        try:
                            questions_data = json.loads(fixed_json)
                            logger.info("JSON补全成功")
                        except:
                            # 方法2：尝试截断到最后一个完整的对象
                            logger.warning("补全失败，尝试截断")
                            # 找到最后一个完整对象的结束位置
                            # 从后向前查找 "}," 模式
                            last_complete = json_str.rfind('},')
                            if last_complete > 0:
                                truncated = json_str[:last_complete+1] + ']'
                                logger.info(f"截断到位置 {last_complete}")
                                questions_data = json.loads(truncated)
                            else:
                                raise
                    else:
                        raise
            else:
                # 尝试解析单个对象
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    json_str = json_str.strip()
                    logger.info(f"提取的JSON对象: {json_str[:200]}")
                    questions_data = [json.loads(json_str)]
                else:
                    logger.error(f"无法从响应中提取JSON: {content[:500]}")
                    raise ValueError("No valid JSON found in response")
            
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