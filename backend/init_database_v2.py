"""
初始化数据库 V2 - 创建新的表结构
"""

import os
from sqlalchemy import create_engine
from app.core.database import BaseQBank
from app.models.question_models_v2 import (
    QuestionBankV2, QuestionV2, QuestionOptionV2,
    QuestionResourceV2, QuestionBankResource, QuestionBankExport
)

def init_database_v2():
    """初始化V2数据库"""
    
    # 确保databases目录存在
    os.makedirs("databases", exist_ok=True)
    
    # 创建数据库引擎
    engine = create_engine(
        "sqlite:///./databases/question_bank_v2.db",
        connect_args={"check_same_thread": False}
    )
    
    # 创建所有表
    print("Creating V2 tables...")
    BaseQBank.metadata.create_all(bind=engine)
    
    print("Database V2 initialized successfully!")
    print("Tables created:")
    print("  - question_banks_v2")
    print("  - questions_v2")
    print("  - question_options_v2")
    print("  - question_resources")
    print("  - question_bank_resources")
    print("  - question_bank_exports")
    
    # 创建存储目录结构
    storage_dirs = [
        "storage/question_banks",
        "storage/resources",
        "storage/uploads/temp",
        "storage/backups/deleted"
    ]
    
    for dir_path in storage_dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    print("\nStorage directories created:")
    for dir_path in storage_dirs:
        print(f"  - {dir_path}")
    
    return engine

if __name__ == "__main__":
    init_database_v2()