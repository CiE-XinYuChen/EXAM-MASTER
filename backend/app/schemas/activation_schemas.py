"""
Activation Code Schemas
激活码相关的Pydantic模型
"""

from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class ExpireTypeEnum(str, Enum):
    """激活码过期类型"""
    permanent = "permanent"  # 永久
    temporary = "temporary"  # 临时


# ==================== Activation Code Schemas ====================

class ActivationCodeCreate(BaseModel):
    """创建激活码（管理员）"""
    bank_id: str = Field(..., description="题库ID")
    expire_type: ExpireTypeEnum = Field(default=ExpireTypeEnum.permanent, description="过期类型")
    expire_days: Optional[int] = Field(None, ge=1, le=3650, description="有效天数（临时激活码必填）")
    description: Optional[str] = Field(None, max_length=200, description="激活码描述")
    count: int = Field(1, ge=1, le=100, description="生成数量")


class ActivationCodeResponse(BaseModel):
    """激活码响应"""
    id: str
    code: str
    bank_id: str
    bank_name: Optional[str] = None  # 可以从关联的bank获取
    created_by: int
    created_at: datetime
    expire_type: str
    expire_days: Optional[int]
    is_used: bool
    used_by: Optional[int]
    used_at: Optional[datetime]
    description: Optional[str]

    class Config:
        from_attributes = True


class ActivationCodeListResponse(BaseModel):
    """激活码列表响应"""
    codes: List[ActivationCodeResponse]
    total: int
    used_count: int
    unused_count: int


# ==================== Activation Request Schemas ====================

class ActivationRequest(BaseModel):
    """用户激活请求"""
    code: str = Field(..., min_length=1, max_length=32, description="激活码")


class ActivationResult(BaseModel):
    """激活结果"""
    success: bool
    message: str
    bank_id: Optional[str] = None
    bank_name: Optional[str] = None
    expire_at: Optional[datetime] = None  # None表示永久有效
    activated_at: datetime


# ==================== User Bank Access Schemas ====================

class UserBankAccessResponse(BaseModel):
    """用户题库访问权限响应"""
    id: str
    user_id: int
    bank_id: str
    bank_name: Optional[str] = None  # 可以从关联的bank获取
    bank_description: Optional[str] = None
    activated_by_code: Optional[str]
    activated_at: datetime
    expire_at: Optional[datetime]  # None表示永久有效
    is_active: bool
    is_expired: bool  # 根据expire_at动态计算

    class Config:
        from_attributes = True


class MyAccessListResponse(BaseModel):
    """我的访问权限列表"""
    access_list: List[UserBankAccessResponse]
    total: int
    active_count: int
    expired_count: int


# ==================== Activation Code Query Schemas ====================

class ActivationCodeQuery(BaseModel):
    """激活码查询参数"""
    bank_id: Optional[str] = Field(None, description="题库ID筛选")
    is_used: Optional[bool] = Field(None, description="是否已使用")
    expire_type: Optional[ExpireTypeEnum] = Field(None, description="过期类型")
    search: Optional[str] = Field(None, description="搜索（激活码/描述）")
    skip: int = Field(0, ge=0, description="跳过数量")
    limit: int = Field(20, ge=1, le=100, description="返回数量")


class ActivationCodeBatchGenerate(BaseModel):
    """批量生成激活码"""
    bank_ids: List[str] = Field(..., min_items=1, max_items=10, description="题库ID列表")
    expire_type: ExpireTypeEnum = Field(default=ExpireTypeEnum.permanent, description="过期类型")
    expire_days: Optional[int] = Field(None, ge=1, le=3650, description="有效天数")
    count_per_bank: int = Field(1, ge=1, le=50, description="每个题库生成数量")
    description: Optional[str] = Field(None, max_length=200, description="激活码描述")


class BatchGenerateResult(BaseModel):
    """批量生成结果"""
    total_generated: int
    codes_by_bank: Dict[str, List[str]]  # {bank_id: [code1, code2, ...]}
