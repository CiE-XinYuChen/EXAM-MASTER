"""
Fix questions with empty or invalid type values in the database
修复数据库中题目类型为空的问题
"""

from sqlalchemy import text
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionQBank

# Create session
session = SessionQBank()

def fix_empty_question_types():
    """Fix questions with empty type values"""

    # Find questions with empty or null type
    result = session.execute(
        text("SELECT id, stem, type FROM questions_v2 WHERE type = '' OR type IS NULL")
    )

    questions_with_empty_type = result.fetchall()

    if not questions_with_empty_type:
        print("✓ No questions with empty type found")
        return

    print(f"Found {len(questions_with_empty_type)} questions with empty type:")

    for question in questions_with_empty_type:
        question_id, stem, current_type = question
        print(f"\nQuestion ID: {question_id}")
        print(f"Stem: {stem[:100]}...")
        print(f"Current type: '{current_type}'")

        # For now, set them to 'single' as default
        # You could make this more intelligent based on the question content
        new_type = 'single'

        # Update the question
        session.execute(
            text("UPDATE questions_v2 SET type = :new_type WHERE id = :question_id"),
            {"new_type": new_type, "question_id": question_id}
        )
        print(f"→ Updated to: {new_type}")

    session.commit()
    print(f"\n✓ Updated {len(questions_with_empty_type)} questions")

def verify_question_types():
    """Verify all questions have valid types"""

    result = session.execute(
        text("SELECT type, COUNT(*) as count FROM questions_v2 GROUP BY type")
    )

    print("\nQuestion type distribution:")
    for row in result:
        type_value, count = row
        print(f"  {type_value}: {count}")

    # Check for any remaining invalid types
    result = session.execute(
        text("SELECT COUNT(*) FROM questions_v2 WHERE type NOT IN ('single', 'multiple', 'judge', 'fill', 'essay', 'composite')")
    )
    invalid_count = result.scalar()

    if invalid_count > 0:
        print(f"\n⚠ Warning: {invalid_count} questions still have invalid types")
    else:
        print("\n✓ All questions have valid types")

if __name__ == "__main__":
    print("=== Fixing Question Types ===\n")

    try:
        fix_empty_question_types()
        verify_question_types()
        print("\n=== Done ===")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        session.rollback()
    finally:
        session.close()
