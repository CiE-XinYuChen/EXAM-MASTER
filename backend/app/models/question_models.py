"""
Question bank related models (Question Bank Database)
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, JSON, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import BaseQBank


class QuestionBank(BaseQBank):
    __tablename__ = "question_banks"
    
    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    version = Column(String(20), default="1.0.0")
    category = Column(String(50))
    creator_id = Column(Integer)
    is_public = Column(Boolean, default=False)
    meta_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    questions = relationship("Question", back_populates="bank", cascade="all, delete-orphan")


class Question(BaseQBank):
    __tablename__ = "questions"
    
    id = Column(String(50), primary_key=True, index=True)
    bank_id = Column(String(50), ForeignKey("question_banks.id"), nullable=False)
    question_number = Column(Integer)
    stem = Column(Text, nullable=False)
    stem_format = Column(String(20), default="text")  # text, markdown, latex, html
    type = Column(String(20), nullable=False)  # single, multiple, judge, fill, essay
    difficulty = Column(String(20))  # easy, medium, hard
    category = Column(String(50))
    tags = Column(JSON)
    explanation = Column(Text)
    explanation_format = Column(String(20), default="text")
    meta_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bank = relationship("QuestionBank", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")
    resources = relationship("QuestionResource", back_populates="question", cascade="all, delete-orphan")
    versions = relationship("QuestionVersion", back_populates="question", cascade="all, delete-orphan")


class QuestionOption(BaseQBank):
    __tablename__ = "question_options"
    
    id = Column(String(50), primary_key=True, index=True)
    question_id = Column(String(50), ForeignKey("questions.id"), nullable=False)
    option_label = Column(String(10), nullable=False)  # A, B, C, D, E, F...
    option_content = Column(Text, nullable=False)
    option_format = Column(String(20), default="text")  # text, markdown, latex, html
    is_correct = Column(Boolean, default=False, nullable=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    question = relationship("Question", back_populates="options")
    resources = relationship("QuestionResource", back_populates="option")


class QuestionResource(BaseQBank):
    __tablename__ = "question_resources"
    
    id = Column(String(50), primary_key=True, index=True)
    question_id = Column(String(50), ForeignKey("questions.id"), nullable=False)
    option_id = Column(String(50), ForeignKey("question_options.id"), nullable=True)
    resource_type = Column(String(20), nullable=False)  # image, video, audio, document
    file_path = Column(String(255), nullable=False)
    file_name = Column(String(100), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(50))
    meta_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    question = relationship("Question", back_populates="resources")
    option = relationship("QuestionOption", back_populates="resources")


class QuestionVersion(BaseQBank):
    __tablename__ = "question_versions"
    
    id = Column(String(50), primary_key=True, index=True)
    question_id = Column(String(50), ForeignKey("questions.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    change_type = Column(String(20), nullable=False)  # create, update, delete
    change_data = Column(JSON, nullable=False)
    changed_by = Column(Integer)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    question = relationship("Question", back_populates="versions")