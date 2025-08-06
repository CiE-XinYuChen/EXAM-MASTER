#!/usr/bin/env python3
"""
Simple test to verify the application structure
"""

print("Testing FastAPI Backend Structure...")
print("=" * 50)

# Test imports
try:
    print("✓ Testing core imports...")
    from app.core.config import settings
    from app.core.database import get_main_db, get_qbank_db
    print("  - Core modules: OK")
except Exception as e:
    print(f"  - Core modules: FAILED - {e}")

try:
    print("✓ Testing model imports...")
    from app.models.user_models import User, UserBankPermission
    from app.models.question_models import Question, QuestionBank
    print("  - Model modules: OK")
except Exception as e:
    print(f"  - Model modules: FAILED - {e}")

try:
    print("✓ Testing API route imports...")
    from app.api.v1.qbank import banks, questions, options, resources, imports
    print("  - API modules: OK")
except Exception as e:
    print(f"  - API modules: FAILED - {e}")

print("\n" + "=" * 50)
print("Backend structure test completed!")
print("\nProject Summary:")
print("- FastAPI framework configured")
print("- Dual database architecture (Main + Question Bank)")
print("- JWT authentication system")
print("- User management with role-based access")
print("- Question bank CRUD operations")
print("- Dynamic option system (unlimited options)")
print("- File upload and resource management")
print("- Import/Export (CSV, JSON)")
print("\nTo run the server:")
print("  1. Install dependencies: pip install -r requirements.txt")
print("  2. Run server: python run.py")
print("  3. Access API docs: http://localhost:8000/docs")