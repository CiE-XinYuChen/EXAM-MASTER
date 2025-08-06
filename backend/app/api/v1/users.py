"""
User management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_main_db
from app.core.security import get_current_user, get_current_admin_user
from app.models.user_models import User, UserBankPermission
from app.schemas.user_schemas import UserResponse, UserUpdate, UserWithPermissions, BankPermission

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_main_db)
):
    """Get list of users (admin only)"""
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserWithPermissions)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_main_db)
):
    """Get user by ID (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_main_db)
):
    """Update user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields if provided
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", response_model=dict)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_main_db)
):
    """Delete user (admin only)"""
    # Prevent self-deletion
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


@router.get("/{user_id}/permissions", response_model=List[BankPermission])
async def get_user_permissions(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_main_db)
):
    """Get user's question bank permissions"""
    # Users can view their own permissions, admins can view anyone's
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these permissions"
        )
    
    permissions = db.query(UserBankPermission).filter(
        UserBankPermission.user_id == user_id
    ).all()
    
    return permissions


@router.post("/{user_id}/permissions", response_model=BankPermission, status_code=status.HTTP_201_CREATED)
async def grant_permission(
    user_id: int,
    bank_id: str,
    permission: str = Query(..., regex="^(read|write|admin)$"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_main_db)
):
    """Grant question bank permission to user (admin only)"""
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if permission already exists
    existing = db.query(UserBankPermission).filter(
        UserBankPermission.user_id == user_id,
        UserBankPermission.bank_id == bank_id
    ).first()
    
    if existing:
        # Update existing permission
        existing.permission = permission
        existing.granted_by = current_user.id
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new permission
    new_permission = UserBankPermission(
        user_id=user_id,
        bank_id=bank_id,
        permission=permission,
        granted_by=current_user.id
    )
    
    db.add(new_permission)
    db.commit()
    db.refresh(new_permission)
    
    return new_permission


@router.delete("/{user_id}/permissions/{bank_id}", response_model=dict)
async def revoke_permission(
    user_id: int,
    bank_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_main_db)
):
    """Revoke question bank permission from user (admin only)"""
    permission = db.query(UserBankPermission).filter(
        UserBankPermission.user_id == user_id,
        UserBankPermission.bank_id == bank_id
    ).first()
    
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    db.delete(permission)
    db.commit()
    
    return {"message": "Permission revoked successfully"}