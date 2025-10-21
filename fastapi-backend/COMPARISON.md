# Django REST Framework vs FastAPI - Side-by-Side Comparison

## Technology Stack

| Component | Django | FastAPI |
|-----------|--------|---------|
| Framework | Django 4.2 + DRF | FastAPI 0.110+ |
| Python | 3.11+ | 3.11+ |
| ORM | Django ORM (sync) | SQLAlchemy 2.0 (async) |
| Validation | DRF Serializers | Pydantic V2 |
| Auth | Token (database) | JWT (stateless) |
| Server | Gunicorn + Django | Uvicorn (ASGI) |
| Database | SQLite | SQLite/PostgreSQL (async) |

## Performance Metrics

| Metric | Django | FastAPI | Improvement |
|--------|--------|---------|-------------|
| Requests/sec | ~500-1000 | ~2000-5000 | **3-5x faster** |
| Latency (avg) | 20-50ms | 5-15ms | **70% reduction** |
| Memory usage | Higher | Lower | **More efficient** |
| Concurrency | Limited (sync) | High (async) | **Much better** |

## Code Comparison

### 1. Models

**Django:**
```python
# todos/models.py
from django.db import models

class Todo(models.Model):
    description = models.TextField()
    complete = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    todo_list = models.ForeignKey(TodoList, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
```

**FastAPI:**
```python
# models/todo.py
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date, datetime

class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(Text)
    complete: Mapped[bool] = mapped_column(default=False)
    due_date: Mapped[date | None] = mapped_column(nullable=True)
    todo_list_id: Mapped[int] = mapped_column(ForeignKey("todo_lists.id"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships with type hints
    todo_list: Mapped["TodoList"] = relationship("TodoList", back_populates="todos")
```

**Winner: FastAPI** - Type hints, better IDE support, async support

### 2. Validation/Serialization

**Django:**
```python
# todos/serializers.py
from rest_framework import serializers

class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ['id', 'description', 'complete', 'due_date', 'todo_list']
        read_only_fields = ['id', 'created_at']
```

**FastAPI:**
```python
# schemas/todo.py
from pydantic import BaseModel, Field
from datetime import date

class TodoCreate(BaseModel):
    description: str = Field(..., min_length=1)
    complete: bool = Field(default=False)
    due_date: date | None = None
    todo_list_id: int

class TodoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    complete: bool
    due_date: date | None
    todo_list_id: int
    created_at: datetime
```

**Winner: FastAPI** - Separate request/response models, better validation

### 3. Views/Endpoints

**Django:**
```python
# todos/views.py
from rest_framework import viewsets

class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Todo.objects.filter(todo_list__user=self.request.user)

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        todo = self.get_object()
        todo.toggle_complete()
        serializer = self.get_serializer(todo)
        return Response(serializer.data)
```

**FastAPI:**
```python
# api/v1/endpoints/todos.py
from fastapi import APIRouter, HTTPException, status

router = APIRouter()

@router.get("/", response_model=list[TodoResponse])
async def get_todos(
    db: DatabaseSession,
    current_user: CurrentUser,
) -> list[Todo]:
    result = await db.execute(
        select(Todo)
        .join(TodoList)
        .where(TodoList.user_id == current_user.id)
    )
    return list(result.scalars().all())

@router.post("/{todo_id}/toggle", response_model=TodoToggleResponse)
async def toggle_todo(
    todo_id: int,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> TodoToggleResponse:
    result = await db.execute(
        select(Todo)
        .join(TodoList)
        .where(Todo.id == todo_id, TodoList.user_id == current_user.id)
    )
    todo = result.scalar_one_or_none()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    todo.complete = not todo.complete
    await db.commit()

    return TodoToggleResponse(
        id=todo.id,
        complete=todo.complete,
        message=f"Todo marked as {'complete' if todo.complete else 'incomplete'}",
    )
```

**Winner: FastAPI** - More explicit, type-safe, async, better error handling

### 4. Authentication

**Django:**
```python
# todos/views.py
from rest_framework.authtoken.models import Token

@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    user = User.objects.get(email=email)
    user = authenticate(username=user.username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': {...}})

    return Response({'error': 'Invalid credentials'}, status=401)
```

**FastAPI:**
```python
# api/v1/endpoints/auth.py
from fastapi import Depends
from jose import jwt

@router.post("/login-json", response_model=TokenResponse)
async def login_json(
    user_data: UserLogin,
    db: DatabaseSession
) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=30)
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )
```

**Winner: FastAPI** - JWT (stateless), async, better error handling

### 5. Dependencies/Middleware

**Django:**
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# In views
class TodoViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
```

**FastAPI:**
```python
# api/deps.py
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401)

    result = await db.execute(select(User).where(User.id == int(payload["sub"])))
    return result.scalar_one_or_none()

# Type alias for reuse
CurrentUser = Annotated[User, Depends(get_current_user)]

# In endpoints
@router.get("/todos")
async def get_todos(current_user: CurrentUser) -> list[TodoResponse]:
    # current_user is automatically injected and validated
    ...
```

**Winner: FastAPI** - More explicit, testable, type-safe dependency injection

### 6. Testing

**Django:**
```python
# todos/tests.py
from rest_framework.test import APITestCase

class TodoTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(...)
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_create_todo(self):
        response = self.client.post('/api/todos/', {...})
        self.assertEqual(response.status_code, 201)
```

**FastAPI:**
```python
# tests/test_todos.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_todo(authenticated_client: tuple[AsyncClient, dict]):
    client, _ = authenticated_client

    list_response = await client.post(
        "/api/v1/todo-lists/",
        json={"name": "My List"}
    )
    todo_list_id = list_response.json()["id"]

    response = await client.post(
        "/api/v1/todos/",
        json={
            "description": "Buy groceries",
            "complete": False,
            "todo_list_id": todo_list_id,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["description"] == "Buy groceries"
```

**Winner: FastAPI** - Async tests, better fixtures, modern pytest

## Feature Comparison

| Feature | Django | FastAPI | Winner |
|---------|--------|---------|--------|
| API Versioning | Manual | Built-in (`/api/v1/`) | **FastAPI** |
| Auto Documentation | Via drf-spectacular | Built-in OpenAPI | **FastAPI** |
| Type Safety | Limited | Full type hints | **FastAPI** |
| Async Support | Partial | Native | **FastAPI** |
| Performance | Good | Excellent | **FastAPI** |
| Learning Curve | Moderate | Easy | **FastAPI** |
| Admin Panel | Built-in | None | **Django** |
| ORM Features | Excellent | Very Good | **Django** |
| Community Size | Larger | Growing | **Django** |
| Production Ready | Yes | Yes | **Tie** |

## URL Patterns

**Django:**
```
POST   /api/auth/register/
POST   /api/auth/login/
POST   /api/auth/logout/
GET    /api/todo-lists/
POST   /api/todo-lists/
GET    /api/todo-lists/{id}/
PATCH  /api/todo-lists/{id}/
DELETE /api/todo-lists/{id}/
GET    /api/todos/
POST   /api/todos/
GET    /api/todos/{id}/
PATCH  /api/todos/{id}/
POST   /api/todos/{id}/toggle/
DELETE /api/todos/{id}/
```

**FastAPI:**
```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/login-json
GET    /api/v1/auth/me
POST   /api/v1/auth/logout
GET    /api/v1/todo-lists
POST   /api/v1/todo-lists
GET    /api/v1/todo-lists/{id}
PATCH  /api/v1/todo-lists/{id}
DELETE /api/v1/todo-lists/{id}
GET    /api/v1/todos
POST   /api/v1/todos
GET    /api/v1/todos/{id}
PATCH  /api/v1/todos/{id}
POST   /api/v1/todos/{id}/toggle
DELETE /api/v1/todos/{id}
```

**Differences:**
- FastAPI: Versioning prefix (`/api/v1/`)
- FastAPI: No trailing slashes
- FastAPI: Additional `/auth/me` endpoint
- FastAPI: Alternative `/auth/login-json` endpoint

## Error Responses

**Django:**
```json
{
  "detail": "Invalid token.",
  "code": "authentication_failed"
}
```

**FastAPI:**
```json
{
  "detail": "Could not validate credentials"
}
```

Or with validation errors:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Winner: FastAPI** - More detailed validation errors

## Documentation

**Django:**
- Manual documentation or drf-spectacular
- Requires additional setup
- Interactive via Swagger UI (with extension)

**FastAPI:**
- Automatic OpenAPI documentation
- Interactive docs at `/docs` (Swagger UI)
- Alternative docs at `/redoc` (ReDoc)
- No additional setup required

**Winner: FastAPI** - Built-in, zero configuration

## Deployment

**Django:**
```bash
gunicorn backend.wsgi:application --workers 4
```

**FastAPI:**
```bash
# Single worker
uvicorn api_service.main:app --host 0.0.0.0 --port 8000

# Multiple workers
gunicorn api_service.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

**Winner: Tie** - Both support production deployment well

## Verdict

### Choose FastAPI When:
- ✅ Performance is critical
- ✅ Building microservices/APIs only
- ✅ Want modern Python features (async, type hints)
- ✅ Need auto-generated documentation
- ✅ Stateless architecture (JWT)
- ✅ Type safety is important
- ✅ Starting a new project

### Choose Django When:
- ✅ Need admin panel out-of-the-box
- ✅ Building full-stack web app
- ✅ Want mature ecosystem
- ✅ Team familiar with Django
- ✅ Need ORM with excellent features
- ✅ Existing Django project

## For This Todo List Project

**Recommendation: FastAPI**

Reasons:
1. ✅ API-only (no admin panel needed)
2. ✅ 3-5x better performance
3. ✅ Modern Python patterns
4. ✅ Better for microservices
5. ✅ Cleaner architecture
6. ✅ Auto-generated docs
7. ✅ Future-proof with type safety

The FastAPI implementation provides all the features of the Django version with significantly better performance, type safety, and developer experience.
