"""
LLM Interface and Template Management API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_qbank_db, get_main_db
from app.core.security import get_current_admin_user, get_admin_user_from_session
from app.models.llm_models import LLMInterface, PromptTemplate
from app.schemas.llm_schemas import (
    LLMInterfaceCreate, LLMInterfaceUpdate, LLMInterfaceResponse,
    PromptTemplateCreate, PromptTemplateUpdate, PromptTemplateResponse,
    QuestionParseRequest, QuestionParseResponse,
    BatchImportRequest, BatchImportResponse,
    InterfaceTestRequest, InterfaceTestResponse
)
from app.services.llm_service import LLMService
from app.services.prompt_templates import get_all_preset_templates
from app.models.question_models import Question, QuestionOption, QuestionBank
import uuid
import json

router = APIRouter(prefix="/llm", tags=["LLM"])


# ============ LLM Interface Management ============

@router.get("/interfaces", response_model=List[LLMInterfaceResponse])
async def get_interfaces(
    request: Request,
    current_user=Depends(get_admin_user_from_session),
    db: Session = Depends(get_qbank_db),
    only_active: bool = False
):
    """获取所有LLM接口配置"""
    query = db.query(LLMInterface).filter_by(user_id=current_user.id)
    if only_active:
        query = query.filter_by(is_active=True)
    interfaces = query.all()
    return interfaces


@router.get("/interfaces/{interface_id}", response_model=LLMInterfaceResponse)
async def get_interface(
    interface_id: str,
    request: Request,
    current_user=Depends(get_admin_user_from_session),
    db: Session = Depends(get_qbank_db)
):
    """获取单个接口配置"""
    interface = db.query(LLMInterface).filter_by(
        id=interface_id,
        user_id=current_user.id
    ).first()
    if not interface:
        raise HTTPException(status_code=404, detail="Interface not found")
    return interface


@router.post("/interfaces", response_model=LLMInterfaceResponse)
async def create_interface(
    interface_data: LLMInterfaceCreate,
    request: Request,
    current_user=Depends(get_admin_user_from_session),
    db: Session = Depends(get_qbank_db)
):
    """创建新的LLM接口配置"""
    # 如果设置为默认，先取消其他默认
    if interface_data.is_default:
        db.query(LLMInterface).filter_by(
            user_id=current_user.id,
            is_default=True
        ).update({"is_default": False})
    
    interface = LLMInterface(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=interface_data.name,
        type=interface_data.type,
        config=interface_data.config.dict(),
        request_format=interface_data.request_format.dict() if interface_data.request_format else None,
        response_parser=interface_data.response_parser,
        prompt_template_id=interface_data.prompt_template_id,
        is_active=interface_data.is_active,
        is_default=interface_data.is_default
    )
    db.add(interface)
    db.commit()
    db.refresh(interface)
    return interface


@router.put("/interfaces/{interface_id}", response_model=LLMInterfaceResponse)
async def update_interface(
    interface_id: str,
    interface_data: LLMInterfaceUpdate,
    request: Request,
    current_user=Depends(get_admin_user_from_session),
    db: Session = Depends(get_qbank_db)
):
    """更新接口配置"""
    interface = db.query(LLMInterface).filter_by(
        id=interface_id,
        user_id=current_user.id
    ).first()
    if not interface:
        raise HTTPException(status_code=404, detail="Interface not found")
    
    # 如果设置为默认，先取消其他默认
    if interface_data.is_default:
        db.query(LLMInterface).filter_by(
            user_id=current_user.id,
            is_default=True
        ).update({"is_default": False})
    
    # 更新字段
    update_data = interface_data.dict(exclude_unset=True)
    if "config" in update_data:
        update_data["config"] = interface_data.config.dict()
    if "request_format" in update_data:
        update_data["request_format"] = interface_data.request_format.dict()
    
    for key, value in update_data.items():
        setattr(interface, key, value)
    
    db.commit()
    db.refresh(interface)
    return interface


@router.delete("/interfaces/{interface_id}")
async def delete_interface(
    interface_id: str,
    request: Request,
    current_user=Depends(get_admin_user_from_session),
    db: Session = Depends(get_qbank_db)
):
    """删除接口配置"""
    interface = db.query(LLMInterface).filter_by(
        id=interface_id,
        user_id=current_user.id
    ).first()
    if not interface:
        raise HTTPException(status_code=404, detail="Interface not found")
    
    db.delete(interface)
    db.commit()
    return {"message": "Interface deleted successfully"}


@router.post("/interfaces/{interface_id}/test", response_model=InterfaceTestResponse)
async def test_interface(
    interface_id: str,
    test_request: InterfaceTestRequest,
    request: Request,
    current_user=Depends(get_admin_user_from_session),
    db: Session = Depends(get_qbank_db)
):
    """测试接口连通性"""
    interface = db.query(LLMInterface).filter_by(
        id=interface_id,
        user_id=current_user.id
    ).first()
    if not interface:
        raise HTTPException(status_code=404, detail="Interface not found")
    
    llm_service = LLMService(db)
    result = llm_service.test_interface(interface_id, test_request.test_prompt)
    return InterfaceTestResponse(**result)


# ============ Prompt Template Management ============

@router.get("/templates", response_model=List[PromptTemplateResponse])
async def get_templates(
    request: Request,
    current_user=Depends(get_admin_user_from_session),
    db: Session = Depends(get_qbank_db),
    include_system: bool = True,
    include_public: bool = True
):
    """获取提示词模板"""
    templates = []
    
    # 用户自己的模板
    user_templates = db.query(PromptTemplate).filter_by(user_id=current_user.id).all()
    templates.extend(user_templates)
    
    # 系统预设模板
    if include_system:
        system_templates = db.query(PromptTemplate).filter_by(is_system=True).all()
        templates.extend(system_templates)
    
    # 公开模板
    if include_public:
        public_templates = db.query(PromptTemplate).filter_by(is_public=True).filter(
            PromptTemplate.user_id != current_user.id
        ).all()
        templates.extend(public_templates)
    
    return templates


@router.get("/templates/presets")
async def get_preset_templates():
    """获取预设模板（无需登录）"""
    return get_all_preset_templates()


@router.get("/templates/{template_id}", response_model=PromptTemplateResponse)
async def get_template(
    template_id: str,
    req: Request,
    current_user=Depends(get_admin_user_from_session),
    db: Session = Depends(get_qbank_db)
):
    """获取单个模板"""
    template = db.query(PromptTemplate).filter_by(id=template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # 检查权限
    if not template.is_system and not template.is_public and template.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return template


@router.post("/templates", response_model=PromptTemplateResponse)
async def create_template(
    template_data: PromptTemplateCreate,
    request: Request,
    current_user=Depends(get_admin_user_from_session),
    db: Session = Depends(get_qbank_db)
):
    """创建新模板"""
    template = PromptTemplate(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=template_data.name,
        type=template_data.type,
        category=template_data.category,
        content=template_data.content,
        variables=template_data.variables,
        description=template_data.description,
        example_input=template_data.example_input,
        example_output=template_data.example_output,
        is_public=template_data.is_public,
        is_system=False
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.put("/templates/{template_id}", response_model=PromptTemplateResponse)
async def update_template(
    template_id: str,
    template_data: PromptTemplateUpdate,
    req: Request,
    current_user=Depends(get_admin_user_from_session),
    db: Session = Depends(get_qbank_db)
):
    """更新模板"""
    template = db.query(PromptTemplate).filter_by(
        id=template_id,
        user_id=current_user.id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found or access denied")
    
    update_data = template_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(template, key, value)
    
    db.commit()
    db.refresh(template)
    return template


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: str,
    req: Request,
    current_user=Depends(get_admin_user_from_session),
    db: Session = Depends(get_qbank_db)
):
    """删除模板"""
    template = db.query(PromptTemplate).filter_by(
        id=template_id,
        user_id=current_user.id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.delete(template)
    db.commit()
    return {"message": "Template deleted successfully"}


# ============ Question Parsing ============

@router.post("/parse", response_model=QuestionParseResponse)
async def parse_questions(
    request: QuestionParseRequest,
    req: Request,
    current_user=Depends(get_admin_user_from_session),
    db: Session = Depends(get_qbank_db)
):
    """使用LLM解析题目"""
    llm_service = LLMService(db)
    response = llm_service.parse_questions(request, current_user.id)
    return response


@router.post("/import", response_model=BatchImportResponse)
async def batch_import_questions(
    request: BatchImportRequest,
    req: Request,
    current_user=Depends(get_admin_user_from_session),
    db: Session = Depends(get_qbank_db)
):
    """批量导入解析后的题目"""
    # 验证题库存在
    bank = db.query(QuestionBank).filter_by(id=request.bank_id).first()
    if not bank:
        raise HTTPException(status_code=404, detail="Question bank not found")
    
    imported_count = 0
    skipped_count = 0
    failed_count = 0
    errors = []
    
    for parsed_q in request.questions:
        try:
            # 检查重复（根据题干）
            if request.skip_duplicates:
                existing = db.query(Question).filter_by(
                    bank_id=request.bank_id,
                    stem=parsed_q.stem
                ).first()
                if existing:
                    skipped_count += 1
                    continue
            
            # 创建题目
            question = Question(
                id=str(uuid.uuid4()),
                bank_id=request.bank_id,
                stem=parsed_q.stem,
                stem_format="text",
                type=parsed_q.type,
                difficulty=parsed_q.difficulty,
                category=parsed_q.category,
                tags=parsed_q.tags,
                explanation=parsed_q.explanation
            )
            
            # 处理不同题型的特殊字段
            if parsed_q.type == "fill":
                # 填空题：存储答案到meta_data
                question.meta_data = {
                    "blanks": [blank.dict() for blank in parsed_q.blanks] if parsed_q.blanks else []
                }
            elif parsed_q.type == "judge":
                # 判断题：存储答案到meta_data
                question.meta_data = {
                    "correct_answer": parsed_q.correct_answer
                }
            elif parsed_q.type in ["single", "multiple"]:
                # 选择题：创建选项
                if parsed_q.options:
                    for i, opt in enumerate(parsed_q.options):
                        option = QuestionOption(
                            id=str(uuid.uuid4()),
                            question_id=question.id,
                            option_label=opt.label,
                            option_content=opt.content,
                            is_correct=opt.is_correct,
                            sort_order=i
                        )
                        db.add(option)
            
            db.add(question)
            imported_count += 1
            
        except Exception as e:
            failed_count += 1
            errors.append({
                "question": parsed_q.stem[:50],
                "error": str(e)
            })
    
    db.commit()
    
    return BatchImportResponse(
        success=imported_count > 0,
        imported_count=imported_count,
        skipped_count=skipped_count,
        failed_count=failed_count,
        errors=errors
    )