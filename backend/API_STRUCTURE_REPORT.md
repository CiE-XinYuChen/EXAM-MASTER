# EXAM-MASTER Backend API Structure Report

## Executive Summary

The EXAM-MASTER backend is a comprehensive FastAPI-based educational platform with dual API versions (v1 and v2), sophisticated question bank management, AI integration via MCP (Model Context Protocol), and user learning analytics.

**Framework**: FastAPI (Python)
**Database**: SQLite (dual databases: main.db and question_bank.db)
**API Versions**: v1 (legacy), v2 (recommended), MCP (AI integration)
**Deployment**: Available at `/api/v1`, `/api/v2`, and `/api/mcp`

---

## 1. Directory Structure

```
backend/app/api/
├── __init__.py (API routes aggregator)
├── mcp/ (Model Context Protocol - AI Integration)
│   ├── __init__.py
│   ├── handlers.py (Tool execution handlers)
│   ├── router.py (MCP endpoints)
│   └── tools.py (MCP tool definitions)
├── v1/ (API Version 1 - Active endpoints)
│   ├── __init__.py (Router registration)
│   ├── auth.py (Authentication & authorization)
│   ├── users.py (User management)
│   ├── ai_chat.py (AI conversational interface)
│   ├── activation.py (Activation codes & access control)
│   ├── practice.py (Practice session management)
│   ├── statistics.py (User learning statistics)
│   ├── favorites.py (Bookmark management)
│   ├── wrong_questions.py (Error tracking)
│   ├── llm.py (LLM interface & templates)
│   ├── qbank_v2.py (Question bank v2 API)
│   └── qbank/ (Submodule for question bank operations)
│       ├── __init__.py
│       ├── banks.py (Bank CRUD operations)
│       ├── questions.py (Question CRUD operations)
│       ├── options.py (Option management)
│       ├── imports.py (Import/Export operations)
│       └── resources.py (Media file management)
└── v2/ (API Version 2 - Recommended for new development)
    ├── __init__.py (Router registration)
    ├── admin.py (System administration & analytics)
    ├── exams.py (Exam & practice sessions)
    └── import_export.py (Data import/export operations)
```

---

## 2. API Versions Overview

### Version 1 (v1) - `/api/v1`
**Status**: Active, Feature-complete
**Use Case**: Legacy endpoints, comprehensive feature set
**Key Features**:
- Modular routing with submodules
- Fine-grained permission controls
- Multiple practice/practice modes
- Direct question bank access

### Version 2 (v2) - `/api/v2`
**Status**: Recommended
**Use Case**: New projects, streamlined operations
**Key Features**:
- Consolidated endpoints
- Improved admin dashboard
- Better data import/export
- Cleaner organization

### MCP (Model Context Protocol) - `/api/mcp`
**Status**: AI Integration Layer
**Use Case**: AI agent integration, tool calling
**Key Features**:
- Standardized tool schemas (OpenAI/Claude compatible)
- Tool execution framework
- Batch operations support

---

## 3. Core API Modules & Endpoints

### 3.1 Authentication & Authorization
**File**: `v1/auth.py`
**Prefix**: `/api/v1/auth`

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/login` | User login with username/email | No |
| POST | `/register` | Register new user | No |
| POST | `/change-password` | Change user password | Yes |
| GET | `/me` | Get current user profile | Yes |
| POST | `/logout` | Logout current user | Yes |

---

### 3.2 User Management
**File**: `v1/users.py`
**Prefix**: `/api/v1/users`

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | List all users | Yes (Admin) |
| GET | `/{user_id}` | Get user details | Yes (Admin) |
| PUT | `/{user_id}` | Update user | Yes (Admin) |
| DELETE | `/{user_id}` | Delete user | Yes (Admin) |
| GET | `/{user_id}/permissions` | Get user permissions | Yes (Admin) |
| POST | `/{user_id}/permissions` | Grant bank access | Yes (Admin) |
| DELETE | `/{user_id}/permissions/{bank_id}` | Revoke access | Yes (Admin) |

**Features**:
- Role-based access control (admin, teacher, student)
- Bank-level permission management
- User activation/deactivation
- Password hashing with security

---

### 3.3 Question Bank Management

#### 3.3.1 Banks Module
**File**: `v1/qbank/banks.py`
**Prefix**: `/api/v1/qbank/banks`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List accessible question banks |
| POST | `/` | Create new bank |
| GET | `/{bank_id}` | Get bank details |
| PUT | `/{bank_id}` | Update bank |
| DELETE | `/{bank_id}` | Delete bank |
| POST | `/{bank_id}/clone` | Clone bank |

**Query Parameters**:
- `category`: Filter by category
- `is_public`: Filter by public/private
- `skip`, `limit`: Pagination

---

#### 3.3.2 Questions Module
**File**: `v1/qbank/questions.py`
**Prefix**: `/api/v1/qbank/questions`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List questions with filters |
| POST | `/` | Create new question |
| GET | `/{question_id}` | Get question details |
| PUT | `/{question_id}` | Update question |
| DELETE | `/{question_id}` | Delete question |
| POST | `/{question_id}/options` | Add question options |
| POST | `/{question_id}/duplicate` | Duplicate question |

**Supported Filters**:
- `bank_id`: Filter by bank
- `type`: Question type (single, multiple, etc.)
- `difficulty`: Difficulty level
- `category`: Question category
- `search`: Full-text search on stem
- `tags`: Filter by tags

---

#### 3.3.3 Options Module
**File**: `v1/qbank/options.py`
**Prefix**: `/api/v1/qbank/options`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/{option_id}` | Get option details |
| PUT | `/{option_id}` | Update option |
| DELETE | `/{option_id}` | Delete option |
| POST | `/{option_id}/reorder` | Reorder options |
| POST | `/batch-update` | Bulk update options |

---

#### 3.3.4 Resources Module (Media Management)
**File**: `v1/qbank/resources.py`
**Prefix**: `/api/v1/qbank/resources`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload single resource |
| POST | `/batch-upload` | Upload multiple resources |
| GET | `/{resource_id}` | Get resource metadata |
| GET | `/{resource_id}/download` | Download resource |
| DELETE | `/{resource_id}` | Delete resource |

**Supported File Types**:
- **Images** (10MB max): .jpg, .jpeg, .png, .gif, .svg, .webp, .bmp
- **Videos** (100MB max): .mp4, .webm, .avi, .mov, .mkv
- **Audio** (20MB max): .mp3, .wav, .ogg, .m4a, .flac
- **Documents** (20MB max): .pdf, .doc, .docx, .txt, .tex, .md

---

#### 3.3.5 Import/Export Module
**File**: `v1/qbank/imports.py`
**Prefix**: `/api/v1/qbank/import`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/csv` | Import questions from CSV |
| POST | `/json` | Import bank from JSON |
| POST | `/validate` | Validate import format |
| GET | `/export/{bank_id}` | Export bank as file |

**Supported Formats**:
- CSV (structured questions)
- JSON (complete bank structure)
- ZIP (batch import/export)

---

#### 3.3.6 Question Bank API v2
**File**: `v1/qbank_v2.py`
**Prefix**: `/api/v1/qbank`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/banks` | Create bank (v2) |
| GET | `/banks` | List banks (v2) |
| GET | `/banks/{bank_id}` | Get bank (v2) |
| PUT | `/banks/{bank_id}` | Update bank (v2) |
| DELETE | `/banks/{bank_id}` | Delete bank (v2) |
| POST | `/banks/{bank_id}/questions` | Add question |
| GET | `/banks/{bank_id}/questions` | List questions in bank |
| POST | `/banks/{bank_id}/export` | Export bank |
| POST | `/banks/{bank_id}/duplicate` | Duplicate bank |
| GET | `/banks/{bank_id}/stats` | Bank statistics |
| GET | `/categories` | List categories |
| GET | `/search` | Full-text search |
| GET | `/stats/users` | User statistics |
| GET | `/stats/banks` | Bank statistics |
| GET | `/stats/questions` | Question statistics |

---

### 3.4 Practice & Learning Sessions
**File**: `v1/practice.py`
**Prefix**: `/api/v1/practice`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/sessions` | Create practice session |
| GET | `/sessions` | List user's sessions |
| GET | `/sessions/{session_id}` | Get session details |
| PUT | `/sessions/{session_id}` | Update session |
| DELETE | `/sessions/{session_id}` | End session |
| POST | `/sessions/{session_id}/submit` | Submit answer |
| GET | `/sessions/{session_id}/current` | Get current question |
| GET | `/sessions/{session_id}/statistics` | Session statistics |
| GET | `/history` | Get answer history |

**Practice Modes**:
- Sequential: Questions in order
- Random: Random question selection
- Wrong-only: Only incorrect questions
- Favorite-only: Only bookmarked questions

**Session Features**:
- Multiple question filtering (type, difficulty, category)
- Real-time progress tracking
- Answer submission and immediate feedback
- Statistics per session

---

### 3.5 User Statistics & Analytics
**File**: `v1/statistics.py`
**Prefix**: `/api/v1/statistics`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/daily` | Daily statistics |
| GET | `/bank/{bank_id}` | Bank-specific statistics |
| GET | `/banks` | All banks statistics |
| GET | `/overview` | User overview statistics |
| GET | `/detailed` | Detailed analytics |

**Tracked Metrics**:
- Questions attempted
- Correct/incorrect answers
- Accuracy rate
- Time spent
- Difficulty distribution
- Category performance
- Streaks and patterns

---

### 3.6 Favorites Management
**File**: `v1/favorites.py`
**Prefix**: `/api/v1/favorites`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `` | Add favorite |
| GET | `` | List favorites |
| GET | `/{favorite_id}` | Get favorite |
| PUT | `/{favorite_id}` | Update favorite |
| DELETE | `/{favorite_id}` | Remove favorite |
| DELETE | `/question/{question_id}` | Remove by question |
| GET | `/check/{question_id}` | Check if favorited |
| POST | `/check/batch` | Batch check favorites |
| GET | `/stats/count` | Favorite count |

**Features**:
- Per-question notes
- Batch operations
- Quick favorite status checking

---

### 3.7 Wrong Questions (Error Tracking)
**File**: `v1/wrong_questions.py`
**Prefix**: `/api/v1/wrong-questions`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `` | List wrong questions |
| GET | `/{wrong_question_id}` | Get wrong question |
| PUT | `/{wrong_question_id}/correct` | Mark as corrected |
| DELETE | `/{wrong_question_id}` | Delete from list |
| DELETE | `/question/{question_id}` | Remove by question |
| GET | `/stats/overview` | Statistics overview |
| GET | `/stats/count` | Count summary |
| GET | `/analysis/{question_id}` | Analysis per question |
| POST | `/batch/correct` | Mark batch as corrected |
| POST | `/batch/delete` | Batch delete |

**Error Tracking Features**:
- Error count tracking
- Last error timestamp
- Corrected status
- Error analysis per question
- Difficulty-based filtering

---

### 3.8 Activation & Access Control
**File**: `v1/activation.py`
**Prefix**: `/api/v1/activation`

#### User Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/activate` | Activate with code |
| GET | `/my-access` | List user's access |
| GET | `/check-access/{bank_id}` | Check bank access |

#### Admin Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/admin/codes` | Create activation codes |
| GET | `/admin/codes` | List codes |
| DELETE | `/admin/codes/{code_id}` | Delete code |
| GET | `/admin/access` | List all access |
| PUT | `/admin/access/{access_id}/revoke` | Revoke access |

**Features**:
- Activation code generation
- Expiration date management
- Limited use codes (single/multiple use)
- Access revocation
- Time-based access control

---

### 3.9 LLM & AI Integration
**File**: `v1/llm.py`
**Prefix**: `/api/v1/llm`

#### Interface Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/interfaces` | List LLM interfaces |
| GET | `/interfaces/{interface_id}` | Get interface |
| POST | `/interfaces` | Create interface |
| PUT | `/interfaces/{interface_id}` | Update interface |
| DELETE | `/interfaces/{interface_id}` | Delete interface |
| POST | `/interfaces/{interface_id}/test` | Test interface |

#### Prompt Templates
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/templates` | List templates |
| GET | `/templates/presets` | Get preset templates |
| GET | `/templates/{template_id}` | Get template |
| POST | `/templates` | Create template |
| PUT | `/templates/{template_id}` | Update template |
| DELETE | `/templates/{template_id}` | Delete template |

#### AI Question Parsing
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/parse` | Parse questions with LLM |
| POST | `/import` | Batch import with parsing |

**Supported LLM Providers**:
- OpenAI
- Claude (Anthropic)
- Zhipu (Chinese LLM)

---

### 3.10 AI Chat Interface
**File**: `v1/ai_chat.py`
**Prefix**: `/api/v1/ai-chat`

#### AI Configuration
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/configs` | Create AI config |
| GET | `/configs` | List configs |
| GET | `/configs/{config_id}` | Get config |
| PUT | `/configs/{config_id}` | Update config |
| DELETE | `/configs/{config_id}` | Delete config |

#### Chat Sessions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/sessions` | Start chat session |
| GET | `/sessions` | List sessions |
| GET | `/sessions/{session_id}` | Get session |
| DELETE | `/sessions/{session_id}` | Close session |
| POST | `/sessions/{session_id}/messages` | Send message |
| GET | `/sessions/{session_id}/messages` | Get messages |
| POST | `/sessions/{session_id}/stream` | Stream response |

#### AI Usage
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/usage/{config_id}` | Get usage stats |
| GET | `/usage/report` | Generate usage report |

---

### 3.11 MCP (Model Context Protocol) Integration
**File**: `mcp/router.py`
**Prefix**: `/api/mcp`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tools` | List available tools |
| GET | `/tools/{tool_name}` | Get tool definition |
| POST | `/execute` | Execute single tool |
| POST | `/batch` | Execute multiple tools |
| GET | `/categories` | Tool categories |

**MCP Tools Available**:
- Question bank operations
- Practice session management
- Favorite management
- Wrong question tracking
- Statistics queries
- File uploads/downloads

**Format Support**:
- OpenAI function calling schema
- Claude native tool format

---

### 3.12 Admin & System Management (v2)
**File**: `v2/admin.py`
**Prefix**: `/api/v2`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | System health check |
| GET | `/` | API info |
| GET | `/stats/overview` | System overview |
| GET | `/stats/users` | User statistics |
| GET | `/stats/question-banks` | Bank statistics |
| GET | `/stats/questions` | Question statistics |

---

### 3.13 Exam & Practice (v2)
**File**: `v2/exams.py`
**Prefix**: `/api/v2/exams`

#### Exam Sessions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/sessions` | Create exam |
| GET | `/sessions` | List exams |
| GET | `/sessions/{session_id}` | Get exam details |

#### Practice Sessions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/practice` | Start practice |
| GET | `/practice` | List practices |

#### Submissions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/submissions` | Submit answers |
| GET | `/submissions/{session_id}` | Get submissions |

---

### 3.14 Import/Export (v2)
**File**: `v2/import_export.py`
**Prefix**: `/api/v2/import-export`

#### Import Operations
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/import/csv` | Import CSV |
| POST | `/import/json` | Import JSON |
| POST | `/import/zip` | Import ZIP bundle |

#### Export Operations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/export/{bank_id}/csv` | Export as CSV |
| GET | `/export/{bank_id}/json` | Export as JSON |
| GET | `/export/{bank_id}/zip` | Export as ZIP |

#### Templates
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/templates/csv` | CSV template |

---

## 4. Data Models & Schemas

### Core Models
- **User** (main.db): Authentication, roles, profiles
- **QuestionBank** (qbank.db): Bank metadata and structure
- **Question** (qbank.db): Question content and metadata
- **QuestionOption** (qbank.db): Multiple choice options
- **UserBankPermission** (main.db): Access control
- **ActivationCode** (qbank.db): Access code management
- **UserBankAccess** (qbank.db): Active access records

### Practice & Learning Models
- **PracticeSession**: Session tracking
- **UserAnswerRecord**: Individual answer tracking
- **UserFavorite**: Bookmarked questions
- **UserWrongQuestion**: Error tracking
- **UserDailyStatistics**: Daily summaries
- **UserBankStatistics**: Per-bank analytics

### AI Models
- **AIConfig**: LLM provider configuration
- **ChatSession**: Conversation history
- **ChatMessage**: Individual messages
- **LLMInterface**: LLM endpoint config
- **PromptTemplate**: Prompt templates

---

## 5. Authentication & Security

### Authentication Methods
- **OAuth2 with Password Flow** (Bearer tokens)
- **JWT Tokens** (configurable expiration, default 24 hours)
- **Session-based Admin Auth** (for dashboard)

### Authorization Levels
1. **Admin**: Full system access
2. **Teacher**: Bank creation, student management
3. **Student**: Practice, learning features
4. **Anonymous**: Public question banks only

### Permission Model
- Bank-level permissions (read, write, admin)
- User bank access via activation codes
- Expiring access tokens with renewal capability

---

## 6. Error Handling & Status Codes

| Code | Status | Common Causes |
|------|--------|---------------|
| 200 | OK | Successful request |
| 201 | Created | Resource creation success |
| 400 | Bad Request | Invalid input, validation failure |
| 401 | Unauthorized | Missing/invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource, constraint violation |
| 413 | Payload Too Large | File exceeds size limit |
| 500 | Server Error | Internal server error |

---

## 7. Pagination & Filtering

### Pagination Parameters
```
skip: int (default: 0) - Records to skip
limit: int (default: 20-100) - Records to return
```

### Common Filters
```
category: string - Filter by category
search: string - Full-text search
difficulty: string - Easy, Medium, Hard
type: string - Question type
is_public: boolean - Public/private filter
```

---

## 8. Response Formats

### Success Response (List)
```json
[
  {
    "id": "uuid-string",
    "name": "string",
    "created_at": "2025-01-01T00:00:00Z",
    ...
  }
]
```

### Success Response (Single)
```json
{
  "id": "uuid-string",
  "name": "string",
  "created_at": "2025-01-01T00:00:00Z",
  ...
}
```

### Error Response
```json
{
  "detail": "Error message",
  "error_code": "ERROR_TYPE"
}
```

---

## 9. Configuration & Deployment

### Environment Variables
- `APP_NAME`: Application name
- `APP_VERSION`: Version string
- `SECRET_KEY`: Django-style secret
- `JWT_SECRET_KEY`: JWT signing key
- `DATABASE_URL`: Main database path
- `QUESTION_BANK_DATABASE_URL`: QBank database path
- `CORS_ORIGINS`: Allowed origins
- `DEBUG`: Debug mode

### Database Structure
- **main.db**: Users, permissions, configurations
- **question_bank.db**: Questions, banks, statistics

### Storage Locations
- `./storage/uploads/`: User uploads
- `./storage/resources/`: Question resources
- `./storage/question_banks/`: Bank exports

---

## 10. API Access Patterns

### Base URLs
```
v1 API:  http://localhost:8000/api/v1
v2 API:  http://localhost:8000/api/v2
MCP API: http://localhost:8000/api/mcp
Docs:    http://localhost:8000/api/docs
```

### Common Headers
```
Authorization: Bearer {jwt_token}
Content-Type: application/json
Accept: application/json
```

### Example: Create Practice Session
```http
POST /api/v1/practice/sessions
Authorization: Bearer {token}
Content-Type: application/json

{
  "bank_id": "bank-uuid",
  "mode": "random",
  "question_types": ["single", "multiple"],
  "difficulty": "medium"
}
```

---

## 11. Statistics & Monitoring

### Available Metrics
- Daily study statistics
- Bank-specific performance
- Question difficulty analysis
- User engagement metrics
- Error patterns
- Time-on-task analysis
- Accuracy rates
- Learning streaks

### Export Capabilities
- CSV export (questions, results)
- JSON export (complete bank data)
- ZIP export (batch operations)
- Statistics reports

---

## 12. Advanced Features

### AI Integration
- LLM-powered question parsing
- Conversational practice assistant
- Auto-grading with AI
- Explanation generation
- Adaptive learning paths

### Batch Operations
- Bulk question import
- Batch answer submission
- Multi-bank management
- Bulk access provisioning

### Analytics
- User performance analytics
- Learning path optimization
- Content difficulty calibration
- Engagement tracking
- Knowledge gap identification

---

## 13. API Consistency Standards

### Naming Conventions
- **URLs**: kebab-case (`/wrong-questions`)
- **JSON Fields**: snake_case (`user_id`, `bank_id`)
- **Prefix Pattern**: `/api/{version}/{resource}`

### Pagination
- Always support `skip` and `limit`
- Default limits 20-100 records
- Total count available

### Timestamps
- ISO 8601 format with timezone
- Stored in UTC
- Field names: `created_at`, `updated_at`, `deleted_at`

---

## 14. Documentation Access

### Interactive API Docs
- **Swagger UI**: `/api/docs`
- **ReDoc**: `/api/redoc`
- **OpenAPI JSON**: `/openapi.json`

### Admin Panel
- **Dashboard**: `/admin`
- **Management**: Full user/bank/stat management
- **Configuration**: LLM, templates, activation codes

---

## Summary Statistics

| Category | Count |
|----------|-------|
| Total API Files | 26 |
| API v1 Endpoints | 80+ |
| API v2 Endpoints | 15+ |
| MCP Tools | 5+ |
| Model Classes | 20+ |
| Database Tables | 25+ |
| Authentication Methods | 2 |
| Supported File Formats | 7+ |
| User Roles | 3 |

---

## Quick Reference: Most Important Endpoints

### User Journey
1. `POST /auth/register` - Create account
2. `POST /auth/login` - Get JWT token
3. `POST /activation/activate` - Access question bank
4. `GET /qbank/banks` - List accessible banks
5. `POST /practice/sessions` - Start practice
6. `POST /practice/sessions/{id}/submit` - Submit answer
7. `GET /statistics/overview` - View progress

### Admin Tasks
1. `GET /stats/overview` - System status
2. `POST /users` - Create user
3. `POST /activation/admin/codes` - Generate access codes
4. `GET /qbank/banks` - Manage banks
5. `POST /llm/interfaces` - Configure LLM

