"""
Fix enum values in database - Remove 'QuestionType.' prefix
修复数据库中的枚举值 - 移除 'QuestionType.' 前缀
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings

def fix_question_type_enum():
    """Fix question type enum values in database"""

    # Create engine
    engine = create_engine(settings.QBANK_DATABASE_URL)

    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()

        try:
            # Fix questions_v2 table
            print("Fixing questions_v2 table...")
            result = conn.execute(text("""
                UPDATE questions_v2
                SET type = REPLACE(type, 'QuestionType.', '')
                WHERE type LIKE 'QuestionType.%'
            """))
            print(f"  Updated {result.rowcount} rows in questions_v2")

            # Commit transaction
            trans.commit()
            print("✓ Successfully fixed enum values!")

        except Exception as e:
            # Rollback on error
            trans.rollback()
            print(f"✗ Error: {e}")
            raise

if __name__ == "__main__":
    print("=" * 60)
    print("Fix Enum Values Script")
    print("=" * 60)

    fix_question_type_enum()

    print("\nDone!")
