"""
Pydantic Schemas for Question Bank V2
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class QuestionTypeEnum(str, Enum):
    single = "single"
    multiple = "multiple"
    judge = "judge"
    fill = "fill"
    essay = "essay"
    composite = "composite"


class DifficultyEnum(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"
    expert = "expert"


# ==================== Question Bank Schemas ====================

class QuestionBankBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = []
    version: Optional[str] = "1.0.0"


class QuestionBankCreate(QuestionBankBase):
    is_public: bool = False
    allow_download: bool = True
    allow_fork: bool = True


class QuestionBankUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    version: Optional[str] = None
    is_public: Optional[bool] = None
    is_published: Optional[bool] = None
    allow_download: Optional[bool] = None
    allow_fork: Optional[bool] = None


class QuestionBankResponse(QuestionBankBase):
    id: str
    folder_path: str
    storage_type: str
    total_questions: int
    total_size_mb: float
    has_images: bool
    has_audio: bool
    has_video: bool
    creator_id: int
    is_public: bool
    is_published: bool
    allow_download: bool
    allow_fork: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        orm_mode = True


# ==================== Question Schemas ====================

class OptionData(BaseModel):
    label: str
    content: str
    is_correct: bool = False
    explanation: Optional[str] = None


class QuestionBase(BaseModel):
    stem: str = Field(..., min_length=1)
    stem_format: str = "text"
    type: QuestionTypeEnum
    difficulty: DifficultyEnum = DifficultyEnum.medium
    score: float = 1.0
    category: Optional[str] = None
    sub_category: Optional[str] = None
    tags: Optional[List[str]] = []
    explanation: Optional[str] = None
    explanation_format: str = "text"
    hint: Optional[str] = None
    source: Optional[str] = None


class QuestionCreate(QuestionBase):
    question_number: Optional[int] = None
    options: Optional[List[OptionData]] = []
    meta_data: Optional[Dict[str, Any]] = {}
    estimated_time: Optional[int] = None
    knowledge_points: Optional[List[str]] = []


class QuestionUpdate(BaseModel):
    stem: Optional[str] = None
    stem_format: Optional[str] = None
    type: Optional[QuestionTypeEnum] = None
    difficulty: Optional[DifficultyEnum] = None
    score: Optional[float] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    tags: Optional[List[str]] = None
    explanation: Optional[str] = None
    explanation_format: Optional[str] = None
    hint: Optional[str] = None
    source: Optional[str] = None
    question_number: Optional[int] = None
    options: Optional[List[OptionData]] = None
    meta_data: Optional[Dict[str, Any]] = None


class QuestionResponse(QuestionBase):
    id: str
    bank_id: str
    question_number: Optional[int]
    question_code: Optional[str]
    has_images: bool
    has_audio: bool
    has_video: bool
    has_formula: bool
    usage_count: int
    error_count: int
    avg_score: Optional[float]
    avg_time: Optional[float]
    meta_data: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    options: Optional[List[OptionData]] = []
    
    class Config:
        orm_mode = True


# ==================== Import/Export Schemas ====================

class QuestionImportRequest(BaseModel):
    bank_id: str
    questions: List[Dict[str, Any]]
    merge_duplicates: bool = False


class QuestionExportRequest(BaseModel):
    bank_id: str
    format: str = "json"  # json, csv, zip
    include_images: bool = True
    include_audio: bool = True
    include_answers: bool = True
    include_explanations: bool = True
    question_ids: Optional[List[str]] = None  # 如果为空，导出所有题目


class ImportResult(BaseModel):
    success: bool
    bank_id: str
    bank_name: str
    imported_count: int
    skipped_count: int = 0
    error_count: int = 0
    errors: List[str] = []


# ==================== Resource Schemas ====================

class ResourceUpload(BaseModel):
    question_id: str
    position: str = "stem"  # stem, option_a, option_b, explanation, etc
    alt_text: Optional[str] = None
    caption: Optional[str] = None


class ResourceResponse(BaseModel):
    id: str
    question_id: str
    resource_type: str
    resource_path: str
    resource_url: Optional[str]
    file_name: Optional[str]
    file_size: Optional[int]
    mime_type: Optional[str]
    position: Optional[str]
    alt_text: Optional[str]
    caption: Optional[str]
    created_at: datetime
    
    class Config:
        orm_mode = True


# ==================== Statistics Schemas ====================

class BankStatistics(BaseModel):
    bank_id: str
    bank_name: str
    total_questions: int
    total_size_mb: float
    has_images: bool
    has_audio: bool
    has_video: bool
    type_distribution: Dict[str, int]
    difficulty_distribution: Dict[str, int]
    created_at: datetime
    updated_at: Optional[datetime]


class QuestionStatistics(BaseModel):
    question_id: str
    usage_count: int
    error_count: int
    avg_score: Optional[float]
    avg_time: Optional[float]
    difficulty_analysis: Optional[Dict[str, Any]]


# ==================== Search Schemas ====================

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2)
    bank_id: Optional[str] = None
    type: Optional[QuestionTypeEnum] = None
    difficulty: Optional[DifficultyEnum] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    skip: int = 0
    limit: int = 20


class SearchResponse(BaseModel):
    total: int
    questions: List[QuestionResponse]
    facets: Optional[Dict[str, Dict[str, int]]] = None  # 分面搜索结果