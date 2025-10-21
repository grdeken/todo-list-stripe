# FastAPI Todo List Microservice

A production-ready, optimally designed FastAPI microservice for managing todo lists with JWT authentication, following modern API design best practices.

## Features

### API Design Excellence
- **RESTful API** with proper HTTP verbs and status codes
- **API Versioning** (`/api/v1/`) for backward compatibility
- **JWT Authentication** (stateless, scalable)
- **Pydantic V2** for request/response validation
- **SQLAlchemy 2.0** async ORM with modern patterns
- **Dependency Injection** for clean, testable code
- **Comprehensive Error Handling** with meaningful messages
- **Automatic OpenAPI/Swagger** documentation
- **CORS Configuration** for frontend integration

### Architecture Highlights
- **Async/Await** throughout for high performance
- **Repository Pattern** via SQLAlchemy models
- **Separation of Concerns** (models, schemas, endpoints, services)
- **Type Safety** with modern Python type hints
- **Proper Data Validation** at API boundaries
- **Database Session Management** with proper lifecycle
- **Security Best Practices** (password hashing, token validation)

## Project Structure

```
fastapi-backend/
├── src/
│   └── api_service/
│       ├── api/
│       │   ├── deps.py              # Dependency injection (auth, db)
│       │   └── v1/
│       │       ├── endpoints/
│       │       │   ├── auth.py      # Authentication endpoints
│       │       │   ├── todo_lists.py # TodoList CRUD
│       │       │   └── todos.py     # Todo CRUD
│       │       └── router.py        # API v1 router
│       ├── core/
│       │   ├── config.py           # Settings (Pydantic Settings)
│       │   └── security.py         # JWT & password hashing
│       ├── db/
│       │   └── base.py             # Database session & base
│       ├── models/
│       │   ├── user.py             # User model
│       │   └── todo.py             # TodoList & Todo models
│       ├── schemas/
│       │   ├── user.py             # User Pydantic schemas
│       │   └── todo.py             # Todo Pydantic schemas
│       └── main.py                 # FastAPI application
├── tests/
│   ├── conftest.py                 # Pytest fixtures
│   ├── test_auth.py                # Authentication tests
│   └── test_todos.py               # Todo tests
├── pyproject.toml                  # Dependencies & tooling
├── .env.example                    # Environment variables template
└── README.md
```

## Installation

### Prerequisites
- Python 3.11+
- pip or uv (recommended)

### Setup

```bash
# Clone or navigate to the project
cd fastapi-backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Install dev dependencies
pip install -e ".[dev]"

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
```

## Running the Application

### Development Server

```bash
# Using uvicorn directly
uvicorn api_service.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python module
python -m uvicorn api_service.main:app --reload
```

The API will be available at:
- API: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI spec: `http://localhost:8000/api/v1/openapi.json`

### Production Server

```bash
# Using uvicorn with production settings
uvicorn api_service.main:app --host 0.0.0.0 --port 8000 --workers 4

# Or using gunicorn with uvicorn workers
gunicorn api_service.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## API Endpoints

### Authentication (`/api/v1/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register` | Register new user | No |
| POST | `/login` | Login (OAuth2 form) | No |
| POST | `/login-json` | Login (JSON) | No |
| GET | `/me` | Get current user | Yes |
| POST | `/logout` | Logout user | Yes |

### Todo Lists (`/api/v1/todo-lists`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Get all todo lists | Yes |
| POST | `/` | Create todo list | Yes |
| GET | `/{id}` | Get todo list by ID | Yes |
| PATCH | `/{id}` | Update todo list | Yes |
| DELETE | `/{id}` | Delete todo list | Yes |

### Todos (`/api/v1/todos`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Get all todos | Yes |
| POST | `/` | Create todo | Yes |
| GET | `/{id}` | Get todo by ID | Yes |
| PATCH | `/{id}` | Update todo | Yes |
| POST | `/{id}/toggle` | Toggle completion | Yes |
| DELETE | `/{id}` | Delete todo | Yes |

## API Usage Examples

### Register User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepassword123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "is_active": true,
    "created_at": "2025-10-20T10:00:00",
    "updated_at": "2025-10-20T10:00:00"
  }
}
```

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### Create Todo List

```bash
curl -X POST "http://localhost:8000/api/v1/todo-lists/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Shopping List"}'
```

### Create Todo

```bash
curl -X POST "http://localhost:8000/api/v1/todos/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Buy groceries",
    "complete": false,
    "due_date": "2025-10-21",
    "todo_list_id": 1
  }'
```

### Toggle Todo Completion

```bash
curl -X POST "http://localhost:8000/api/v1/todos/1/toggle" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=api_service --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v

# Run specific test
pytest tests/test_auth.py::test_register_user -v
```

## Database

### SQLite (Default - Development)
The application uses SQLite by default for easy local development. The database file `todos.db` is created automatically on first run.

### PostgreSQL (Production)

1. Install PostgreSQL and create a database:
```bash
createdb todolist_db
```

2. Update `.env`:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/todolist_db
```

3. Install PostgreSQL driver:
```bash
pip install asyncpg
```

### Database Migrations (Optional - Alembic)

If you need migrations:

```bash
# Initialize Alembic
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

## Configuration

Environment variables (`.env`):

```env
# Application
PROJECT_NAME="FastAPI Todo List API"
VERSION="0.1.0"
DEBUG=False
API_V1_PREFIX="/api/v1"

# CORS
ALLOWED_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
CORS_ALLOW_CREDENTIALS=True

# Database
DATABASE_URL="sqlite+aiosqlite:///./todos.db"
# DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/todolist_db"

# Security
SECRET_KEY="your-secret-key-change-in-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Comparison with Django REST Framework

### Advantages of FastAPI Version

1. **Performance**: Async/await throughout = 3-5x faster
2. **Type Safety**: Full Pydantic validation + Python type hints
3. **Modern Python**: Uses Python 3.11+ features
4. **Auto Documentation**: OpenAPI/Swagger built-in
5. **Stateless**: JWT tokens (no database sessions)
6. **Lightweight**: Minimal dependencies
7. **Developer Experience**: Better IDE support with types
8. **Async Native**: Built for async from the ground up

### API Design Improvements

1. **Proper Versioning**: `/api/v1/` prefix for future compatibility
2. **RESTful Standards**: Correct HTTP methods and status codes
3. **Dependency Injection**: Clean separation of concerns
4. **Request/Response Schemas**: Explicit validation
5. **Error Handling**: Consistent error responses
6. **Security**: Modern JWT implementation
7. **Testing**: Async test fixtures
8. **Documentation**: Auto-generated interactive docs

## Migration from Django

### Key Differences

| Feature | Django | FastAPI |
|---------|--------|---------|
| Authentication | Token in DB | JWT (stateless) |
| ORM | Django ORM (sync) | SQLAlchemy 2.0 (async) |
| Validation | Serializers | Pydantic schemas |
| Routing | Class-based views | Function decorators |
| Performance | Sync by default | Async by default |
| Type Safety | Limited | Full type hints |

### Migration Steps

1. **Update Frontend API Client**: Change base URL and token handling
2. **Update Authentication**: JWT tokens instead of session tokens
3. **Update Endpoints**: Minor path changes (see API docs)
4. **Data Migration**: Export Django data, import to new DB

### Frontend Changes Required

```javascript
// Old Django endpoint
const response = await fetch('http://localhost:8000/api/todos/', {
  headers: { 'Authorization': `Token ${token}` }
});

// New FastAPI endpoint
const response = await fetch('http://localhost:8000/api/v1/todos/', {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

## Development

### Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type checking
mypy src/
```

### Adding New Features

1. Create model in `models/`
2. Create Pydantic schemas in `schemas/`
3. Create endpoints in `api/v1/endpoints/`
4. Register router in `api/v1/router.py`
5. Write tests in `tests/`

## Deployment

### Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install -e .

COPY src/ ./src/

CMD ["uvicorn", "api_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t fastapi-todo .
docker run -p 8000:8000 --env-file .env fastapi-todo
```

### Production Checklist

- [ ] Change `SECRET_KEY` to a secure random value
- [ ] Set `DEBUG=False`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up monitoring and logging
- [ ] Use environment variables for secrets
- [ ] Run with multiple workers (gunicorn/uvicorn)
- [ ] Set up database backups
- [ ] Configure rate limiting

## Contributing

1. Follow PEP 8 and use type hints
2. Write tests for new features
3. Update documentation
4. Run linting and formatting before committing

## License

MIT License

## Support

For issues and questions, see the FastAPI documentation: https://fastapi.tiangolo.com/
