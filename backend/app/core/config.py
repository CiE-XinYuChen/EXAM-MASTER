"""
Configuration management using Pydantic Settings
"""

from typing import List, Optional
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Application
    app_name: str = Field(default="EXAM-MASTER", env="APP_NAME")
    app_version: str = Field(default="2.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    
    # Database
    database_url: str = Field(
        default="sqlite:///./databases/main.db", 
        env="DATABASE_URL"
    )
    question_bank_database_url: str = Field(
        default="sqlite:///./databases/question_bank.db",
        env="QUESTION_BANK_DATABASE_URL"
    )
    
    # File Storage
    upload_dir: Path = Field(
        default=Path("./storage/uploads"), 
        env="UPLOAD_DIR"
    )
    resource_dir: Path = Field(
        default=Path("./storage/resources"),
        env="RESOURCE_DIR"
    )
    question_bank_dir: Path = Field(
        default=Path("./storage/question_banks"),
        env="QUESTION_BANK_DIR"
    )
    max_upload_size: int = Field(
        default=52428800,  # 50MB
        env="MAX_UPLOAD_SIZE"
    )
    
    # Redis (optional)
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="CORS_ORIGINS"
    )
    
    # API
    api_v1_prefix: str = Field(default="/api/v1", env="API_V1_PREFIX")
    docs_url: str = Field(default="/docs", env="DOCS_URL")
    redoc_url: str = Field(default="/redoc", env="REDOC_URL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.resource_dir.mkdir(parents=True, exist_ok=True)
        self.question_bank_dir.mkdir(parents=True, exist_ok=True)
        # Create databases directory
        Path("./databases").mkdir(parents=True, exist_ok=True)


settings = Settings()