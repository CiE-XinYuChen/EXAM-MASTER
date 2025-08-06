"""
User and authentication related models (Main Database)
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, JSON, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import BaseMain


class UserRole(str, enum.Enum):
    admin = "admin"
    teacher = "teacher"
    student = "student"


class User(BaseMain):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.student, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    permissions = relationship("UserBankPermission", foreign_keys="UserBankPermission.user_id", back_populates="user", cascade="all, delete-orphan")
    answer_history = relationship("AnswerHistory", back_populates="user", cascade="all, delete-orphan")
    exam_sessions = relationship("ExamSession", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")


class UserBankPermission(BaseMain):
    __tablename__ = "user_bank_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bank_id = Column(String(50), nullable=False, index=True)
    permission = Column(String(20), nullable=False)  # read, write, admin
    granted_by = Column(Integer, ForeignKey("users.id"))
    granted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="permissions")
    granter = relationship("User", foreign_keys=[granted_by])


class AnswerHistory(BaseMain):
    __tablename__ = "answer_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(String(50), nullable=False, index=True)
    bank_id = Column(String(50), nullable=False, index=True)
    answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_spent = Column(Integer)  # in seconds
    answered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="answer_history")


class ExamSession(BaseMain):
    __tablename__ = "exam_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bank_id = Column(String(50), nullable=False)
    mode = Column(String(20), nullable=False)  # practice, exam, timed
    question_ids = Column(JSON, nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime)
    duration = Column(Integer)  # in seconds
    score = Column(Float)
    status = Column(String(20), default="in_progress")  # in_progress, completed, abandoned
    
    # Relationships
    user = relationship("User", back_populates="exam_sessions")


class Favorite(BaseMain):
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(String(50), nullable=False, index=True)
    bank_id = Column(String(50), nullable=False, index=True)
    tags = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="favorites")