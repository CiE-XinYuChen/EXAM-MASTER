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
from concurrent.futures import ThreadPoolExecutor, as_completed

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
        """解析题目文本 (支持长文本自动分块和并发处理)"""
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
            
        # 预处理：检查文本长度，决定是否分块
        CHUNK_SIZE = 2000  # 字符数阈值
        
        # 检查是否禁用分块
        disable_chunking = False
        if request.custom_variables and str(request.custom_variables.get("disable_chunking", "")).lower() == "true":
            disable_chunking = True
        
        # 如果接口配置中禁用了分块（可选，这里暂不从接口配置读，主要看请求参数）
        
        all_errors = []
        # 用于存储分块结果: {index: [questions], ...}
        chunk_results = {}
        # 用于存储原始响应: {index: raw_response_str, ...}
        chunk_raw_responses = {}
        
        # 简单的分块策略：按题号或段落
        if disable_chunking or len(request.raw_text) < CHUNK_SIZE:
            if disable_chunking:
                logger.info(f"用户请求禁用分块处理 (文本长度: {len(request.raw_text)})")
            chunks = [request.raw_text]
        else:
            logger.info(f"文本较长 ({len(request.raw_text)} chars)，启用自动分块处理")
            chunks = self._chunk_text(request.raw_text)
            logger.info(f"分块完成，共 {len(chunks)} 块")
            
        # 定义单个块的处理函数
        def process_chunk(chunk_index: int, chunk_text: str):
            logger.info(f"开始处理第 {chunk_index+1}/{len(chunks)} 块 (长度: {len(chunk_text)})")
            chunk_start = time.time()
            
            # 构建提示词
            prompt = self._build_prompt(template, chunk_text, request.custom_variables)
            
            try:
                # 调用LLM接口
                response = self._call_interface(interface, prompt)
                
                # 记录响应
                raw_resp = ""
                if isinstance(response, dict):
                    if 'choices' in response and response['choices']:
                        msg = response['choices'][0].get('message', {})
                        raw_resp = msg.get('content', '') or msg.get('reasoning_content', '')
                    elif 'content' in response:
                        raw_resp = str(response['content'])
                else:
                    raw_resp = str(response)
                
                # 解析响应
                parsed = self._parse_response(response, interface.response_parser)
                
                elapsed = time.time() - chunk_start
                logger.info(f"第 {chunk_index+1} 块处理完成，耗时 {elapsed:.2f}s，解析出 {len(parsed)} 道题")
                
                return {
                    "index": chunk_index,
                    "parsed": parsed,
                    "raw": raw_resp,
                    "success": True
                }
                
            except Exception as e:
                elapsed = time.time() - chunk_start
                logger.error(f"第 {chunk_index+1} 块处理失败 (耗时 {elapsed:.2f}s): {str(e)}")
                return {
                    "index": chunk_index,
                    "error": str(e),
                    "success": False
                }

        # 使用线程池并发处理
        # 限制并发数为3，避免触发API速率限制
        max_workers = min(3, len(chunks))
        logger.info(f"启动并发处理，线程数: {max_workers}")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_chunk = {
                executor.submit(process_chunk, i, chunk): i 
                for i, chunk in enumerate(chunks)
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_chunk):
                result = future.result()
                idx = result["index"]
                
                if result["success"]:
                    chunk_results[idx] = result["parsed"]
                    chunk_raw_responses[idx] = result["raw"]
                else:
                    all_errors.append({"chunk_index": idx, "error": result["error"]})
                    # 失败时也要占位，保证顺序（或者直接忽略，取决于策略）
                    chunk_results[idx] = []
                    chunk_raw_responses[idx] = f"[Error in chunk {idx}: {result['error']}]"

        # 按顺序合并结果
        all_parsed_questions = []
        ordered_raw_responses = []
        
        for i in range(len(chunks)):
            if i in chunk_results:
                all_parsed_questions.extend(chunk_results[i])
            if i in chunk_raw_responses:
                ordered_raw_responses.append(chunk_raw_responses[i])
        
        # 记录总日志
        response_time = int((time.time() - start_time) * 1000)
        self._log_parse(
            interface_id=interface.id,
            user_id=user_id,
            input_text=request.raw_text, # 记录完整文本
            parsed_result={"questions": [q.dict() for q in all_parsed_questions]},
            success=len(all_errors) == 0,
            error_message=str(all_errors) if all_errors else None,
            response_time=response_time
        )
        
        # 更新使用统计
        interface.usage_count += 1
        interface.last_used_at = datetime.utcnow()
        template.usage_count += 1
        self.db.commit()
        
        return QuestionParseResponse(
            success=len(all_parsed_questions) > 0,
            parsed_questions=all_parsed_questions,
            parse_errors=all_errors,
            suggestions=self._generate_suggestions(all_parsed_questions),
            raw_response="\n\n--- Chunk Separator ---\n\n".join(ordered_raw_responses)
        )

    def _chunk_text(self, text: str, max_chunk_size: int = 1500) -> List[str]:
        """
        智能文本分块
        尝试按题目编号或段落分割，保持每块大小适中
        """
        lines = text.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        # 题号匹配正则 (支持 "1.", "1、", "(1)", "一、", "Question 1")
        question_start_pattern = re.compile(r'^\s*(\d+[\.、\)]|\(\d+\)|[一二三四五六七八九十]+[\.、]|Question\s+\d+|第\d+题)')
        
        for line in lines:
            line_len = len(line)
            is_new_question = bool(question_start_pattern.match(line))
            
            # 如果当前块加上新行会过大，且当前行看起来是新题目的开始，或者当前块已经非常大
            if (current_size + line_len > max_chunk_size and is_new_question) or (current_size > max_chunk_size * 1.5):
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                    current_chunk = []
                    current_size = 0
            
            current_chunk.append(line)
            current_size += line_len
            
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
            
        return chunks
    
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
        
        # 针对长文本分块处理的补充指令
        prompt += "\n\n【重要补充规则】\n"
        prompt += "1. 输入文本可能是长试卷的其中一个片段（分块）。\n"
        prompt += "2. 如果文本的开头或结尾包含不完整的题目（例如只有选项没有题干，或只有题干没有选项），请**直接忽略**这些残缺的题目，不要强行解析或输出。\n"
        prompt += "3. 确保输出格式为合法的JSON数组，不要包含Markdown标记、代码块符号（```）或其他解释性文字。\n"
        
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
        if request_format and "max_tokens" in request_format and request_format["max_tokens"] is not None:
            request_body["max_tokens"] = request_format["max_tokens"]
            
        # 添加其他OpenAI支持的可选参数
        supported_params = {
            "top_p", "stop", "presence_penalty", "frequency_penalty", "logit_bias", "user", "seed"
        }
        
        # 针对Kimi模型的特殊处理：移除不支持的参数
        model_name = config.get("model", "").lower()
        if "kimi" in model_name or "moonshot" in model_name:
            supported_params.discard("frequency_penalty")
            supported_params.discard("presence_penalty")
            supported_params.discard("logit_bias")
            # Kimi可能对stop参数格式有特殊要求，或者不支持空列表，暂且保留但在下面做空检查
        
        if request_format:
            for key, value in request_format.items():
                if key in supported_params and value is not None:
                    # 再次检查：空列表不传递
                    if key == "stop" and isinstance(value, list) and not value:
                        continue
                    request_body[key] = value
        
        # 构建API URL
        base_url = config['base_url']
        if base_url.endswith('/chat/completions'):
            api_url = base_url
        else:
            api_url = f"{base_url}/chat/completions"
        
        # 发送请求
        try:
            logger.info(f"请求URL: {api_url}")
            
            # 获取超时设置，默认为300秒（5分钟），适应聚合API的延迟
            timeout = max(config.get("timeout", 300), 300)
            
            response = requests.post(
                api_url,
                headers=headers,
                json=request_body,
                timeout=timeout
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
        
        # 构建请求体
        request_body = {
            "model": config.get("model", "claude-3-sonnet-20240229"),
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096,  # Anthropic API要求必须设置，使用最大值
            "temperature": request_format.get("temperature", 0.3) if request_format else 0.3
        }
        
        # 如果用户指定了max_tokens，使用用户的值
        if request_format and "max_tokens" in request_format and request_format["max_tokens"] is not None:
            request_body["max_tokens"] = request_format["max_tokens"]
            
        # 添加其他Claude支持的可选参数
        supported_params = {
            "top_p", "top_k", "stop_sequences", "system", "metadata"
        }
        
        if request_format:
            for key, value in request_format.items():
                if key in supported_params and value is not None:
                    request_body[key] = value
        
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
        """调用智谱AI接口 (使用官方SDK)"""
        try:
            from zhipuai import ZhipuAI
        except ImportError:
            raise ValueError("未安装 zhipuai 库，请运行 pip install zhipuai>=2.0.0")
        
        api_key = config.get('api_key', '').strip()
        if not api_key:
            raise ValueError("智谱AI API密钥未配置")
            
        # 处理 base_url
        base_url = config.get('base_url')
        if not base_url or base_url.strip() == "":
            base_url = None
        elif base_url.rstrip("/") == "https://open.bigmodel.cn":
            # 如果用户错误地设置了根域名��强制使用默认值（None）
            logger.warning("检测到错误的智谱AI Base URL配置，已自动修正为默认值")
            base_url = None
            
        # 初始化客户端
        client = ZhipuAI(api_key=api_key, base_url=base_url)
        
        logger.info(f"调用智谱AI (SDK)，模型: {config.get('model', 'glm-4')}")
        
        # 对于智谱AI，强调只返回JSON
        enhanced_prompt = prompt + "\n\n重要：直接输出JSON数组，不要包含任何解释、思考过程或其他文字。"
        
        # 构建消息列表
        messages = [{"role": "user", "content": enhanced_prompt}]
        
        # 添加系统提示词，强调JSON输出
        system_prompt = "你是一个专业的题目解析助手。请直接输出JSON格式的结果，不要包含任何其他解释或思考过程。"
        if request_format and "system_prompt" in request_format:
            system_prompt = request_format["system_prompt"] + "\n" + system_prompt
        messages.insert(0, {"role": "system", "content": system_prompt})
        
        # 准备参数
        # 基础参数
        temp = request_format.get("temperature") if request_format else 0.3
        if temp is None: temp = 0.3
        
        top_p = request_format.get("top_p") if request_format else 1.0
        if top_p is None: top_p = 1.0

        kwargs = {
            "model": config.get("model", "glm-4"),
            "messages": messages,
            "temperature": float(temp),
            "top_p": float(top_p),
            "stream": False
        }
        
        # 只有在用户明确指定max_tokens时才添加限制
        if request_format and "max_tokens" in request_format and request_format["max_tokens"] is not None:
            kwargs["max_tokens"] = int(request_format["max_tokens"])
            
        # 添加其他智谱AI支持的可选参数
        # 显式白名单过滤，防止传入API不支持的参数导致400错误
        supported_params = {
            "stop", "tools", "tool_choice", "request_id", "do_sample", "user_id", "thinking"
        }
        
        if request_format:
            for key, value in request_format.items():
                if key in supported_params and value is not None:
                    # 特殊处理：如果列表为空，则不传递（防止API报错）
                    if key in ["stop", "tools"] and isinstance(value, list) and len(value) == 0:
                        continue
                    kwargs[key] = value
        
        try:
            logger.info(f"发送给智谱AI SDK的参数: {json.dumps({k: v for k, v in kwargs.items() if k != 'messages'}, ensure_ascii=False)}")
            # 调用SDK
            response = client.chat.completions.create(**kwargs)
            
            # 获取第一个choice
            choice = response.choices[0]
            content = choice.message.content
            
            logger.info(f"智谱AI SDK返回内容长度: {len(content) if content else 0}")
            if not content:
                logger.warning(f"智谱AI SDK返回空内容! Finish reason: {choice.finish_reason}")
                # 检查是否有工具调用
                if choice.message.tool_calls:
                    logger.info(f"检测到工具调用: {choice.message.tool_calls}")
            
            # 构造兼容的返回结果
            result = {
                "choices": [
                    {
                        "message": {
                            "content": content,
                            "role": choice.message.role
                        },
                        "finish_reason": choice.finish_reason
                    }
                ],
                "usage": response.usage.model_dump() if response.usage else {}
            }
            
            logger.info("智谱AI调用成功")
            
            return result
            
        except Exception as e:
            logger.error(f"智谱AI SDK调用失败: {e}")
            raise
    
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
            # 尝试匹配 ```json ... ``` 或 ``` ... ```
            code_block_match = re.search(r'```(?:json)?\s*(.*?)\s*```', content, re.DOTALL | re.IGNORECASE)
            if code_block_match:
                content = code_block_match.group(1)
                logger.info("已移除Markdown代码块标记")
            else:
                # 如果没有匹配到成对的 code block，尝试简单的移除
                if '```' in content:
                    content = content.replace('```json', '').replace('```', '')
                    logger.info("已移除Markdown标记 (Fallback)")
            
            logger.info(f"清理后内容前100字符: {content[:100] if content else 'EMPTY'}")
            
            # 尝试从content中提取JSON
            json_str = None
            
            # 方法1: 查找标记了JSON代码块的内容 (已经在前面处理过)
            # 如果前面匹配成功，content已经是纯JSON字符串
            # 如果前面没有匹配成功，尝试最后的手段：查找首尾的大括号或方括号
            
            # 简单的 heuristic: 检查是否以 [ 或 { 开始 (允许空白)
            stripped_content = content.strip()
            if stripped_content.startswith('[') or stripped_content.startswith('{'):
                json_str = content
            else:
                # 方法2 (原方法3): 简单查找[到]
                json_start = content.find('[')
                json_end = content.rfind(']') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    logger.info("通过查找方括号提取JSON")
                else:
                    # 尝试找对象
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = content[json_start:json_end]
                        logger.info("通过查找大括号提取JSON")
            
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