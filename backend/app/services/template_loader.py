"""
Markdown Template Loader
加载和管理Markdown格式的提示词模板
"""
import os
import re
import yaml
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import hashlib


class TemplateLoader:
    """Markdown模板加载器"""
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            base_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "prompt_templates"
            )
        self.base_path = Path(base_path)
        self.templates_cache = {}
        
    def load_template(self, template_path: str) -> Dict[str, Any]:
        """加载单个模板文件"""
        file_path = Path(template_path)
        if not file_path.is_absolute():
            file_path = self.base_path / template_path
            
        if not file_path.exists():
            raise FileNotFoundError(f"Template not found: {file_path}")
            
        # 检查缓存
        file_hash = self._get_file_hash(file_path)
        if str(file_path) in self.templates_cache:
            cached = self.templates_cache[str(file_path)]
            if cached['hash'] == file_hash:
                return cached['data']
        
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析模板
        template_data = self._parse_markdown_template(content)
        template_data['file_path'] = str(file_path)
        template_data['file_hash'] = file_hash
        
        # 更新缓存
        self.templates_cache[str(file_path)] = {
            'hash': file_hash,
            'data': template_data
        }
        
        return template_data
    
    def _parse_markdown_template(self, content: str) -> Dict[str, Any]:
        """解析Markdown模板格式"""
        # 分离YAML前置内容和Markdown内容
        parts = re.split(r'^---\s*$', content, maxsplit=2, flags=re.MULTILINE)
        
        if len(parts) >= 3:
            # 有YAML前置内容
            yaml_content = parts[1].strip()
            markdown_content = parts[2].strip()
            
            # 解析YAML
            try:
                metadata = yaml.safe_load(yaml_content) or {}
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML metadata: {e}")
        else:
            # 没有YAML前置内容，全部作为Markdown
            metadata = {}
            markdown_content = content.strip()
        
        # 解析Markdown中的变量占位符
        variables = self._extract_variables(markdown_content)
        
        # 解析示例部分
        examples = self._extract_examples(markdown_content)
        
        # 构建模板数据
        template_data = {
            'id': metadata.get('id', self._generate_id(markdown_content)),
            'name': metadata.get('name', 'Unnamed Template'),
            'type': metadata.get('type', 'general'),
            'category': metadata.get('category', 'default'),
            'version': metadata.get('version', '1.0.0'),
            'author': metadata.get('author', 'unknown'),
            'tags': metadata.get('tags', []),
            'variables': metadata.get('variables', variables),
            'content': self._process_content(markdown_content),
            'raw_content': markdown_content,
            'metadata': metadata,
            'examples': examples
        }
        
        return template_data
    
    def _extract_variables(self, content: str) -> Dict[str, str]:
        """提取模板中的变量"""
        # 查找 {{variable}} 格式的变量
        pattern = r'\{\{(\w+)\}\}'
        variables = set(re.findall(pattern, content))
        
        # 返回变量字典（变量名: 描述）
        var_dict = {}
        for var in variables:
            var_dict[var] = f"Variable: {var}"
        
        return var_dict
    
    def _extract_examples(self, content: str) -> List[Dict[str, str]]:
        """提取示例部分"""
        examples = []
        
        # 查找示例部分（### 示例 或 ## 示例）
        example_pattern = r'###?\s*示例.*?\n(.*?)(?=###?\s*|$)'
        example_matches = re.findall(example_pattern, content, re.DOTALL)
        
        for match in example_matches:
            # 提取输入和输出
            input_pattern = r'\*\*输入[：:]\*\*\s*\n```[^\n]*\n(.*?)\n```'
            output_pattern = r'\*\*输出[：:]\*\*\s*\n```[^\n]*\n(.*?)\n```'
            
            input_match = re.search(input_pattern, match, re.DOTALL)
            output_match = re.search(output_pattern, match, re.DOTALL)
            
            if input_match and output_match:
                examples.append({
                    'input': input_match.group(1).strip(),
                    'output': output_match.group(1).strip()
                })
        
        return examples
    
    def _process_content(self, markdown_content: str) -> str:
        """处理Markdown内容为纯文本提示词"""
        # 移除Markdown标题标记
        content = re.sub(r'^#+\s+', '', markdown_content, flags=re.MULTILINE)
        
        # 移除代码块标记但保留内容
        content = re.sub(r'```[^\n]*\n(.*?)\n```', r'\1', content, flags=re.DOTALL)
        
        # 移除强调标记
        content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
        content = re.sub(r'\*(.*?)\*', r'\1', content)
        
        # 移除示例部分（可选，因为示例可能需要包含在提示词中）
        # content = re.sub(r'###?\s*示例.*?(?=###?\s*|$)', '', content, flags=re.DOTALL)
        
        return content.strip()
    
    def _generate_id(self, content: str) -> str:
        """生成模板ID"""
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _get_file_hash(self, file_path: Path) -> str:
        """获取文件哈希值"""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def load_all_templates(self, category: str = None) -> List[Dict[str, Any]]:
        """加载所有模板"""
        templates = []
        
        # 遍历所有子目录
        for subdir in ['system', 'user', 'shared']:
            dir_path = self.base_path / subdir
            if not dir_path.exists():
                continue
                
            # 查找所有.md文件
            for file_path in dir_path.glob('*.md'):
                try:
                    template = self.load_template(str(file_path.relative_to(self.base_path)))
                    if category is None or template.get('category') == category:
                        template['source'] = subdir  # 标记来源
                        templates.append(template)
                except Exception as e:
                    print(f"Error loading template {file_path}: {e}")
        
        return templates
    
    def save_template(self, template_data: Dict[str, Any], subdir: str = 'user') -> str:
        """保存模板到文件"""
        # 准备YAML前置内容
        metadata = {
            'id': template_data.get('id'),
            'name': template_data.get('name'),
            'type': template_data.get('type'),
            'category': template_data.get('category'),
            'version': template_data.get('version', '1.0.0'),
            'author': template_data.get('author'),
            'tags': template_data.get('tags', []),
            'variables': template_data.get('variables', {})
        }
        
        # 生成文件名
        file_name = f"{template_data.get('id', 'template')}.md"
        file_path = self.base_path / subdir / file_name
        
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 构建文件内容
        yaml_content = yaml.dump(metadata, allow_unicode=True, sort_keys=False)
        markdown_content = template_data.get('raw_content', template_data.get('content', ''))
        
        file_content = f"---\n{yaml_content}---\n\n{markdown_content}"
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        return str(file_path)
    
    def delete_template(self, template_id: str, subdir: str = 'user') -> bool:
        """删除模板文件"""
        file_path = self.base_path / subdir / f"{template_id}.md"
        if file_path.exists():
            file_path.unlink()
            # 清除缓存
            if str(file_path) in self.templates_cache:
                del self.templates_cache[str(file_path)]
            return True
        return False
    
    def render_template(self, template_data: Dict[str, Any], variables: Dict[str, str]) -> str:
        """渲染模板，替换变量"""
        content = template_data.get('content', '')
        
        # 替换变量
        for var_name, var_value in variables.items():
            content = content.replace(f"{{{{{var_name}}}}}", var_value)
        
        return content


# 全局实例
template_loader = TemplateLoader()