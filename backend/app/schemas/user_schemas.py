"""
User related Pydantic schemas
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.user_models import UserRole


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: UserRole = UserRole.student


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserInDB):
    pass


class UserWithPermissions(UserResponse):
    permissions: List["BankPermission"] = []


class BankPermission(BaseModel):
    bank_id: str
    permission: str
    granted_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Update forward references
UserWithPermissions.model_rebuild()