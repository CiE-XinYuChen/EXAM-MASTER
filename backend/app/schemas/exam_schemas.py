"""
Exam and Practice Session Schemas
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SessionStatus(str, Enum):
    """Session status enumeration"""
    pending = "pending"
    in_progress = "in_progress" 
    completed = "completed"
    expired = "expired"
    cancelled = "cancelled"


class SessionType(str, Enum):
    """Session type enumeration"""
    exam = "exam"
    practice = "practice"
    quiz = "quiz"


# Base Schemas
class SessionBase(BaseModel):
    """Base session schema"""
    title: str
    description: Optional[str] = None
    bank_id: str
    time_limit: Optional[int] = None  # in minutes
    question_count: Optional[int] = None
    shuffle_questions: bool = False
    shuffle_options: bool = False
    show_results: bool = True
    allow_review: bool = True


# Exam Session Schemas
class ExamSessionCreate(SessionBase):
    """Create exam session request"""
    session_type: SessionType = SessionType.exam
    passing_score: Optional[float] = None
    max_attempts: int = 1


class ExamSessionResponse(SessionBase):
    """Exam session response"""
    id: str
    creator_id: int
    status: SessionStatus
    session_type: SessionType
    passing_score: Optional[float] = None
    max_attempts: int
    current_attempt: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Practice Session Schemas
class PracticeSessionCreate(SessionBase):
    """Create practice session request"""
    session_type: SessionType = SessionType.practice
    difficulty_filter: Optional[List[str]] = None
    category_filter: Optional[List[str]] = None
    question_types: Optional[List[str]] = None


class PracticeSessionResponse(SessionBase):
    """Practice session response"""
    id: str
    creator_id: int
    status: SessionStatus
    session_type: SessionType
    difficulty_filter: Optional[List[str]] = None
    category_filter: Optional[List[str]] = None
    question_types: Optional[List[str]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Submission Schemas
class SubmissionCreate(BaseModel):
    """Create answer submission request"""
    session_id: str
    question_id: str
    answer: Dict[str, Any]  # Flexible answer format
    time_taken: Optional[int] = None  # in seconds
    is_final: bool = True


class SubmissionResponse(BaseModel):
    """Answer submission response"""
    id: str
    session_id: str
    question_id: str
    user_id: int
    answer: Dict[str, Any]
    is_correct: Optional[bool] = None
    score: Optional[float] = None
    time_taken: Optional[int] = None
    is_final: bool
    submitted_at: datetime
    
    class Config:
        from_attributes = True


# Session Results Schemas
class SessionResultResponse(BaseModel):
    """Session result response"""
    session_id: str
    user_id: int
    total_questions: int
    answered_questions: int
    correct_answers: int
    total_score: float
    percentage_score: float
    time_taken: Optional[int] = None  # in seconds
    passed: Optional[bool] = None
    completed_at: datetime
    
    class Config:
        from_attributes = True


class QuestionResultResponse(BaseModel):
    """Individual question result"""
    question_id: str
    user_answer: Dict[str, Any]
    correct_answer: Dict[str, Any]
    is_correct: bool
    score: float
    time_taken: Optional[int] = None
    
    class Config:
        from_attributes = True


class SessionDetailResponse(BaseModel):
    """Detailed session response with questions and results"""
    session: ExamSessionResponse | PracticeSessionResponse
    questions: List[Dict[str, Any]]
    results: Optional[SessionResultResponse] = None
    question_results: Optional[List[QuestionResultResponse]] = None
    
    class Config:
        from_attributes = True