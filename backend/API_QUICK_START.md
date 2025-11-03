# EXAM-MASTER API Quick Start Guide

## Overview
**Framework**: FastAPI (Python)  
**Current Version**: v2.0.0  
**Active Routes**: v1, v2, MCP  
**Documentation**: `/api/docs` or `/api/redoc`  

## 1. Quick API Access

### Development Server
```bash
cd backend
python run.py  # or: uvicorn app.main:app --reload
```

Visit: http://localhost:8000/api/docs

### Core URLs
```
API v1:      http://localhost:8000/api/v1
API v2:      http://localhost:8000/api/v2
MCP:         http://localhost:8000/api/mcp
Docs:        http://localhost:8000/api/docs
ReDoc:       http://localhost:8000/api/redoc
Admin:       http://localhost:8000/admin
```

## 2. Authentication Flow

### Step 1: Register User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student1",
    "email": "student@example.com",
    "password": "pass123",
    "confirm_password": "pass123"
  }'
```

### Step 2: Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=student1&password=pass123"

# Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Step 3: Use Token
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

## 3. Most Important Endpoints

### Access Question Banks
```bash
# List available banks
GET /api/v1/qbank/banks

# Activate with code (get access to private bank)
POST /api/v1/activation/activate
Body: { "code": "ACTIVATION-CODE" }

# Check your access
GET /api/v1/activation/my-access
```

### Practice Questions
```bash
# Start practice session
POST /api/v1/practice/sessions
Body: {
  "bank_id": "bank-uuid",
  "mode": "random",
  "question_types": ["single", "multiple"]
}

# Submit answer
POST /api/v1/practice/sessions/{session_id}/submit
Body: {
  "question_id": "q-uuid",
  "selected_options": ["A", "B"]
}

# Get statistics
GET /api/v1/practice/sessions/{session_id}/statistics
```

### Manage Learning Progress
```bash
# Add to favorites
POST /api/v1/favorites
Body: { "question_id": "q-uuid", "bank_id": "b-uuid" }

# Track wrong questions
GET /api/v1/wrong-questions
GET /api/v1/wrong-questions?bank_id=b-uuid

# View statistics
GET /api/v1/statistics/overview
GET /api/v1/statistics/daily
```

## 4. File Structure Summary

```
backend/app/
├── api/
│   ├── v1/                 # Main API endpoints
│   │   ├── auth.py         # Login, register
│   │   ├── practice.py     # Practice sessions
│   │   ├── favorites.py    # Bookmarks
│   │   ├── wrong_questions.py # Error tracking
│   │   ├── statistics.py   # Analytics
│   │   ├── activation.py   # Access codes
│   │   ├── llm.py          # AI integration
│   │   ├── ai_chat.py      # Chat interface
│   │   ├── qbank/          # Question bank operations
│   │   │   ├── banks.py    # Bank CRUD
│   │   │   ├── questions.py # Question CRUD
│   │   │   ├── options.py  # Options management
│   │   │   ├── resources.py # File upload
│   │   │   └── imports.py  # Import/Export
│   │   └── qbank_v2.py     # v2 API wrapper
│   ├── v2/                 # Modern API (recommended)
│   │   ├── admin.py        # Admin operations
│   │   ├── exams.py        # Exam management
│   │   └── import_export.py # Data operations
│   └── mcp/                # AI tool integration
│       ├── router.py       # MCP endpoints
│       ├── tools.py        # Tool definitions
│       └── handlers.py     # Tool execution
├── models/                 # Database models
│   ├── user_models.py
│   ├── question_models.py
│   ├── question_models_v2.py
│   ├── user_practice.py
│   ├── user_statistics.py
│   ├── ai_models.py
│   └── activation.py
├── schemas/                # Request/Response schemas
├── services/               # Business logic
└── core/
    ├── database.py         # DB connection
    ├── security.py         # Auth/encryption
    └── config.py           # Settings
```

## 5. Module Organization

### 1. Authentication (`v1/auth.py`)
- User registration
- User login
- Password management
- Current user profile

### 2. User Management (`v1/users.py`)
- List users (admin)
- Manage user roles
- Grant/revoke permissions

### 3. Question Banks (`v1/qbank/*`)
- **Banks**: Create, read, update, delete question banks
- **Questions**: Manage question content
- **Options**: Manage multiple choice options
- **Resources**: Upload/download media files
- **Imports**: Bulk import/export

### 4. Practice Sessions (`v1/practice.py`)
- Create practice sessions
- Submit answers
- Track progress
- Get statistics
- Multiple practice modes

### 5. Learning Analytics (`v1/statistics.py`)
- Daily statistics
- Bank-specific stats
- Performance overview
- Detailed analytics

### 6. Personal Learning (`v1/favorites.py`, `v1/wrong_questions.py`)
- **Favorites**: Bookmark questions
- **Wrong Questions**: Track errors and practice weak areas

### 7. Access Control (`v1/activation.py`)
- Activation codes
- User bank access
- Access revocation
- Admin code generation

### 8. AI Integration (`v1/llm.py`, `v1/ai_chat.py`)
- **LLM**: Configure AI models, manage templates
- **AI Chat**: Conversational practice assistant
- Supports: OpenAI, Claude, Zhipu

### 9. MCP Integration (`mcp/*`)
- Standardized tool interface for AI
- OpenAI & Claude compatible
- Tool discovery and execution

## 6. API Versions Comparison

| Feature | v1 | v2 | MCP |
|---------|----|----|-----|
| Full CRUD | Yes | Yes | No |
| Admin functions | Yes | Yes | No |
| Practice | Yes | Yes | No |
| Conversational | Yes | Yes | Yes |
| Tool-based | No | No | Yes |

## 7. Common Query Parameters

### Pagination (all list endpoints)
```
skip=0         # Start position
limit=20       # Number of results
```

### Filtering (question endpoints)
```
bank_id=uuid              # Filter by bank
type=single|multiple      # Question type
difficulty=easy|medium    # Difficulty
category=string           # Topic
search=keyword            # Full-text search
```

### Practice modes
```
mode=sequential|random|wrong_only|favorite_only
question_types=single,multiple
difficulty=medium
```

## 8. Database Overview

### Two Databases
1. **main.db**: Users, permissions, configurations
2. **question_bank.db**: Questions, banks, statistics

### Key Models
- **User**: Authentication, roles
- **QuestionBank**: Bank metadata
- **Question**: Question content
- **QuestionOption**: Multiple choice options
- **PracticeSession**: Session tracking
- **UserAnswerRecord**: Answer history
- **UserFavorite**: Bookmarks
- **UserWrongQuestion**: Error tracking
- **ActivationCode**: Access codes

## 9. Error Responses

### Common Errors
```
400 Bad Request        - Invalid input
401 Unauthorized       - Missing/invalid token
403 Forbidden          - Insufficient permissions
404 Not Found          - Resource doesn't exist
409 Conflict           - Duplicate/constraint
413 Payload Too Large  - File too large
500 Server Error       - Internal error
```

### Error Response Format
```json
{
  "detail": "Error message",
  "error_code": "ERROR_TYPE"
}
```

## 10. File Upload Limits

```
Images:    10 MB   (.jpg, .png, .gif, .webp, .svg)
Videos:   100 MB   (.mp4, .webm, .avi, .mov, .mkv)
Audio:     20 MB   (.mp3, .wav, .ogg, .m4a, .flac)
Docs:      20 MB   (.pdf, .doc, .docx, .txt)
CSV:       50 MB   (UTF-8 encoded)
JSON:      50 MB   (valid JSON)
ZIP:      200 MB   (valid archive)
```

## 11. Development Tips

### 1. Generate Test Data
```bash
python init_database_v2.py  # Initialize with test data
```

### 2. Run Tests
```bash
pytest tests/test_api.py
```

### 3. API Documentation Endpoints
```
Swagger:   /api/docs         # Interactive docs
ReDoc:     /api/redoc        # Alternative docs
OpenAPI:   /openapi.json     # Schema file
```

### 4. Admin Dashboard
```
Login:     /admin/login
Dashboard: /admin            # Requires session
```

### 5. Using Interactive Docs
1. Visit `http://localhost:8000/api/docs`
2. Click on any endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"

## 12. Typical User Journey

```
1. Register               POST   /auth/register
2. Login                  POST   /auth/login (get token)
3. List banks             GET    /qbank/banks
4. Activate (if needed)   POST   /activation/activate
5. Start practice         POST   /practice/sessions
6. Get question           GET    /practice/sessions/{id}/current
7. Submit answer          POST   /practice/sessions/{id}/submit
8. View stats             GET    /statistics/overview
9. Add to favorites       POST   /favorites
10. Review progress       GET    /statistics/daily
```

## 13. Admin/Teacher Journey

```
1. Login as admin         POST   /auth/login
2. Create bank            POST   /qbank/banks
3. Add questions          POST   /qbank/questions
4. Manage users           GET    /users
5. Create activation codes POST   /activation/admin/codes
6. View statistics        GET    /stats/overview
7. Configure AI           POST   /llm/interfaces
```

## 14. Key Configuration

### Environment Variables (`.env`)
```
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-key
DATABASE_URL=sqlite:///databases/main.db
QUESTION_BANK_DATABASE_URL=sqlite:///databases/question_bank.db
DEBUG=False
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Database Locations
```
Main DB:        ./databases/main.db
QBank DB:       ./databases/question_bank.db
Uploads:        ./storage/uploads/
Resources:      ./storage/resources/
Exports:        ./storage/question_banks/
```

## 15. Recommended Tools

### Testing API
- **Postman**: Desktop API client
- **Insomnia**: REST client
- **curl**: Command line (examples in this guide)
- **VS Code**: Rest Client extension

### Documentation
- Built-in Swagger: `/api/docs`
- Built-in ReDoc: `/api/redoc`
- This guide: API_STRUCTURE_REPORT.md
- Complete endpoints: API_ENDPOINTS_REFERENCE.md

## 16. Contact & Support

For issues or questions:
1. Check `/api/docs` for endpoint details
2. Review API_STRUCTURE_REPORT.md
3. Look at test files in `tests/`
4. Check initialization scripts

