"""
Initialize preset prompt templates in database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_qbank_db
from app.models.llm_models import PromptTemplate
from app.services.prompt_templates import PRESET_TEMPLATES
import uuid


def init_preset_templates():
    """初始化预设提示词模板"""
    db = next(get_qbank_db())
    
    try:
        # 检查是否已有系统模板
        existing_count = db.query(PromptTemplate).filter_by(is_system=True).count()
        if existing_count > 0:
            print(f"已存在 {existing_count} 个系统模板，跳过初始化")
            return
        
        # 添加预设模板
        for template_data in PRESET_TEMPLATES:
            template = PromptTemplate(
                id=template_data["id"],
                user_id=None,  # 系统模板没有用户
                name=template_data["name"],
                type=template_data["type"],
                category=template_data.get("category"),
                content=template_data["content"],
                variables=template_data.get("variables", []),
                description=template_data.get("description"),
                example_input=template_data.get("example_input"),
                example_output=template_data.get("example_output"),
                is_public=True,  # 系统模板默认公开
                is_system=template_data.get("is_system", True),
                usage_count=0,
                rating=0
            )
            db.add(template)
            print(f"添加模板: {template.name}")
        
        db.commit()
        print(f"\n成功初始化 {len(PRESET_TEMPLATES)} 个预设模板！")
        
    except Exception as e:
        print(f"初始化失败: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_preset_templates()