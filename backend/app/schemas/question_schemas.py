"""
Question bank related Pydantic schemas
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class QuestionType(str, Enum):
    SINGLE = "single"
    MULTIPLE = "multiple"
    JUDGE = "judge"
    FILL = "fill"
    ESSAY = "essay"


class ContentFormat(str, Enum):
    TEXT = "text"
    MARKDOWN = "markdown"
    LATEX = "latex"
    HTML = "html"


class ResourceType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"


# Question Bank Schemas
class QuestionBankBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: bool = False
    meta_data: Optional[Dict[str, Any]] = None


class QuestionBankCreate(QuestionBankBase):
    pass


class QuestionBankUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    meta_data: Optional[Dict[str, Any]] = None


class QuestionBankResponse(QuestionBankBase):
    id: str
    version: str
    creator_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    question_count: Optional[int] = 0
    total_questions: Optional[int] = 0
    
    model_config = ConfigDict(from_attributes=True)


# Question Option Schemas
class QuestionOptionBase(BaseModel):
    option_label: str = Field(..., max_length=10)
    option_content: str
    option_format: ContentFormat = ContentFormat.TEXT
    is_correct: bool = False
    sort_order: int = 0


class QuestionOptionCreate(QuestionOptionBase):
    pass


class QuestionOptionUpdate(BaseModel):
    option_content: Optional[str] = None
    option_format: Optional[ContentFormat] = None
    is_correct: Optional[bool] = None
    sort_order: Optional[int] = None


class QuestionOptionResponse(QuestionOptionBase):
    id: str
    created_at: datetime
    resources: List["ResourceResponse"] = []
    
    model_config = ConfigDict(from_attributes=True)


# Question Schemas
class QuestionBase(BaseModel):
    stem: str
    stem_format: ContentFormat = ContentFormat.TEXT
    type: QuestionType
    difficulty: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    explanation: Optional[str] = None
    explanation_format: ContentFormat = ContentFormat.TEXT
    meta_data: Optional[Dict[str, Any]] = None


class QuestionCreate(QuestionBase):
    bank_id: str
    options: List[QuestionOptionCreate] = []


class QuestionUpdate(BaseModel):
    stem: Optional[str] = None
    stem_format: Optional[ContentFormat] = None
    type: Optional[QuestionType] = None
    difficulty: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    explanation: Optional[str] = None
    explanation_format: Optional[ContentFormat] = None
    meta_data: Optional[Dict[str, Any]] = None


class QuestionResponse(QuestionBase):
    id: str
    bank_id: str
    question_number: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    options: List[QuestionOptionResponse] = []
    resources: List["ResourceResponse"] = []
    
    model_config = ConfigDict(from_attributes=True)


# Resource Schemas
class ResourceBase(BaseModel):
    resource_type: ResourceType
    file_name: str
    meta_data: Optional[Dict[str, Any]] = None


class ResourceCreate(ResourceBase):
    question_id: str
    option_id: Optional[str] = None


class ResourceResponse(ResourceBase):
    id: str
    file_path: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    created_at: datetime
    url: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# Import/Export Schemas
class ImportConfig(BaseModel):
    bank_id: str
    format: str = "auto_detect"
    merge_duplicates: bool = True
    auto_tag: bool = True
    extract_images: bool = True
    parse_latex: bool = True
    create_categories: bool = True
    mapping: Optional[Dict[str, str]] = None


class ImportResult(BaseModel):
    success: bool
    imported_count: int
    failed_count: int
    errors: List[str] = []
    warnings: List[str] = []


# Update forward references
QuestionOptionResponse.model_rebuild()
QuestionResponse.model_rebuild()