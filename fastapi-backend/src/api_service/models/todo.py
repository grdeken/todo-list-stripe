"""Todo and TodoList database models."""
from datetime import date, datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base


class TodoList(Base):
    """TodoList model - container for todos."""

    __tablename__ = "todo_lists"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="todo_lists")
    todos: Mapped[list["Todo"]] = relationship(
        "Todo", back_populates="todo_list", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<TodoList(id={self.id}, name='{self.name}', user_id={self.user_id})>"


class Todo(Base):
    """Todo model - individual todo item."""

    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    complete: Mapped[bool] = mapped_column(default=False, nullable=False)
    due_date: Mapped[Optional[date]] = mapped_column(nullable=True)
    todo_list_id: Mapped[int] = mapped_column(
        ForeignKey("todo_lists.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    todo_list: Mapped["TodoList"] = relationship("TodoList", back_populates="todos")

    def __repr__(self) -> str:
        status = "✓" if self.complete else "○"
        return f"<Todo(id={self.id}, description='{self.description[:50]}...', {status})>"
