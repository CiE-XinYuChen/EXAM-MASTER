# EXAM-MASTER Complete API Endpoints Reference

## API v1 Complete Endpoint List

### Authentication Module (`/api/v1/auth`)
```
POST   /login                      - User login (username/email + password)
POST   /register                   - Register new user
POST   /change-password            - Change user password (requires auth)
GET    /me                         - Get current user profile (requires auth)
POST   /logout                     - Logout current user (requires auth)
```

### User Management Module (`/api/v1/users`)
```
GET    /                           - List all users (admin only)
GET    /{user_id}                  - Get user by ID (admin only)
PUT    /{user_id}                  - Update user (admin only)
DELETE /{user_id}                  - Delete user (admin only)
GET    /{user_id}/permissions      - Get user bank permissions (admin only)
POST   /{user_id}/permissions      - Grant bank permission (admin only)
DELETE /{user_id}/permissions/{bank_id} - Revoke permission (admin only)
```

### Question Bank Management - Banks (`/api/v1/qbank/banks`)
```
GET    /                           - List accessible question banks
POST   /                           - Create new question bank
GET    /{bank_id}                  - Get bank details by ID
PUT    /{bank_id}                  - Update bank details
DELETE /{bank_id}                  - Delete bank
POST   /{bank_id}/clone            - Clone entire bank
```

### Question Bank Management - Questions (`/api/v1/qbank/questions`)
```
GET    /                           - List questions with filters
POST   /                           - Create new question
GET    /{question_id}              - Get question details
PUT    /{question_id}              - Update question
DELETE /{question_id}              - Delete question
POST   /{question_id}/options      - Add option to question
POST   /{question_id}/duplicate    - Duplicate question
```

### Question Bank Management - Options (`/api/v1/qbank/options`)
```
GET    /{option_id}                - Get option details
PUT    /{option_id}                - Update option
DELETE /{option_id}                - Delete option
POST   /{option_id}/reorder        - Reorder options for question
POST   /batch-update               - Batch update multiple options
```

### Question Bank Management - Resources (`/api/v1/qbank/resources`)
```
POST   /upload                     - Upload single resource file
POST   /batch-upload               - Batch upload multiple files
GET    /{resource_id}              - Get resource metadata
GET    /{resource_id}/download     - Download resource file
DELETE /{resource_id}              - Delete resource
```

### Import/Export Module (`/api/v1/qbank/import`)
```
POST   /csv                        - Import questions from CSV file
POST   /json                       - Import bank from JSON file
POST   /validate                   - Validate import format before importing
GET    /export/{bank_id}           - Export bank as downloadable file
```

### Question Bank API v2 (`/api/v1/qbank`)
```
POST   /banks                      - Create new bank (v2)
GET    /banks                      - List banks (v2)
GET    /banks/{bank_id}            - Get bank details (v2)
PUT    /banks/{bank_id}            - Update bank (v2)
DELETE /banks/{bank_id}            - Delete bank (v2)
POST   /banks/{bank_id}/questions  - Add question to bank
GET    /banks/{bank_id}/questions  - List questions in bank
GET    /questions/{question_id}    - Get question details
PUT    /questions/{question_id}    - Update question
DELETE /questions/{question_id}    - Delete question
POST   /questions/{question_id}/images - Upload question image
GET    /resources/{resource_id}    - Get resource details
POST   /banks/{bank_id}/export     - Export bank with questions
POST   /import                     - Import questions/banks
POST   /banks/{bank_id}/duplicate  - Duplicate entire bank
GET    /banks/{bank_id}/stats      - Get bank statistics
GET    /categories                 - List all categories
GET    /search                     - Full-text search questions
GET    /stats/users                - User statistics
GET    /stats/banks                - Bank statistics
GET    /stats/questions            - Question statistics
```

### Practice & Learning Sessions (`/api/v1/practice`)
```
POST   /sessions                   - Create new practice session
GET    /sessions                   - List user's practice sessions
GET    /sessions/{session_id}      - Get session details
PUT    /sessions/{session_id}      - Update session (pause/resume)
DELETE /sessions/{session_id}      - End/delete session
POST   /sessions/{session_id}/submit - Submit answer for current question
GET    /sessions/{session_id}/current - Get current question in session
GET    /sessions/{session_id}/statistics - Get session statistics
GET    /history                    - Get complete answer history
```

### Statistics & Analytics (`/api/v1/statistics`)
```
GET    /daily                      - Daily practice statistics
GET    /bank/{bank_id}             - Statistics for specific bank
GET    /banks                      - Statistics for all banks
GET    /overview                   - Overall user statistics overview
GET    /detailed                   - Detailed analytics breakdown
```

### Favorites Management (`/api/v1/favorites`)
```
POST   /                           - Add question to favorites
GET    /                           - List all favorite questions
GET    /{favorite_id}              - Get favorite details
PUT    /{favorite_id}              - Update favorite (edit notes)
DELETE /{favorite_id}              - Remove from favorites by ID
DELETE /question/{question_id}     - Remove from favorites by question
GET    /check/{question_id}        - Check if question is favorited
POST   /check/batch                - Batch check favorites status
GET    /stats/count                - Get total favorite count
```

### Wrong Questions/Error Tracking (`/api/v1/wrong-questions`)
```
GET    /                           - List all wrong questions
GET    /{wrong_question_id}        - Get wrong question details
PUT    /{wrong_question_id}/correct - Mark question as corrected
DELETE /{wrong_question_id}        - Remove from wrong questions
DELETE /question/{question_id}     - Remove by question ID
GET    /stats/overview             - Error statistics overview
GET    /stats/count                - Get wrong question count
GET    /analysis/{question_id}     - Analyze errors for question
POST   /batch/correct              - Mark multiple as corrected
DELETE /batch/delete               - Delete multiple at once
```

### Activation & Access Control (`/api/v1/activation`)
```
POST   /activate                   - Activate bank with code
GET    /my-access                  - List user's active access
GET    /check-access/{bank_id}     - Check access to specific bank
POST   /admin/codes                - Generate activation codes (admin)
GET    /admin/codes                - List activation codes (admin)
DELETE /admin/codes/{code_id}      - Delete activation code (admin)
GET    /admin/access               - List all user access records (admin)
PUT    /admin/access/{access_id}/revoke - Revoke user access (admin)
```

### LLM & AI Integration (`/api/v1/llm`)
```
GET    /interfaces                 - List LLM interface configs
GET    /interfaces/{interface_id}  - Get interface details
POST   /interfaces                 - Create new LLM interface
PUT    /interfaces/{interface_id}  - Update interface config
DELETE /interfaces/{interface_id}  - Delete interface
POST   /interfaces/{interface_id}/test - Test interface connection
GET    /templates                  - List prompt templates
GET    /templates/presets          - Get preset templates
GET    /templates/{template_id}    - Get template details
POST   /templates                  - Create new template
PUT    /templates/{template_id}    - Update template
DELETE /templates/{template_id}    - Delete template
POST   /parse                      - Parse questions using LLM
POST   /import                     - Batch import with LLM parsing
```

### AI Chat Interface (`/api/v1/ai-chat`)
```
POST   /configs                    - Create AI configuration
GET    /configs                    - List AI configs
GET    /configs/{config_id}        - Get config details
PUT    /configs/{config_id}        - Update config
DELETE /configs/{config_id}        - Delete config
POST   /sessions                   - Create chat session
GET    /sessions                   - List chat sessions
GET    /sessions/{session_id}      - Get session details
DELETE /sessions/{session_id}      - Close chat session
POST   /sessions/{session_id}/messages - Send message
GET    /sessions/{session_id}/messages - Get message history
POST   /sessions/{session_id}/stream - Stream response
GET    /usage/{config_id}          - Get usage statistics
GET    /usage/report               - Generate usage report
```

---

## API v2 Endpoints

### System Administration (`/api/v2/`)
```
GET    /health                     - Health check
GET    /                           - API info
GET    /stats/overview             - System overview
GET    /stats/users                - User statistics
GET    /stats/question-banks       - Bank statistics
GET    /stats/questions            - Question statistics
```

### Exams & Practice Sessions (`/api/v2/exams`)
```
POST   /sessions                   - Create exam session
GET    /sessions                   - List exam sessions
GET    /sessions/{session_id}      - Get exam session details
POST   /practice                   - Create practice session
GET    /practice                   - List practice sessions
POST   /submissions                - Submit answers
GET    /submissions/{session_id}   - Get submissions
```

### Import/Export Operations (`/api/v2/import-export`)
```
POST   /import/csv                 - Import from CSV
POST   /import/json                - Import from JSON
POST   /import/zip                 - Import from ZIP
GET    /export/{bank_id}/csv       - Export as CSV
GET    /export/{bank_id}/json      - Export as JSON
GET    /export/{bank_id}/zip       - Export as ZIP
GET    /templates/csv              - Get CSV template
```

---

## MCP (Model Context Protocol) Integration

### MCP Tools & Services (`/api/mcp/`)
```
GET    /tools                      - List available MCP tools
GET    /tools/{tool_name}          - Get specific tool definition
POST   /execute                    - Execute single tool
POST   /batch                      - Execute multiple tools
GET    /categories                 - Get tool categories
```

---

## Query Parameters Reference

### Pagination Parameters (Most Endpoints)
```
skip: int              - Number of records to skip (default: 0)
limit: int             - Maximum records to return (default: 20-100)
```

### Filter Parameters (Question Endpoints)
```
bank_id: string        - Filter by question bank ID
type: string           - Question type (single, multiple, essay, etc.)
difficulty: string     - Difficulty level (easy, medium, hard)
category: string       - Question category
tags: string           - Tag filter
search: string         - Full-text search in question stem
is_public: boolean     - Filter by public/private
```

### Sort Parameters
```
sort_by: string        - Field to sort by
order: string          - Sort order (asc, desc)
```

### Practice Specific
```
mode: string           - Practice mode (sequential, random, wrong_only, favorite_only)
question_types: array  - Question types to include
difficulty: string     - Difficulty filter
```

### Statistics Specific
```
start_date: date       - Statistics start date
end_date: date         - Statistics end date
period: string         - Period (daily, weekly, monthly)
```

---

## Request/Response Examples

### Example 1: User Registration
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "student1",
  "email": "student1@example.com",
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!"
}

Response (201):
{
  "id": 1,
  "username": "student1",
  "email": "student1@example.com",
  "role": "student",
  "is_active": true,
  "created_at": "2025-01-01T12:00:00Z"
}
```

### Example 2: Create Practice Session
```http
POST /api/v1/practice/sessions
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "bank_id": "550e8400-e29b-41d4-a716-446655440000",
  "mode": "random",
  "question_types": ["single_choice", "multiple_choice"],
  "difficulty": "medium"
}

Response (201):
{
  "id": "session-uuid",
  "user_id": 1,
  "bank_id": "550e8400-e29b-41d4-a716-446655440000",
  "mode": "random",
  "status": "in_progress",
  "total_questions": 50,
  "current_question_index": 0,
  "created_at": "2025-01-01T12:00:00Z"
}
```

### Example 3: Submit Answer
```http
POST /api/v1/practice/sessions/{session_id}/submit
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "question_id": "q-uuid",
  "selected_options": ["A", "B"],
  "time_spent_seconds": 45
}

Response (200):
{
  "is_correct": true,
  "selected_options": ["A", "B"],
  "correct_options": ["A", "B"],
  "explanation": "Both options A and B are correct because...",
  "points_earned": 10
}
```

### Example 4: List Favorites
```http
GET /api/v1/favorites?skip=0&limit=20
Authorization: Bearer {jwt_token}

Response (200):
{
  "total": 45,
  "items": [
    {
      "id": "fav-uuid",
      "question_id": "q-uuid",
      "bank_id": "b-uuid",
      "note": "Review this later",
      "created_at": "2025-01-01T12:00:00Z"
    }
  ],
  "skip": 0,
  "limit": 20
}
```

### Example 5: Upload Resource
```http
POST /api/v1/qbank/resources/upload
Authorization: Bearer {jwt_token}
Content-Type: multipart/form-data

file: [binary file content]
question_id: "q-uuid"
resource_type: "image"

Response (201):
{
  "id": "resource-uuid",
  "question_id": "q-uuid",
  "file_name": "question_image.png",
  "file_size": 245000,
  "file_type": "image",
  "url": "/storage/resources/resource-uuid.png",
  "created_at": "2025-01-01T12:00:00Z"
}
```

---

## HTTP Status Codes Summary

```
200 OK                      - Successful GET, PUT
201 Created                 - Successful POST creating resource
204 No Content              - Successful DELETE
400 Bad Request             - Invalid input/validation error
401 Unauthorized            - Missing/invalid authentication
403 Forbidden               - Insufficient permissions
404 Not Found               - Resource doesn't exist
409 Conflict                - Duplicate/constraint violation
413 Payload Too Large       - File exceeds size limit
422 Unprocessable Entity    - Validation failure details
500 Internal Server Error   - Server error
```

---

## Authentication Headers

All authenticated endpoints require:
```
Authorization: Bearer {jwt_token}
```

Token obtained from:
```
POST /api/v1/auth/login
```

---

## CORS & Content-Type

All requests should include:
```
Content-Type: application/json
Accept: application/json
```

CORS is enabled for configured origins (see config).

---

## Rate Limiting (if implemented)

Future rate limiting headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1609459200
```

---

## File Upload Constraints

### Image Files
- Max size: 10 MB
- Formats: .jpg, .jpeg, .png, .gif, .svg, .webp, .bmp

### Video Files
- Max size: 100 MB
- Formats: .mp4, .webm, .avi, .mov, .mkv

### Audio Files
- Max size: 20 MB
- Formats: .mp3, .wav, .ogg, .m4a, .flac

### Document Files
- Max size: 20 MB
- Formats: .pdf, .doc, .docx, .txt, .tex, .md

### Data Import Files
- CSV: < 50 MB, UTF-8 encoded
- JSON: < 50 MB, valid JSON structure
- ZIP: < 200 MB, valid archive

