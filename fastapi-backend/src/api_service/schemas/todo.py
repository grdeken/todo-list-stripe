"""Todo and TodoList Pydantic schemas for request/response validation."""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# TodoList schemas
class TodoListCreate(BaseModel):
    """Schema for creating a todo list."""

    name: str = Field(..., min_length=1, max_length=200, description="Name of the todo list")


class TodoListUpdate(BaseModel):
    """Schema for updating a todo list."""

    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Name of the todo list")


class TodoListResponse(BaseModel):
    """Schema for todo list response without nested todos."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    user_id: int
    created_at: datetime
    updated_at: datetime


# Todo schemas
class TodoCreate(BaseModel):
    """Schema for creating a todo."""

    description: str = Field(..., min_length=1, description="Todo description")
    complete: bool = Field(default=False, description="Completion status")
    due_date: Optional[date] = Field(None, description="Optional due date")
    todo_list_id: int = Field(..., description="ID of the parent todo list")


class TodoUpdate(BaseModel):
    """Schema for updating a todo."""

    description: Optional[str] = Field(None, min_length=1, description="Todo description")
    complete: Optional[bool] = Field(None, description="Completion status")
    due_date: Optional[date] = Field(None, description="Optional due date")
    todo_list_id: Optional[int] = Field(None, description="ID of the parent todo list")


class TodoResponse(BaseModel):
    """Schema for todo response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    complete: bool
    due_date: Optional[date]
    todo_list_id: int
    created_at: datetime
    updated_at: datetime


# Nested response schemas
class TodoListWithTodosResponse(BaseModel):
    """Schema for todo list with nested todos."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    user_id: int
    created_at: datetime
    updated_at: datetime
    todos: list[TodoResponse] = []


# Toggle schema
class TodoToggleResponse(BaseModel):
    """Schema for toggle response."""

    id: int
    complete: bool
    message: str = Field(..., description="Success message")
