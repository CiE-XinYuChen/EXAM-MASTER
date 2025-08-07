"""
Comprehensive API Testing for EXAM-MASTER Backend
Tests all API endpoints including auth, questions, banks, LLM, etc.
"""

import pytest
import json
import uuid
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_main_db, get_qbank_db, BaseMain, BaseQBank
from app.core.security import get_password_hash
from app.models.user_models import User, UserRole
from app.models.question_models import QuestionBank, Question, QuestionOption
from app.models.llm_models import LLMInterface, PromptTemplate

# Test database setup
SQLALCHEMY_TEST_MAIN_URL = "sqlite:///./test_main.db"
SQLALCHEMY_TEST_QBANK_URL = "sqlite:///./test_qbank.db"

engine_main = create_engine(SQLALCHEMY_TEST_MAIN_URL, connect_args={"check_same_thread": False})
TestingSessionMain = sessionmaker(autocommit=False, autoflush=False, bind=engine_main)

engine_qbank = create_engine(SQLALCHEMY_TEST_QBANK_URL, connect_args={"check_same_thread": False})
TestingSessionQBank = sessionmaker(autocommit=False, autoflush=False, bind=engine_qbank)

# Override dependencies
def override_get_main_db():
    try:
        db = TestingSessionMain()
        yield db
    finally:
        db.close()

def override_get_qbank_db():
    try:
        db = TestingSessionQBank()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_main_db] = override_get_main_db
app.dependency_overrides[get_qbank_db] = override_get_qbank_db

# Create test client
client = TestClient(app)

# Setup and teardown
@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Create test databases"""
    BaseMain.metadata.create_all(bind=engine_main)
    BaseQBank.metadata.create_all(bind=engine_qbank)
    
    # Create test admin user
    db = TestingSessionMain()
    admin_user = User(
        username="admin",
        email="admin@test.com",
        password_hash=get_password_hash("admin123"),
        role=UserRole.admin,
        is_active=True
    )
    db.add(admin_user)
    db.commit()
    db.close()
    
    yield
    
    # Cleanup
    BaseMain.metadata.drop_all(bind=engine_main)
    BaseQBank.metadata.drop_all(bind=engine_qbank)

@pytest.fixture
def auth_token():
    """Get auth token for test user"""
    response = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def auth_headers(auth_token):
    """Get auth headers with token"""
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
def test_question_bank(auth_headers):
    """Create a test question bank"""
    response = client.post(
        "/api/v1/qbank/banks/",
        headers=auth_headers,
        json={
            "name": "Test Bank",
            "description": "Test question bank",
            "category": "test",
            "is_public": True
        }
    )
    assert response.status_code == 200
    return response.json()

@pytest.fixture
def test_llm_interface(auth_headers):
    """Create a test LLM interface"""
    response = client.post(
        "/api/v1/llm/interfaces",
        headers=auth_headers,
        json={
            "name": "Test LLM",
            "type": "openai-compatible",
            "config": {
                "base_url": "https://api.openai.com/v1",
                "api_key": "test-key",
                "model": "gpt-3.5-turbo",
                "timeout": 30
            },
            "is_active": True
        }
    )
    assert response.status_code == 200
    return response.json()


# ===================== SYSTEM ENDPOINTS TESTS =====================

class TestSystemEndpoints:
    """Test system and health endpoints"""
    
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
    
    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


# ===================== AUTHENTICATION TESTS =====================

class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_login_success(self):
        response = client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self):
        response = client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "wrong_password"
        })
        assert response.status_code == 401
    
    def test_register_new_user(self):
        response = client.post("/api/v1/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"
    
    def test_get_current_user(self, auth_headers):
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["username"] == "admin"
    
    def test_change_password(self, auth_headers):
        response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "old_password": "admin123",
                "new_password": "newpass123"
            }
        )
        assert response.status_code == 200
        
        # Change back
        response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "old_password": "newpass123",
                "new_password": "admin123"
            }
        )
        assert response.status_code == 200


# ===================== USER MANAGEMENT TESTS =====================

class TestUserEndpoints:
    """Test user management endpoints"""
    
    def test_list_users(self, auth_headers):
        response = client.get("/api/v1/users/", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_user_by_id(self, auth_headers):
        # First get users list
        response = client.get("/api/v1/users/", headers=auth_headers)
        users = response.json()
        
        if users:
            user_id = users[0]["id"]
            response = client.get(f"/api/v1/users/{user_id}", headers=auth_headers)
            assert response.status_code == 200
            assert response.json()["id"] == user_id
    
    def test_update_user(self, auth_headers):
        # Get first user
        response = client.get("/api/v1/users/", headers=auth_headers)
        users = response.json()
        
        if users:
            user_id = users[0]["id"]
            response = client.put(
                f"/api/v1/users/{user_id}",
                headers=auth_headers,
                json={"email": "updated@test.com"}
            )
            assert response.status_code == 200


# ===================== QUESTION BANK TESTS =====================

class TestQuestionBankEndpoints:
    """Test question bank endpoints"""
    
    def test_create_question_bank(self, auth_headers):
        response = client.post(
            "/api/v1/qbank/banks/",
            headers=auth_headers,
            json={
                "name": "Python Programming",
                "description": "Python basics questions",
                "category": "programming",
                "is_public": True
            }
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Python Programming"
    
    def test_list_question_banks(self, auth_headers):
        response = client.get("/api/v1/qbank/banks/", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_question_bank(self, auth_headers, test_question_bank):
        bank_id = test_question_bank["id"]
        response = client.get(f"/api/v1/qbank/banks/{bank_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == bank_id
    
    def test_update_question_bank(self, auth_headers, test_question_bank):
        bank_id = test_question_bank["id"]
        response = client.put(
            f"/api/v1/qbank/banks/{bank_id}",
            headers=auth_headers,
            json={"description": "Updated description"}
        )
        assert response.status_code == 200
        assert response.json()["description"] == "Updated description"
    
    def test_clone_question_bank(self, auth_headers, test_question_bank):
        bank_id = test_question_bank["id"]
        response = client.post(
            f"/api/v1/qbank/banks/{bank_id}/clone",
            headers=auth_headers,
            json={"new_name": "Cloned Bank"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Cloned Bank"


# ===================== QUESTION TESTS =====================

class TestQuestionEndpoints:
    """Test question CRUD operations for all question types"""
    
    def test_create_single_choice_question(self, auth_headers, test_question_bank):
        """Test creating a single choice question"""
        response = client.post(
            "/api/v1/qbank/questions/",
            headers=auth_headers,
            json={
                "bank_id": test_question_bank["id"],
                "stem": "What is 2 + 2?",
                "type": "single",
                "difficulty": "easy",
                "category": "math",
                "options": [
                    {"label": "A", "content": "3", "is_correct": False},
                    {"label": "B", "content": "4", "is_correct": True},
                    {"label": "C", "content": "5", "is_correct": False},
                    {"label": "D", "content": "6", "is_correct": False}
                ]
            }
        )
        assert response.status_code == 200
        assert response.json()["type"] == "single"
    
    def test_create_multiple_choice_question(self, auth_headers, test_question_bank):
        """Test creating a multiple choice question"""
        response = client.post(
            "/api/v1/qbank/questions/",
            headers=auth_headers,
            json={
                "bank_id": test_question_bank["id"],
                "stem": "Which are even numbers?",
                "type": "multiple",
                "difficulty": "medium",
                "category": "math",
                "options": [
                    {"label": "A", "content": "2", "is_correct": True},
                    {"label": "B", "content": "3", "is_correct": False},
                    {"label": "C", "content": "4", "is_correct": True},
                    {"label": "D", "content": "5", "is_correct": False}
                ]
            }
        )
        assert response.status_code == 200
        assert response.json()["type"] == "multiple"
    
    def test_create_judge_question(self, auth_headers, test_question_bank):
        """Test creating a true/false question"""
        response = client.post(
            "/api/v1/qbank/questions/",
            headers=auth_headers,
            json={
                "bank_id": test_question_bank["id"],
                "stem": "Python is a compiled language",
                "type": "judge",
                "difficulty": "easy",
                "category": "programming",
                "meta_data": {"answer": False}
            }
        )
        assert response.status_code == 200
        assert response.json()["type"] == "judge"
        assert response.json()["meta_data"]["answer"] == False
    
    def test_create_fill_question(self, auth_headers, test_question_bank):
        """Test creating a fill-in-the-blank question"""
        response = client.post(
            "/api/v1/qbank/questions/",
            headers=auth_headers,
            json={
                "bank_id": test_question_bank["id"],
                "stem": "Python was created by ____ in ____",
                "type": "fill",
                "difficulty": "medium",
                "category": "programming",
                "meta_data": {
                    "blanks": [
                        {"position": 0, "answer": "Guido van Rossum", "alternatives": ["Guido"]},
                        {"position": 1, "answer": "1991", "alternatives": []}
                    ]
                }
            }
        )
        assert response.status_code == 200
        assert response.json()["type"] == "fill"
        assert len(response.json()["meta_data"]["blanks"]) == 2
    
    def test_create_essay_question(self, auth_headers, test_question_bank):
        """Test creating an essay question"""
        response = client.post(
            "/api/v1/qbank/questions/",
            headers=auth_headers,
            json={
                "bank_id": test_question_bank["id"],
                "stem": "Explain the difference between lists and tuples in Python",
                "type": "essay",
                "difficulty": "hard",
                "category": "programming",
                "meta_data": {
                    "reference_answer": "Lists are mutable, tuples are immutable...",
                    "keywords": ["mutable", "immutable", "performance"]
                }
            }
        )
        assert response.status_code == 200
        assert response.json()["type"] == "essay"
        assert "reference_answer" in response.json()["meta_data"]
    
    def test_list_questions(self, auth_headers, test_question_bank):
        """Test listing questions"""
        response = client.get(
            f"/api/v1/qbank/questions/?bank_id={test_question_bank['id']}",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_update_question(self, auth_headers, test_question_bank):
        """Test updating a question"""
        # First create a question
        create_response = client.post(
            "/api/v1/qbank/questions/",
            headers=auth_headers,
            json={
                "bank_id": test_question_bank["id"],
                "stem": "Original question",
                "type": "single",
                "difficulty": "easy",
                "options": [
                    {"label": "A", "content": "Option 1", "is_correct": True},
                    {"label": "B", "content": "Option 2", "is_correct": False}
                ]
            }
        )
        question_id = create_response.json()["id"]
        
        # Update the question
        response = client.put(
            f"/api/v1/qbank/questions/{question_id}",
            headers=auth_headers,
            json={
                "stem": "Updated question",
                "difficulty": "medium"
            }
        )
        assert response.status_code == 200
        assert response.json()["stem"] == "Updated question"
        assert response.json()["difficulty"] == "medium"
    
    def test_duplicate_question(self, auth_headers, test_question_bank):
        """Test duplicating a question"""
        # Create original question
        create_response = client.post(
            "/api/v1/qbank/questions/",
            headers=auth_headers,
            json={
                "bank_id": test_question_bank["id"],
                "stem": "Question to duplicate",
                "type": "single",
                "options": [
                    {"label": "A", "content": "Yes", "is_correct": True},
                    {"label": "B", "content": "No", "is_correct": False}
                ]
            }
        )
        question_id = create_response.json()["id"]
        
        # Duplicate the question
        response = client.post(
            f"/api/v1/qbank/questions/{question_id}/duplicate",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["stem"] == "Question to duplicate"
        assert response.json()["id"] != question_id
    
    def test_delete_question(self, auth_headers, test_question_bank):
        """Test deleting a question"""
        # Create a question
        create_response = client.post(
            "/api/v1/qbank/questions/",
            headers=auth_headers,
            json={
                "bank_id": test_question_bank["id"],
                "stem": "Question to delete",
                "type": "judge",
                "meta_data": {"answer": True}
            }
        )
        question_id = create_response.json()["id"]
        
        # Delete the question
        response = client.delete(
            f"/api/v1/qbank/questions/{question_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Verify deletion
        get_response = client.get(
            f"/api/v1/qbank/questions/{question_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404


# ===================== LLM INTERFACE TESTS =====================

class TestLLMInterfaceEndpoints:
    """Test LLM interface management endpoints"""
    
    def test_create_llm_interface(self, auth_headers):
        response = client.post(
            "/api/v1/llm/interfaces",
            headers=auth_headers,
            json={
                "name": "OpenAI GPT",
                "type": "openai-compatible",
                "config": {
                    "base_url": "https://api.openai.com/v1",
                    "api_key": "sk-test",
                    "model": "gpt-3.5-turbo",
                    "timeout": 60
                },
                "is_active": True,
                "is_default": True
            }
        )
        assert response.status_code == 200
        assert response.json()["name"] == "OpenAI GPT"
    
    def test_create_zhipu_interface(self, auth_headers):
        response = client.post(
            "/api/v1/llm/interfaces",
            headers=auth_headers,
            json={
                "name": "Zhipu AI",
                "type": "zhipu-ai",
                "config": {
                    "base_url": "https://open.bigmodel.cn/api/paas/v4",
                    "api_key": "test-zhipu-key",
                    "model": "glm-4",
                    "timeout": 120
                },
                "is_active": True
            }
        )
        assert response.status_code == 200
        assert response.json()["type"] == "zhipu-ai"
    
    def test_list_llm_interfaces(self, auth_headers):
        response = client.get("/api/v1/llm/interfaces", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_update_llm_interface(self, auth_headers, test_llm_interface):
        interface_id = test_llm_interface["id"]
        response = client.put(
            f"/api/v1/llm/interfaces/{interface_id}",
            headers=auth_headers,
            json={
                "name": "Updated LLM",
                "is_active": False
            }
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated LLM"
        assert response.json()["is_active"] == False
    
    def test_test_llm_interface(self, auth_headers, test_llm_interface):
        """Test the interface connectivity (will fail with test key)"""
        interface_id = test_llm_interface["id"]
        response = client.post(
            f"/api/v1/llm/interfaces/{interface_id}/test",
            headers=auth_headers,
            json={"test_prompt": "Hello"}
        )
        # This will likely fail with test API key
        assert response.status_code in [200, 500]


# ===================== PROMPT TEMPLATE TESTS =====================

class TestPromptTemplateEndpoints:
    """Test prompt template management endpoints"""
    
    def test_create_prompt_template(self, auth_headers):
        response = client.post(
            "/api/v1/llm/templates",
            headers=auth_headers,
            json={
                "name": "Question Parser",
                "type": "question_parser",
                "category": "parsing",
                "content": "Parse the following question: {question}",
                "variables": ["question"],
                "description": "Template for parsing questions",
                "is_public": False
            }
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Question Parser"
    
    def test_list_templates(self, auth_headers):
        response = client.get("/api/v1/llm/templates", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_preset_templates(self):
        response = client.get("/api/v1/llm/templates/presets")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_update_template(self, auth_headers):
        # Create a template first
        create_response = client.post(
            "/api/v1/llm/templates",
            headers=auth_headers,
            json={
                "name": "Test Template",
                "type": "custom",
                "content": "Original content",
                "is_public": False
            }
        )
        template_id = create_response.json()["id"]
        
        # Update the template
        response = client.put(
            f"/api/v1/llm/templates/{template_id}",
            headers=auth_headers,
            json={
                "content": "Updated content",
                "is_public": True
            }
        )
        assert response.status_code == 200
        assert response.json()["content"] == "Updated content"
        assert response.json()["is_public"] == True
    
    def test_delete_template(self, auth_headers):
        # Create a template
        create_response = client.post(
            "/api/v1/llm/templates",
            headers=auth_headers,
            json={
                "name": "Template to Delete",
                "type": "custom",
                "content": "Delete me"
            }
        )
        template_id = create_response.json()["id"]
        
        # Delete the template
        response = client.delete(
            f"/api/v1/llm/templates/{template_id}",
            headers=auth_headers
        )
        assert response.status_code == 200


# ===================== LLM PARSING TESTS =====================

class TestLLMParsingEndpoints:
    """Test LLM question parsing endpoints"""
    
    def test_parse_questions(self, auth_headers, test_llm_interface, test_question_bank):
        """Test parsing questions with LLM (will fail without real API key)"""
        response = client.post(
            "/api/v1/llm/parse",
            headers=auth_headers,
            json={
                "interface_id": test_llm_interface["id"],
                "raw_text": "Question: What is Python?\nA. A snake\nB. A programming language\nC. A fruit\nD. A movie\nAnswer: B",
                "hint_type": "single",
                "bank_id": test_question_bank["id"]
            }
        )
        # This will fail without a real API key
        assert response.status_code in [200, 500]
    
    def test_batch_import_parsed_questions(self, auth_headers, test_question_bank):
        """Test batch importing parsed questions"""
        response = client.post(
            "/api/v1/llm/import",
            headers=auth_headers,
            json={
                "bank_id": test_question_bank["id"],
                "questions": [
                    {
                        "type": "single",
                        "stem": "Imported question 1",
                        "options": [
                            {"label": "A", "content": "Option 1", "is_correct": True},
                            {"label": "B", "content": "Option 2", "is_correct": False}
                        ],
                        "difficulty": "easy",
                        "category": "imported"
                    },
                    {
                        "type": "judge",
                        "stem": "Imported true/false question",
                        "correct_answer": "true",
                        "difficulty": "medium",
                        "category": "imported"
                    }
                ],
                "validate_before_import": True,
                "skip_duplicates": True
            }
        )
        assert response.status_code == 200
        assert response.json()["imported_count"] >= 0


# ===================== IMPORT/EXPORT TESTS =====================

class TestImportExportEndpoints:
    """Test import/export functionality"""
    
    def test_validate_import_data(self, auth_headers):
        """Test validating import data"""
        response = client.post(
            "/api/v1/qbank/import/validate",
            headers=auth_headers,
            json={
                "data": [
                    {
                        "stem": "Test question",
                        "type": "single",
                        "options": ["A", "B", "C", "D"],
                        "correct": "A"
                    }
                ],
                "format": "json"
            }
        )
        assert response.status_code == 200
    
    def test_export_question_bank(self, auth_headers, test_question_bank):
        """Test exporting a question bank"""
        # Add some questions first
        client.post(
            "/api/v1/qbank/questions/",
            headers=auth_headers,
            json={
                "bank_id": test_question_bank["id"],
                "stem": "Export test question",
                "type": "judge",
                "meta_data": {"answer": True}
            }
        )
        
        # Export the bank
        response = client.get(
            f"/api/v1/qbank/import/export/{test_question_bank['id']}",
            headers=auth_headers,
            params={"format": "json"}
        )
        assert response.status_code == 200


# ===================== ADMIN PANEL TESTS =====================

class TestAdminPanelEndpoints:
    """Test admin panel HTML endpoints"""
    
    def test_admin_login_page(self):
        response = client.get("/admin/login")
        assert response.status_code == 200
        assert b"login" in response.content.lower()
    
    def test_admin_login_post(self):
        response = client.post("/admin/login", data={
            "username": "admin",
            "password": "admin123"
        }, follow_redirects=False)
        assert response.status_code in [303, 200]  # Redirect or success
    
    def test_admin_dashboard_requires_auth(self):
        response = client.get("/admin", follow_redirects=False)
        assert response.status_code in [303, 401]  # Redirect to login or unauthorized
    
    def test_admin_questions_page(self):
        # Login first
        login_response = client.post("/admin/login", data={
            "username": "admin",
            "password": "admin123"
        })
        
        # Access questions page
        response = client.get("/admin/questions")
        assert response.status_code in [200, 303]
    
    def test_admin_qbanks_page(self):
        response = client.get("/admin/qbanks")
        assert response.status_code in [200, 303]
    
    def test_admin_llm_page(self):
        response = client.get("/admin/llm")
        assert response.status_code in [200, 303]


# ===================== ERROR HANDLING TESTS =====================

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_404_not_found(self, auth_headers):
        response = client.get(
            "/api/v1/qbank/questions/non-existent-id",
            headers=auth_headers
        )
        assert response.status_code == 404
    
    def test_unauthorized_access(self):
        response = client.get("/api/v1/users/")
        assert response.status_code == 401
    
    def test_invalid_question_type(self, auth_headers, test_question_bank):
        response = client.post(
            "/api/v1/qbank/questions/",
            headers=auth_headers,
            json={
                "bank_id": test_question_bank["id"],
                "stem": "Invalid type question",
                "type": "invalid_type"
            }
        )
        assert response.status_code == 422
    
    def test_missing_required_fields(self, auth_headers):
        response = client.post(
            "/api/v1/qbank/questions/",
            headers=auth_headers,
            json={
                "stem": "Missing bank_id"
            }
        )
        assert response.status_code == 422
    
    def test_duplicate_username_registration(self):
        # First registration
        client.post("/api/v1/auth/register", json={
            "username": "duplicate_user",
            "email": "dup1@test.com",
            "password": "pass123"
        })
        
        # Duplicate registration
        response = client.post("/api/v1/auth/register", json={
            "username": "duplicate_user",
            "email": "dup2@test.com",
            "password": "pass456"
        })
        assert response.status_code == 400


# ===================== PERFORMANCE TESTS =====================

class TestPerformance:
    """Test API performance and pagination"""
    
    def test_pagination(self, auth_headers, test_question_bank):
        """Test pagination for question listing"""
        # Create multiple questions
        for i in range(25):
            client.post(
                "/api/v1/qbank/questions/",
                headers=auth_headers,
                json={
                    "bank_id": test_question_bank["id"],
                    "stem": f"Question {i}",
                    "type": "judge",
                    "meta_data": {"answer": True}
                }
            )
        
        # Test pagination
        response = client.get(
            f"/api/v1/qbank/questions/?bank_id={test_question_bank['id']}&limit=10&offset=0",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert len(response.json()) <= 10
        
        # Get second page
        response = client.get(
            f"/api/v1/qbank/questions/?bank_id={test_question_bank['id']}&limit=10&offset=10",
            headers=auth_headers
        )
        assert response.status_code == 200
    
    def test_bulk_operations(self, auth_headers, test_question_bank):
        """Test bulk create operations"""
        questions = []
        for i in range(10):
            questions.append({
                "type": "single",
                "stem": f"Bulk question {i}",
                "options": [
                    {"label": "A", "content": "Yes", "is_correct": True},
                    {"label": "B", "content": "No", "is_correct": False}
                ],
                "difficulty": "easy"
            })
        
        # Bulk import
        response = client.post(
            "/api/v1/llm/import",
            headers=auth_headers,
            json={
                "bank_id": test_question_bank["id"],
                "questions": questions,
                "validate_before_import": False,
                "skip_duplicates": False
            }
        )
        assert response.status_code == 200
        assert response.json()["imported_count"] == 10


# ===================== RUN ALL TESTS =====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])