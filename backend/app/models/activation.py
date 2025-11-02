"""
Activation Code Models
激活码模型
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import enum
from app.core.database import Base, BaseQBank


class ExpireType(str, enum.Enum):
    """激活码过期类型"""
    permanent = "permanent"     # 永久
    temporary = "temporary"     # 临时（有有效期）


class ActivationCode(BaseQBank):
    """激活码表"""
    __tablename__ = "activation_codes"

    # 基本信息
    id = Column(String(36), primary_key=True, index=True)
    code = Column(String(32), unique=True, nullable=False, index=True)  # 激活码
    bank_id = Column(String(36), ForeignKey("question_banks_v2.id"), nullable=False, index=True)

    # 创建信息
    created_by = Column(Integer, nullable=False)  # 创建者（引用主库users.id，无外键约束）
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 过期策略
    expire_type = Column(SQLEnum(ExpireType), default=ExpireType.permanent, nullable=False)
    expire_days = Column(Integer)  # 如果是临时激活码，指定天数

    # 使用信息
    is_used = Column(Boolean, default=False, index=True)
    used_by = Column(Integer)  # 使用者（引用主库users.id，无外键约束）
    used_at = Column(DateTime)

    # 备注
    description = Column(String(200))  # 激活码描述（方便管理）

    # 关系（只有bank的关系，user关系因跨数据库无法建立）
    bank = relationship("QuestionBankV2", backref="activation_codes")


class UserBankAccess(BaseQBank):
    """用户题库访问权限表"""
    __tablename__ = "user_bank_access"

    # 基本信息
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # 引用主库users.id（无外键约束）
    bank_id = Column(String(36), ForeignKey("question_banks_v2.id"), nullable=False, index=True)

    # 激活信息
    activated_by_code = Column(String(36), ForeignKey("activation_codes.id"))
    activated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 过期信息
    expire_at = Column(DateTime)  # 如果为None则永久有效
    is_active = Column(Boolean, default=True, index=True)

    # 关系（user关系因跨数据库无法建立）
    bank = relationship("QuestionBankV2", backref="user_access")
    activation_code = relationship("ActivationCode", backref="access_records")

    # 联合唯一索引（一个用户对一个题库只能有一条访问记录）
    __table_args__ = (
        {'extend_existing': True},
    )

    def is_expired(self):
        """检查是否过期"""
        if not self.expire_at:
            return False
        return datetime.utcnow() > self.expire_at
