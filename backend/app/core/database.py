"""
Database configuration and session management
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from .config import settings


# Main database for user management and system data
engine_main = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.debug
)

# Question bank database for questions and related data
engine_qbank = create_engine(
    settings.question_bank_database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.question_bank_database_url else {},
    echo=settings.debug
)

# Session factories
SessionMain = sessionmaker(autocommit=False, autoflush=False, bind=engine_main)
SessionQBank = sessionmaker(autocommit=False, autoflush=False, bind=engine_qbank)

# Base classes for models
BaseMain = declarative_base()
BaseQBank = declarative_base()


# Dependency injection functions
def get_main_db() -> Generator[Session, None, None]:
    """Get main database session"""
    db = SessionMain()
    try:
        yield db
    finally:
        db.close()


def get_qbank_db() -> Generator[Session, None, None]:
    """Get question bank database session"""
    db = SessionQBank()
    try:
        yield db
    finally:
        db.close()


def init_databases():
    """Initialize both databases"""
    # Import all models to ensure they are registered
    from app.models import user_models, question_models
    
    # Create all tables
    BaseMain.metadata.create_all(bind=engine_main)
    BaseQBank.metadata.create_all(bind=engine_qbank)
    
    print("Databases initialized successfully!")