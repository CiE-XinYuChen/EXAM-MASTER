"""
Complete API Testing Suite for EXAM-MASTER Backend
Tests all actively used API endpoints and admin routes
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

# Global test data
TEST_ADMIN_ID = None
TEST_BANK_ID = None

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Create test databases and initial data"""
    global TEST_ADMIN_ID
    
    # Create tables
    BaseMain.metadata.create_all(bind=engine_main)
    BaseQBank.metadata.create_all(bind=engine_qbank)
    
    # Create test admin user
    db = TestingSessionMain()
    admin_user = User(
        username="admin",
        email="admin@test.com",
        password_hash=get_password_hash("admin123"),
        role=UserRole.admin,  # Use role instead of is_admin
        is_active=True
    )
    db.add(admin_user)
    db.commit()
    TEST_ADMIN_ID = admin_user.id
    db.close()
    
    # Create test question bank
    db = TestingSessionQBank()
    test_bank = QuestionBank(
        id=str(uuid.uuid4()),
        name="Test Bank",
        description="Test question bank for testing",
        category="test",
        creator_id=TEST_ADMIN_ID,
        is_public=True
    )
    db.add(test_bank)
    db.commit()
    global TEST_BANK_ID
    TEST_BANK_ID = test_bank.id
    db.close()
    
    yield
    
    # Cleanup
    BaseMain.metadata.drop_all(bind=engine_main)
    BaseQBank.metadata.drop_all(bind=engine_qbank)

@pytest.fixture
def auth_token():
    """Get auth token for admin user"""
    response = client.post("/api/v1/auth/login", data={
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
def admin_session():
    """Create admin session for admin panel tests"""
    response = client.post("/admin/login", data={
        "username": "admin",
        "password": "admin123"
    }, follow_redirects=False)
    return client


# ===================== SYSTEM & HEALTH TESTS =====================

class TestSystemEndpoints:
    """Test system and health check endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


# ===================== AUTHENTICATION API TESTS =====================

class TestAuthenticationAPI:
    """Test authentication API endpoints"""
    
    def test_login_success(self):
        """Test successful login"""
        response = client.post("/api/v1/auth/login", data={
            "username": "admin",
            "password": "admin123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = client.post("/api/v1/auth/login", data={
            "username": "admin",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
    
    def test_register_new_user(self):
        """Test user registration"""
        response = client.post("/api/v1/auth/register", json={
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "password123",
            "confirm_password": "password123"
        })
        assert response.status_code == 201  # Created status
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@test.com"
        assert data["role"] == "student"  # Default role
    
    def test_register_duplicate_username(self):
        """Test registration with duplicate username"""
        response = client.post("/api/v1/auth/register", json={
            "username": "admin",  # Already exists
            "email": "another@test.com",
            "password": "password123",
            "confirm_password": "password123"
        })
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_get_current_user(self, auth_headers):
        """Test getting current user info"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["role"] == "admin"
    
    def test_change_password(self, auth_headers):
        """Test changing password"""
        # Change password
        response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "old_password": "admin123",
                "new_password": "newpass456"
            }
        )
        assert response.status_code == 200
        
        # Verify new password works
        response = client.post("/api/v1/auth/login", data={
            "username": "admin",
            "password": "newpass456"
        })
        assert response.status_code == 200
        
        # Change back to original
        new_token = response.json()["access_token"]
        response = client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {new_token}"},
            json={
                "old_password": "newpass456",
                "new_password": "admin123"
            }
        )
        assert response.status_code == 200


# ===================== QUESTION BANK API TESTS =====================

class TestQuestionBankAPI:
    """Test question bank management APIs"""
    
    def test_create_question_bank(self, auth_headers):
        """Test creating a question bank"""
        response = client.post(
            "/api/v1/qbank/banks/",
            headers=auth_headers,
            json={
                "name": "Python Programming",
                "description": "Python programming questions",
                "category": "programming",
                "version": "1.0",
                "is_public": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Python Programming"
        assert data["category"] == "programming"
        return data["id"]
    
    def test_list_question_banks(self, auth_headers):
        """Test listing question banks"""
        response = client.get("/api/v1/qbank/banks/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0  # At least test bank exists
    
    def test_get_question_bank(self, auth_headers):
        """Test getting specific question bank"""
        response = client.get(f"/api/v1/qbank/banks/{TEST_BANK_ID}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == TEST_BANK_ID
        assert data["name"] == "Test Bank"
    
    def test_update_question_bank(self, auth_headers):
        """Test updating question bank"""
        response = client.put(
            f"/api/v1/qbank/banks/{TEST_BANK_ID}",
            headers=auth_headers,
            json={
                "description": "Updated description"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"
    
    def test_delete_question_bank(self, auth_headers):
        """Test deleting question bank"""
        # Create a bank to delete
        create_response = client.post(
            "/api/v1/qbank/banks/",
            headers=auth_headers,
            json={
                "name": "Bank to Delete",
                "description": "Will be deleted"
            }
        )
        bank_id = create_response.json()["id"]
        
        # Delete it
        response = client.delete(f"/api/v1/qbank/banks/{bank_id}", headers=auth_headers)
        assert response.status_code == 200
        
        # Verify deletion
        response = client.get(f"/api/v1/qbank/banks/{bank_id}", headers=auth_headers)
        assert response.status_code == 404


# ===================== LLM INTERFACE API TESTS =====================

class TestLLMInterfaceAPI:
    """Test LLM interface management APIs"""
    
    def test_create_openai_interface(self, auth_headers):
        """Test creating OpenAI compatible interface"""
        response = client.post(
            "/api/v1/llm/interfaces",
            headers=auth_headers,
            json={
                "name": "OpenAI GPT-4",
                "type": "openai-compatible",
                "config": {
                    "base_url": "https://api.openai.com/v1",
                    "api_key": "sk-test-key",
                    "model": "gpt-4",
                    "timeout": 60,
                    "max_retries": 3
                },
                "is_active": True,
                "is_default": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "OpenAI GPT-4"
        assert data["type"] == "openai-compatible"
        return data["id"]
    
    def test_create_zhipu_interface(self, auth_headers):
        """Test creating Zhipu AI interface"""
        response = client.post(
            "/api/v1/llm/interfaces",
            headers=auth_headers,
            json={
                "name": "Zhipu GLM-4",
                "type": "zhipu-ai",
                "config": {
                    "base_url": "https://open.bigmodel.cn/api/paas/v4",
                    "api_key": "test.zhipu.key",
                    "model": "glm-4",
                    "timeout": 120
                },
                "is_active": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "zhipu-ai"
        return data["id"]
    
    def test_list_interfaces(self, auth_headers):
        """Test listing LLM interfaces"""
        response = client.get("/api/v1/llm/interfaces", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_list_active_interfaces_only(self, auth_headers):
        """Test listing only active interfaces"""
        response = client.get("/api/v1/llm/interfaces?only_active=true", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        for interface in data:
            assert interface["is_active"] == True
    
    def test_update_interface(self, auth_headers):
        """Test updating LLM interface"""
        # Create interface first
        create_resp = client.post(
            "/api/v1/llm/interfaces",
            headers=auth_headers,
            json={
                "name": "Test Interface",
                "type": "openai-compatible",
                "config": {
                    "base_url": "https://api.test.com",
                    "api_key": "test-key",
                    "model": "test-model"
                }
            }
        )
        interface_id = create_resp.json()["id"]
        
        # Update it
        response = client.put(
            f"/api/v1/llm/interfaces/{interface_id}",
            headers=auth_headers,
            json={
                "name": "Updated Interface",
                "is_active": False,
                "type": "anthropic"  # Change type
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Interface"
        assert data["is_active"] == False
        assert data["type"] == "anthropic"
    
    def test_delete_interface(self, auth_headers):
        """Test deleting LLM interface"""
        # Create interface
        create_resp = client.post(
            "/api/v1/llm/interfaces",
            headers=auth_headers,
            json={
                "name": "To Delete",
                "type": "openai-compatible",
                "config": {
                    "base_url": "https://api.test.com",
                    "api_key": "test",
                    "model": "test"
                }
            }
        )
        interface_id = create_resp.json()["id"]
        
        # Delete it
        response = client.delete(f"/api/v1/llm/interfaces/{interface_id}", headers=auth_headers)
        assert response.status_code == 200
        
        # Verify deletion
        response = client.get(f"/api/v1/llm/interfaces/{interface_id}", headers=auth_headers)
        assert response.status_code == 404
    
    def test_test_interface(self, auth_headers):
        """Test interface connectivity test"""
        # Create interface
        create_resp = client.post(
            "/api/v1/llm/interfaces",
            headers=auth_headers,
            json={
                "name": "Test Connection",
                "type": "openai-compatible",
                "config": {
                    "base_url": "https://api.openai.com/v1",
                    "api_key": "invalid-key",
                    "model": "gpt-3.5-turbo"
                }
            }
        )
        interface_id = create_resp.json()["id"]
        
        # Test connection (will fail with invalid key)
        response = client.post(
            f"/api/v1/llm/interfaces/{interface_id}/test",
            headers=auth_headers,
            json={
                "test_prompt": "Hello, respond with OK"
            }
        )
        # Should return error but not crash
        assert response.status_code in [200, 500]
        data = response.json()
        if response.status_code == 500:
            assert "error" in data or "detail" in data


# ===================== PROMPT TEMPLATE API TESTS =====================

class TestPromptTemplateAPI:
    """Test prompt template management APIs"""
    
    def test_create_template(self, auth_headers):
        """Test creating prompt template"""
        response = client.post(
            "/api/v1/llm/templates",
            headers=auth_headers,
            json={
                "name": "Question Parser Template",
                "type": "question_parser",
                "category": "parsing",
                "content": "Parse the following text into questions:\n{text}",
                "variables": ["text"],
                "description": "Template for parsing questions from text",
                "example_input": "What is Python?",
                "example_output": '{"type": "essay", "stem": "What is Python?"}',
                "is_public": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Question Parser Template"
        assert data["type"] == "question_parser"
        return data["id"]
    
    def test_list_templates(self, auth_headers):
        """Test listing templates"""
        response = client.get("/api/v1/llm/templates", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_preset_templates(self):
        """Test getting preset templates (no auth required)"""
        response = client.get("/api/v1/llm/templates/presets")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_update_template(self, auth_headers):
        """Test updating template"""
        # Create template
        create_resp = client.post(
            "/api/v1/llm/templates",
            headers=auth_headers,
            json={
                "name": "Test Template",
                "type": "custom",
                "content": "Original content"
            }
        )
        template_id = create_resp.json()["id"]
        
        # Update it
        response = client.put(
            f"/api/v1/llm/templates/{template_id}",
            headers=auth_headers,
            json={
                "content": "Updated content",
                "is_public": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Updated content"
        assert data["is_public"] == True
    
    def test_delete_template(self, auth_headers):
        """Test deleting template"""
        # Create template
        create_resp = client.post(
            "/api/v1/llm/templates",
            headers=auth_headers,
            json={
                "name": "To Delete",
                "type": "custom",
                "content": "Delete me"
            }
        )
        template_id = create_resp.json()["id"]
        
        # Delete it
        response = client.delete(f"/api/v1/llm/templates/{template_id}", headers=auth_headers)
        assert response.status_code == 200


# ===================== ADMIN PANEL ROUTE TESTS =====================

class TestAdminPanelRoutes:
    """Test admin panel HTML routes"""
    
    def test_admin_login_page(self):
        """Test admin login page loads"""
        response = client.get("/admin/login")
        assert response.status_code == 200
        assert b"login" in response.content.lower()
    
    def test_admin_login_process(self):
        """Test admin login process"""
        response = client.post("/admin/login", data={
            "username": "admin",
            "password": "admin123"
        }, follow_redirects=False)
        assert response.status_code == 303  # Redirect after login
        assert response.headers["location"] == "/admin"
    
    def test_admin_dashboard_requires_auth(self):
        """Test admin dashboard requires authentication"""
        response = client.get("/admin", follow_redirects=False)
        assert response.status_code == 303  # Redirect to login
    
    def test_admin_questions_page(self, admin_session):
        """Test questions management page"""
        # Login first
        admin_session.post("/admin/login", data={
            "username": "admin",
            "password": "admin123"
        })
        
        response = admin_session.get("/admin/questions")
        assert response.status_code in [200, 303]
    
    def test_admin_question_create_page(self, admin_session):
        """Test question creation page"""
        admin_session.post("/admin/login", data={
            "username": "admin",
            "password": "admin123"
        })
        
        response = admin_session.get("/admin/questions/create")
        assert response.status_code in [200, 303]
    
    def test_admin_qbanks_page(self, admin_session):
        """Test question banks page"""
        admin_session.post("/admin/login", data={
            "username": "admin",
            "password": "admin123"
        })
        
        response = admin_session.get("/admin/qbanks")
        assert response.status_code in [200, 303]
    
    def test_admin_llm_page(self, admin_session):
        """Test LLM management page"""
        admin_session.post("/admin/login", data={
            "username": "admin",
            "password": "admin123"
        })
        
        response = admin_session.get("/admin/llm")
        assert response.status_code in [200, 303]


# ===================== QUESTION CREATION TESTS (ALL TYPES) =====================

class TestQuestionCreation:
    """Test creating all types of questions through admin panel"""
    
    def test_create_single_choice_question(self, admin_session):
        """Test creating single choice question"""
        admin_session.post("/admin/login", data={
            "username": "admin",
            "password": "admin123"
        })
        
        response = admin_session.post("/admin/questions/create", json={
            "bank_id": TEST_BANK_ID,
            "type": "single",
            "stem": "What is 2 + 2?",
            "difficulty": "easy",
            "category": "math",
            "tags": ["addition", "basic"],
            "options": [
                {"label": "A", "content": "3", "is_correct": False},
                {"label": "B", "content": "4", "is_correct": True},
                {"label": "C", "content": "5", "is_correct": False},
                {"label": "D", "content": "6", "is_correct": False}
            ],
            "explanation": "2 + 2 equals 4"
        })
        assert response.status_code in [200, 303]
    
    def test_create_multiple_choice_question(self, admin_session):
        """Test creating multiple choice question"""
        admin_session.post("/admin/login", data={
            "username": "admin",
            "password": "admin123"
        })
        
        response = admin_session.post("/admin/questions/create", json={
            "bank_id": TEST_BANK_ID,
            "type": "multiple",
            "stem": "Which of the following are programming languages?",
            "difficulty": "medium",
            "category": "programming",
            "tags": ["languages"],
            "options": [
                {"label": "A", "content": "Python", "is_correct": True},
                {"label": "B", "content": "HTML", "is_correct": False},
                {"label": "C", "content": "Java", "is_correct": True},
                {"label": "D", "content": "CSS", "is_correct": False}
            ]
        })
        assert response.status_code in [200, 303]
    
    def test_create_judge_question(self, admin_session):
        """Test creating true/false question"""
        admin_session.post("/admin/login", data={
            "username": "admin",
            "password": "admin123"
        })
        
        response = admin_session.post("/admin/questions/create", json={
            "bank_id": TEST_BANK_ID,
            "type": "judge",
            "stem": "Python is a compiled language",
            "difficulty": "easy",
            "category": "programming",
            "tags": ["python", "basics"],
            "meta_data": {
                "answer": False
            },
            "explanation": "Python is an interpreted language, not compiled"
        })
        assert response.status_code in [200, 303]
    
    def test_create_fill_question(self, admin_session):
        """Test creating fill-in-the-blank question"""
        admin_session.post("/admin/login", data={
            "username": "admin",
            "password": "admin123"
        })
        
        response = admin_session.post("/admin/questions/create", json={
            "bank_id": TEST_BANK_ID,
            "type": "fill",
            "stem": "Python was created by ____ in the year ____",
            "difficulty": "medium",
            "category": "history",
            "tags": ["python", "history"],
            "meta_data": {
                "blanks": [
                    {
                        "position": 0,
                        "answer": "Guido van Rossum",
                        "alternatives": ["Guido", "Van Rossum"]
                    },
                    {
                        "position": 1,
                        "answer": "1991",
                        "alternatives": []
                    }
                ]
            }
        })
        assert response.status_code in [200, 303]
    
    def test_create_essay_question(self, admin_session):
        """Test creating essay question"""
        admin_session.post("/admin/login", data={
            "username": "admin",
            "password": "admin123"
        })
        
        response = admin_session.post("/admin/questions/create", json={
            "bank_id": TEST_BANK_ID,
            "type": "essay",
            "stem": "Explain the difference between lists and tuples in Python",
            "difficulty": "hard",
            "category": "programming",
            "tags": ["python", "data-structures"],
            "meta_data": {
                "reference_answer": "Lists are mutable while tuples are immutable. Lists use square brackets [], tuples use parentheses (). Lists can be modified after creation, tuples cannot.",
                "keywords": ["mutable", "immutable", "brackets", "parentheses"]
            }
        })
        assert response.status_code in [200, 303]


# ===================== LLM PARSING & IMPORT TESTS =====================

class TestLLMParsing:
    """Test LLM parsing and import functionality"""
    
    def test_parse_single_choice(self, auth_headers):
        """Test parsing single choice question"""
        # First create an interface
        interface_resp = client.post(
            "/api/v1/llm/interfaces",
            headers=auth_headers,
            json={
                "name": "Test Parser",
                "type": "openai-compatible",
                "config": {
                    "base_url": "https://api.openai.com/v1",
                    "api_key": "test-key",
                    "model": "gpt-3.5-turbo"
                }
            }
        )
        interface_id = interface_resp.json()["id"]
        
        # Try to parse (will fail with test key but should handle gracefully)
        response = client.post(
            "/api/v1/llm/parse",
            headers=auth_headers,
            json={
                "interface_id": interface_id,
                "raw_text": "Question: What is Python?\nA. A snake\nB. A programming language\nC. A movie\nD. A fruit\nAnswer: B",
                "hint_type": "single",
                "bank_id": TEST_BANK_ID
            }
        )
        # Should handle error gracefully
        assert response.status_code in [200, 500]
    
    def test_batch_import_questions(self, auth_headers):
        """Test batch importing parsed questions"""
        response = client.post(
            "/api/v1/llm/import",
            headers=auth_headers,
            json={
                "bank_id": TEST_BANK_ID,
                "questions": [
                    {
                        "type": "single",
                        "stem": "What is the capital of France?",
                        "difficulty": "easy",
                        "category": "geography",
                        "options": [
                            {"label": "A", "content": "London", "is_correct": False},
                            {"label": "B", "content": "Paris", "is_correct": True},
                            {"label": "C", "content": "Berlin", "is_correct": False},
                            {"label": "D", "content": "Madrid", "is_correct": False}
                        ]
                    },
                    {
                        "type": "judge",
                        "stem": "The Earth is flat",
                        "difficulty": "easy",
                        "correct_answer": "false"
                    },
                    {
                        "type": "fill",
                        "stem": "The capital of ____ is Paris",
                        "difficulty": "easy",
                        "blanks": [
                            {"position": 0, "answer": "France", "alternatives": []}
                        ]
                    }
                ],
                "validate_before_import": True,
                "skip_duplicates": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["imported_count"] >= 0


# ===================== CSV IMPORT/EXPORT TESTS =====================

class TestImportExport:
    """Test import and export functionality"""
    
    def test_download_import_template(self, admin_session):
        """Test downloading CSV template"""
        admin_session.post("/admin/login", data={
            "username": "admin",
            "password": "admin123"
        })
        
        response = admin_session.get("/admin/imports/template")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
    
    def test_csv_import(self, admin_session):
        """Test importing questions from CSV"""
        admin_session.post("/admin/login", data={
            "username": "admin",
            "password": "admin123"
        })
        
        # Create CSV content as bytes
        csv_content = "题干,类型,选项A,选项B,选项C,选项D,正确答案,难度,分类,解析\n"
        csv_content += "What is 1+1?,single,1,2,3,4,B,easy,math,1+1=2\n"
        
        response = admin_session.post(
            "/admin/imports/csv",
            data={
                "bank_id": TEST_BANK_ID,
                "merge_duplicates": "true"
            },
            files={
                "file": ("test.csv", csv_content.encode('utf-8'), "text/csv")
            }
        )
        assert response.status_code in [200, 303]
    
    def test_export_question_bank(self, admin_session):
        """Test exporting question bank"""
        admin_session.post("/admin/login", data={
            "username": "admin",
            "password": "admin123"
        })
        
        response = admin_session.get(f"/admin/exports/{TEST_BANK_ID}?format=csv")
        assert response.status_code in [200, 303]


# ===================== ERROR HANDLING TESTS =====================

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_unauthorized_access(self):
        """Test accessing protected endpoint without auth"""
        response = client.get("/api/v1/llm/interfaces")
        assert response.status_code == 401
    
    def test_invalid_token(self):
        """Test using invalid auth token"""
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/api/v1/llm/interfaces", headers=headers)
        assert response.status_code == 401
    
    def test_not_found_resource(self, auth_headers):
        """Test accessing non-existent resource"""
        response = client.get(
            "/api/v1/llm/interfaces/non-existent-id",
            headers=auth_headers
        )
        assert response.status_code == 404
    
    def test_invalid_question_type(self, admin_session):
        """Test creating question with invalid type"""
        admin_session.post("/admin/login", data={
            "username": "admin",
            "password": "admin123"
        })
        
        response = admin_session.post("/admin/questions/create", json={
            "bank_id": TEST_BANK_ID,
            "type": "invalid_type",
            "stem": "Test question"
        })
        assert response.status_code in [400, 422, 500]
    
    def test_missing_required_fields(self, auth_headers):
        """Test API with missing required fields"""
        response = client.post(
            "/api/v1/llm/interfaces",
            headers=auth_headers,
            json={
                "name": "Missing Config"
                # Missing required 'type' and 'config'
            }
        )
        assert response.status_code == 422
    
    def test_invalid_enum_value(self, auth_headers):
        """Test using invalid enum value"""
        response = client.post(
            "/api/v1/llm/interfaces",
            headers=auth_headers,
            json={
                "name": "Test",
                "type": "invalid-type",  # Invalid interface type
                "config": {
                    "base_url": "https://test.com",
                    "api_key": "test",
                    "model": "test"
                }
            }
        )
        assert response.status_code == 422


# ===================== PERFORMANCE & EDGE CASE TESTS =====================

class TestPerformanceAndEdgeCases:
    """Test performance and edge cases"""
    
    def test_large_batch_import(self, auth_headers):
        """Test importing large batch of questions"""
        questions = []
        for i in range(50):
            questions.append({
                "type": "single",
                "stem": f"Question {i}: What is {i} + {i}?",
                "difficulty": "easy",
                "options": [
                    {"label": "A", "content": str(i), "is_correct": False},
                    {"label": "B", "content": str(i*2), "is_correct": True},
                    {"label": "C", "content": str(i*3), "is_correct": False},
                    {"label": "D", "content": str(i*4), "is_correct": False}
                ]
            })
        
        response = client.post(
            "/api/v1/llm/import",
            headers=auth_headers,
            json={
                "bank_id": TEST_BANK_ID,
                "questions": questions,
                "validate_before_import": False,
                "skip_duplicates": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["imported_count"] == 50
    
    def test_special_characters_in_question(self, admin_session):
        """Test creating question with special characters"""
        admin_session.post("/admin/login", data={
            "username": "admin",
            "password": "admin123"
        })
        
        response = admin_session.post("/admin/questions/create", json={
            "bank_id": TEST_BANK_ID,
            "type": "judge",
            "stem": "Is 'Hello \"World\"' & <HTML> valid? 中文测试 😀",
            "difficulty": "medium",
            "meta_data": {"answer": True}
        })
        assert response.status_code in [200, 303]
    
    def test_very_long_question_content(self, admin_session):
        """Test creating question with very long content"""
        admin_session.post("/admin/login", data={
            "username": "admin",
            "password": "admin123"
        })
        
        long_text = "A" * 5000  # 5000 characters
        response = admin_session.post("/admin/questions/create", json={
            "bank_id": TEST_BANK_ID,
            "type": "essay",
            "stem": long_text,
            "difficulty": "hard",
            "meta_data": {
                "reference_answer": "Long answer",
                "keywords": ["test"]
            }
        })
        assert response.status_code in [200, 303]
    
    def test_concurrent_interface_updates(self, auth_headers):
        """Test concurrent updates to same interface"""
        # Create interface
        create_resp = client.post(
            "/api/v1/llm/interfaces",
            headers=auth_headers,
            json={
                "name": "Concurrent Test",
                "type": "openai-compatible",
                "config": {
                    "base_url": "https://test.com",
                    "api_key": "test",
                    "model": "test"
                }
            }
        )
        interface_id = create_resp.json()["id"]
        
        # Simulate concurrent updates
        response1 = client.put(
            f"/api/v1/llm/interfaces/{interface_id}",
            headers=auth_headers,
            json={"name": "Update 1"}
        )
        response2 = client.put(
            f"/api/v1/llm/interfaces/{interface_id}",
            headers=auth_headers,
            json={"name": "Update 2"}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Check final state
        final_resp = client.get(f"/api/v1/llm/interfaces/{interface_id}", headers=auth_headers)
        assert final_resp.json()["name"] in ["Update 1", "Update 2"]


# ===================== RUN ALL TESTS =====================

if __name__ == "__main__":
    import sys
    pytest_args = [
        __file__,
        "-v",  # Verbose
        "--tb=short",  # Short traceback
        "--color=yes",  # Colored output
        "-x",  # Stop on first failure
        "--capture=no"  # Show print statements
    ]
    
    # Add specific test if provided
    if len(sys.argv) > 1:
        pytest_args.append(f"-k={sys.argv[1]}")
    
    pytest.main(pytest_args)