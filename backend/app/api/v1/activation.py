"""
Activation Code API - 激活码管理
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
import uuid
import random
import string

from app.core.database import get_qbank_db
from app.core.security import get_current_user
from app.models.user_models import User
from app.models.activation import ActivationCode, UserBankAccess, ExpireType
from app.models.question_models_v2 import QuestionBankV2
from app.schemas.activation_schemas import (
    ActivationCodeCreate,
    ActivationCodeResponse,
    ActivationCodeListResponse,
    ActivationRequest,
    ActivationResult,
    UserBankAccessResponse,
    MyAccessListResponse,
    ActivationCodeQuery
)

router = APIRouter()


# ==================== Helper Functions ====================

def generate_activation_code(length: int = 16) -> str:
    """生成激活码"""
    # 使用大写字母和数字，避免易混淆的字符（0, O, 1, I, L）
    chars = string.ascii_uppercase.replace('O', '').replace('I', '').replace('L', '') + string.digits.replace('0', '').replace('1', '')
    return ''.join(random.choice(chars) for _ in range(length))


def check_admin_permission(user: User) -> bool:
    """检查用户是否是管理员"""
    return user.role == "admin"


# ==================== User Activation Endpoints ====================

@router.post("/activate", response_model=ActivationResult, tags=["🔑 Activation"])
async def activate_bank(
    activation_request: ActivationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """使用激活码激活题库"""

    # 查找激活码
    code = db.query(ActivationCode).filter(
        ActivationCode.code == activation_request.code
    ).first()

    if not code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="激活码不存在"
        )

    # 检查是否已使用
    if code.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该激活码已被使用"
        )

    # 检查用户是否已有该题库的访问权限
    existing_access = db.query(UserBankAccess).filter(
        and_(
            UserBankAccess.user_id == current_user.id,
            UserBankAccess.bank_id == code.bank_id
        )
    ).first()

    if existing_access:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已拥有该题库的访问权限"
        )

    # 获取题库信息
    bank = db.query(QuestionBankV2).filter(
        QuestionBankV2.id == code.bank_id
    ).first()

    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题库不存在"
        )

    # 计算过期时间
    expire_at = None
    if code.expire_type == ExpireType.temporary and code.expire_days:
        expire_at = datetime.utcnow() + timedelta(days=code.expire_days)

    # 创建访问权限
    access = UserBankAccess(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        bank_id=code.bank_id,
        activated_by_code=code.id,
        activated_at=datetime.utcnow(),
        expire_at=expire_at,
        is_active=True
    )

    db.add(access)

    # 标记激活码为已使用
    code.is_used = True
    code.used_by = current_user.id
    code.used_at = datetime.utcnow()

    db.commit()

    return ActivationResult(
        success=True,
        message=f"成功激活题库：{bank.name}",
        bank_id=bank.id,
        bank_name=bank.name,
        expire_at=expire_at,
        activated_at=access.activated_at
    )


@router.get("/my-access", response_model=MyAccessListResponse, tags=["🔑 Activation"])
async def get_my_access(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """获取我的题库访问权限"""

    access_list = db.query(UserBankAccess).filter(
        UserBankAccess.user_id == current_user.id
    ).order_by(UserBankAccess.activated_at.desc()).all()

    # 获取题库信息
    bank_ids = [a.bank_id for a in access_list]
    banks = db.query(QuestionBankV2).filter(
        QuestionBankV2.id.in_(bank_ids)
    ).all()
    bank_info = {b.id: {"name": b.name, "description": b.description} for b in banks}

    # 构造响应
    response_list = []
    active_count = 0
    expired_count = 0

    for access in access_list:
        bank_data = bank_info.get(access.bank_id, {})
        is_expired = access.is_expired()

        if not is_expired and access.is_active:
            active_count += 1
        elif is_expired:
            expired_count += 1

        response_list.append(UserBankAccessResponse(
            id=access.id,
            user_id=access.user_id,
            bank_id=access.bank_id,
            bank_name=bank_data.get("name"),
            bank_description=bank_data.get("description"),
            activated_by_code=access.activated_by_code,
            activated_at=access.activated_at,
            expire_at=access.expire_at,
            is_active=access.is_active,
            is_expired=is_expired
        ))

    return MyAccessListResponse(
        access_list=response_list,
        total=len(response_list),
        active_count=active_count,
        expired_count=expired_count
    )


@router.get("/check-access/{bank_id}", tags=["🔑 Activation"])
async def check_bank_access(
    bank_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """检查是否有权限访问某个题库"""

    access = db.query(UserBankAccess).filter(
        and_(
            UserBankAccess.user_id == current_user.id,
            UserBankAccess.bank_id == bank_id,
            UserBankAccess.is_active == True
        )
    ).first()

    if not access:
        return {
            "has_access": False,
            "message": "您没有访问该题库的权限"
        }

    if access.is_expired():
        return {
            "has_access": False,
            "message": "您的访问权限已过期",
            "expired_at": access.expire_at
        }

    return {
        "has_access": True,
        "message": "您有权限访问该题库",
        "expire_at": access.expire_at
    }


# ==================== Admin Activation Code Management Endpoints ====================

@router.post("/admin/codes", response_model=List[ActivationCodeResponse], tags=["🔑 Activation - Admin"])
async def create_activation_codes(
    code_data: ActivationCodeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """创建激活码（管理员）"""

    # 检查管理员权限
    if not check_admin_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )

    # 检查题库是否存在
    bank = db.query(QuestionBankV2).filter(
        QuestionBankV2.id == code_data.bank_id
    ).first()

    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题库不存在"
        )

    # 如果是临时激活码，必须指定天数
    if code_data.expire_type == ExpireTypeEnum.temporary and not code_data.expire_days:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="临时激活码必须指定有效天数"
        )

    # 批量生成激活码
    created_codes = []
    for _ in range(code_data.count):
        # 生成唯一激活码
        while True:
            new_code = generate_activation_code()
            existing = db.query(ActivationCode).filter(
                ActivationCode.code == new_code
            ).first()
            if not existing:
                break

        # 创建激活码记录
        activation_code = ActivationCode(
            id=str(uuid.uuid4()),
            code=new_code,
            bank_id=code_data.bank_id,
            created_by=current_user.id,
            created_at=datetime.utcnow(),
            expire_type=code_data.expire_type,
            expire_days=code_data.expire_days,
            is_used=False,
            description=code_data.description
        )

        db.add(activation_code)
        created_codes.append(activation_code)

    db.commit()

    # 刷新并构造响应
    for code in created_codes:
        db.refresh(code)

    return [
        ActivationCodeResponse(
            id=code.id,
            code=code.code,
            bank_id=code.bank_id,
            bank_name=bank.name,
            created_by=code.created_by,
            created_at=code.created_at,
            expire_type=code.expire_type.value,
            expire_days=code.expire_days,
            is_used=code.is_used,
            used_by=code.used_by,
            used_at=code.used_at,
            description=code.description
        )
        for code in created_codes
    ]


@router.get("/admin/codes", response_model=ActivationCodeListResponse, tags=["🔑 Activation - Admin"])
async def list_activation_codes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    bank_id: Optional[str] = None,
    is_used: Optional[bool] = None,
    expire_type: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """获取激活码列表（管理员）"""

    # 检查管理员权限
    if not check_admin_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )

    query = db.query(ActivationCode)

    # 筛选条件
    if bank_id:
        query = query.filter(ActivationCode.bank_id == bank_id)
    if is_used is not None:
        query = query.filter(ActivationCode.is_used == is_used)
    if expire_type:
        query = query.filter(ActivationCode.expire_type == expire_type)
    if search:
        query = query.filter(
            or_(
                ActivationCode.code.contains(search),
                ActivationCode.description.contains(search)
            )
        )

    # 按创建时间倒序
    query = query.order_by(ActivationCode.created_at.desc())

    total = query.count()
    codes = query.offset(skip).limit(limit).all()

    # 统计已使用/未使用数量
    used_count = db.query(func.count(ActivationCode.id)).filter(
        ActivationCode.is_used == True
    ).scalar() or 0
    unused_count = total - used_count

    # 获取题库名称
    bank_ids = list(set(c.bank_id for c in codes))
    banks = db.query(QuestionBankV2).filter(
        QuestionBankV2.id.in_(bank_ids)
    ).all()
    bank_names = {b.id: b.name for b in banks}

    # 构造响应
    response_list = [
        ActivationCodeResponse(
            id=code.id,
            code=code.code,
            bank_id=code.bank_id,
            bank_name=bank_names.get(code.bank_id),
            created_by=code.created_by,
            created_at=code.created_at,
            expire_type=code.expire_type.value,
            expire_days=code.expire_days,
            is_used=code.is_used,
            used_by=code.used_by,
            used_at=code.used_at,
            description=code.description
        )
        for code in codes
    ]

    return ActivationCodeListResponse(
        codes=response_list,
        total=total,
        used_count=used_count,
        unused_count=unused_count
    )


@router.delete("/admin/codes/{code_id}", tags=["🔑 Activation - Admin"])
async def delete_activation_code(
    code_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """删除激活码（管理员）"""

    # 检查管理员权限
    if not check_admin_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )

    code = db.query(ActivationCode).filter(
        ActivationCode.id == code_id
    ).first()

    if not code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="激活码不存在"
        )

    # 如果已被使用，不允许删除（保持数据完整性）
    if code.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已使用的激活码不能删除"
        )

    db.delete(code)
    db.commit()

    return {"success": True, "message": "激活码已删除"}


# ==================== Admin User Access Management Endpoints ====================

@router.get("/admin/access", tags=["🔑 Activation - Admin"])
async def list_user_access(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user_id: Optional[int] = None,
    bank_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """获取用户访问权限列表（管理员）"""

    # 检查管理员权限
    if not check_admin_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )

    query = db.query(UserBankAccess)

    # 筛选条件
    if user_id:
        query = query.filter(UserBankAccess.user_id == user_id)
    if bank_id:
        query = query.filter(UserBankAccess.bank_id == bank_id)
    if is_active is not None:
        query = query.filter(UserBankAccess.is_active == is_active)

    # 按激活时间倒序
    query = query.order_by(UserBankAccess.activated_at.desc())

    total = query.count()
    access_list = query.offset(skip).limit(limit).all()

    # 获取题库名称
    bank_ids = list(set(a.bank_id for a in access_list))
    banks = db.query(QuestionBankV2).filter(
        QuestionBankV2.id.in_(bank_ids)
    ).all()
    bank_names = {b.id: b.name for b in banks}

    # 构造响应
    result = []
    for access in access_list:
        result.append({
            "id": access.id,
            "user_id": access.user_id,
            "bank_id": access.bank_id,
            "bank_name": bank_names.get(access.bank_id),
            "activated_by_code": access.activated_by_code,
            "activated_at": access.activated_at,
            "expire_at": access.expire_at,
            "is_active": access.is_active,
            "is_expired": access.is_expired()
        })

    return {
        "access_list": result,
        "total": total
    }


@router.put("/admin/access/{access_id}/revoke", tags=["🔑 Activation - Admin"])
async def revoke_user_access(
    access_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_qbank_db)
):
    """撤销用户访问权限（管理员）"""

    # 检查管理员权限
    if not check_admin_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )

    access = db.query(UserBankAccess).filter(
        UserBankAccess.id == access_id
    ).first()

    if not access:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="访问权限不存在"
        )

    access.is_active = False
    db.commit()

    return {"success": True, "message": "已撤销用户访问权限"}
