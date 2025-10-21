# Todo List Manager - Full Stack Application

A full-stack todo list application built with **React** (frontend) and **Django REST Framework** (backend).

## Architecture Overview

### Backend (Django)
- **Framework**: Django 4.2 with Django REST Framework
- **Database**: SQLite (can be switched to PostgreSQL)
- **Authentication**: Token-based authentication
- **Models**:
  - `User` - Built-in Django user model (email, username, password)
  - `TodoList` - Container for todos (id, name, user, timestamps)
  - `Todo` - Individual todo items (id, description, complete, due_date, todo_list, timestamps)

### Frontend (React)
- **Framework**: React 18 with Vite
- **Styling**: Custom CSS with gradient design
- **Features**:
  - User registration and login
  - Create, read, update, delete todos
  - Mark todos as complete/incomplete
  - Set due dates for todos
  - Persistent authentication with localStorage

## Project Structure

```
test/
├── backend/                 # Django backend
│   ├── backend/            # Django project settings
│   │   ├── settings.py     # Configuration (CORS, REST Framework, etc.)
│   │   └── urls.py         # Main URL routing
│   ├── todos/              # Todos Django app
│   │   ├── models.py       # Data models (TodoList, Todo)
│   │   ├── serializers.py  # DRF serializers
│   │   ├── views.py        # API views and authentication
│   │   └── urls.py         # API endpoints
│   └── manage.py           # Django management script
├── todo-app/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── Login.jsx   # Login/Register component
│   │   │   ├── TodoList.jsx # Main todo list view
│   │   │   └── TodoItem.jsx # Individual todo item
│   │   ├── api.js          # API client functions
│   │   ├── types.js        # Data type definitions
│   │   ├── App.jsx         # Main app component
│   │   └── App.css         # Styling
│   └── package.json
└── backend_env/            # Python virtual environment
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login and get token
- `POST /api/auth/logout/` - Logout and delete token

### Todo Lists
- `GET /api/todo-lists/` - Get all todo lists for authenticated user
- `POST /api/todo-lists/` - Create new todo list
- `GET /api/todo-lists/{id}/` - Get specific todo list
- `PATCH /api/todo-lists/{id}/` - Update todo list
- `DELETE /api/todo-lists/{id}/` - Delete todo list

### Todos
- `POST /api/todos/` - Create new todo
- `PATCH /api/todos/{id}/` - Update todo
- `POST /api/todos/{id}/toggle/` - Toggle todo complete status
- `DELETE /api/todos/{id}/` - Delete todo

## Running the Application

### Backend (Django)
```bash
cd test
source backend_env/bin/activate
cd backend
python manage.py runserver 8000
```

Backend will be available at: `http://localhost:8000`

### Frontend (React)
```bash
cd test/todo-app
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## How to Use

1. **Start both servers** (backend and frontend)
2. **Open browser** to `http://localhost:5173`
3. **Register** a new account with email, username, and password
4. **Login** with your credentials
5. **Add todos** with descriptions and optional due dates
6. **Check off** completed todos by clicking the checkbox
7. **Delete** todos using the delete button
8. **Logout** when done

## Key Features

### Backend Models
- **Proper Django ORM models** with relationships
- **User authentication** with token-based auth
- **Automatic timestamps** (created_at, updated_at)
- **Model methods** like `toggle_complete()` on Todo model
- **Proper foreign key relationships** (User -> TodoList -> Todo)

### Authentication
- **Token-based authentication** for stateless API
- **CORS configured** for React frontend
- **Secure password handling** with Django's built-in user model

### Data Persistence
- **SQLite database** stores all data
- **Migrations** manage database schema
- **localStorage** keeps user logged in on frontend

## Database Schema

```
User (Django built-in)
├── id
├── username
├── email
└── password (hashed)

TodoList
├── id
├── name
├── user_id (FK -> User)
├── created_at
└── updated_at

Todo
├── id
├── description
├── complete (boolean)
├── due_date (nullable)
├── todo_list_id (FK -> TodoList)
├── created_at
└── updated_at
```

## Switching to PostgreSQL

To use PostgreSQL instead of SQLite:

1. Install PostgreSQL and create a database
2. Update `backend/backend/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'todolist_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

3. Run migrations again:
```bash
python manage.py migrate
```

## Technologies Used

- **Backend**: Python, Django, Django REST Framework, SQLite
- **Frontend**: React, JavaScript, CSS
- **Build Tool**: Vite
- **Authentication**: Token-based (DRF TokenAuthentication)
- **HTTP Client**: Fetch API
