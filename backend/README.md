# EXAM-MASTER Backend API

A modern question bank management system built with FastAPI with integrated admin panel.

## Features

- 🔐 JWT Authentication with role-based access control
- 👥 User management (Admin, Teacher, Student roles)
- 📚 Multi-question bank management
- ❓ Dynamic question options (not limited to ABCD)
- 📁 File upload and resource management
- 📊 Statistics and analytics
- 🔄 Import/Export support (CSV, JSON, Markdown, etc.)
- 🎯 Multiple quiz modes (practice, exam, timed)

## Tech Stack

- **Framework**: FastAPI
- **Database**: Dual SQLite architecture (Main DB + Question Bank DB)
- **Authentication**: JWT tokens
- **ORM**: SQLAlchemy
- **Validation**: Pydantic

## Project Structure

```
backend/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── core/            # Core configuration
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   └── utils/           # Utilities
├── databases/           # SQLite databases
├── storage/            # File storage
│   ├── question_banks/  # Question bank files
│   ├── resources/       # Media resources
│   └── uploads/         # Temporary uploads
└── requirements.txt
```

## Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the application:
```bash
python run.py
```

The API will be available at `http://localhost:8000`

## Access Points

- Admin Panel: `http://localhost:8000/admin`
- API Documentation: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

## Default Admin Account

After running the application, create an admin account:

```bash
python init_admin.py
```

Default credentials:
- Username: admin
- Password: admin123

## Database Architecture

### Main Database (main.db)
- User management
- Authentication
- Permissions
- Answer history
- Exam sessions

### Question Bank Database (question_bank.db)
- Question banks
- Questions
- Dynamic options
- Resources
- Version history

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/me` - Get current user

### Users
- `GET /api/v1/users` - List users (admin)
- `GET /api/v1/users/{id}` - Get user details
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

### Question Banks
- `GET /api/v1/qbank/banks` - List question banks
- `POST /api/v1/qbank/banks` - Create question bank
- `GET /api/v1/qbank/banks/{id}` - Get bank details
- `PUT /api/v1/qbank/banks/{id}` - Update bank
- `DELETE /api/v1/qbank/banks/{id}` - Delete bank

### Questions
- `GET /api/v1/qbank/questions` - List questions
- `POST /api/v1/qbank/questions` - Create question
- `GET /api/v1/qbank/questions/{id}` - Get question
- `PUT /api/v1/qbank/questions/{id}` - Update question
- `DELETE /api/v1/qbank/questions/{id}` - Delete question

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black app/
```

### Linting
```bash
flake8 app/
```

## License

MIT