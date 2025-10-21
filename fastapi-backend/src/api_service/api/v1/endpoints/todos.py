"""Todo endpoints for CRUD operations."""
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from ....models import Todo, TodoList
from ....schemas import TodoCreate, TodoResponse, TodoToggleResponse, TodoUpdate
from ....services.subscription import check_todo_limit, get_user_todo_count
from ....core.config import settings
from ...deps import CurrentUser, DatabaseSession

router = APIRouter()


@router.get("/", response_model=list[TodoResponse])
async def get_todos(
    db: DatabaseSession,
    current_user: CurrentUser,
    todo_list_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Todo]:
    """
    Get all todos for the current user.

    Args:
        db: Database session
        current_user: Current authenticated user
        todo_list_id: Optional filter by todo list ID
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return

    Returns:
        List of todos
    """
    query = (
        select(Todo)
        .join(TodoList)
        .where(TodoList.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .order_by(Todo.complete, Todo.created_at.desc())
    )

    if todo_list_id:
        query = query.where(Todo.todo_list_id == todo_list_id)

    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_data: TodoCreate,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> Todo:
    """
    Create a new todo.

    Args:
        todo_data: Todo creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created todo

    Raises:
        HTTPException: If todo list doesn't exist or doesn't belong to user
        HTTPException: If user has reached their todo limit (403)
    """
    # Check todo limit before allowing creation
    can_create = await check_todo_limit(
        current_user, db, free_tier_limit=settings.FREE_TIER_TODO_LIMIT
    )
    if not can_create:
        current_count = await get_user_todo_count(current_user.id, db)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "todo_limit_reached",
                "message": "Upgrade to premium to create more todos",
                "current_count": current_count,
                "limit": settings.FREE_TIER_TODO_LIMIT,
            },
        )

    # Verify todo list exists and belongs to user
    result = await db.execute(
        select(TodoList).where(
            TodoList.id == todo_data.todo_list_id, TodoList.user_id == current_user.id
        )
    )
    todo_list = result.scalar_one_or_none()

    if not todo_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo list not found",
        )

    # Create todo
    db_todo = Todo(
        description=todo_data.description,
        complete=todo_data.complete,
        due_date=todo_data.due_date,
        todo_list_id=todo_data.todo_list_id,
    )
    db.add(db_todo)
    await db.commit()
    await db.refresh(db_todo)
    return db_todo


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: int,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> Todo:
    """
    Get a specific todo.

    Args:
        todo_id: ID of the todo
        db: Database session
        current_user: Current authenticated user

    Returns:
        Todo

    Raises:
        HTTPException: If todo not found or doesn't belong to user
    """
    result = await db.execute(
        select(Todo).join(TodoList).where(Todo.id == todo_id, TodoList.user_id == current_user.id)
    )
    todo = result.scalar_one_or_none()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    return todo


@router.patch("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> Todo:
    """
    Update a todo.

    Args:
        todo_id: ID of the todo
        todo_data: Todo update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated todo

    Raises:
        HTTPException: If todo not found or doesn't belong to user
    """
    result = await db.execute(
        select(Todo).join(TodoList).where(Todo.id == todo_id, TodoList.user_id == current_user.id)
    )
    todo = result.scalar_one_or_none()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    # Verify new todo list if provided
    if todo_data.todo_list_id and todo_data.todo_list_id != todo.todo_list_id:
        result = await db.execute(
            select(TodoList).where(
                TodoList.id == todo_data.todo_list_id, TodoList.user_id == current_user.id
            )
        )
        todo_list = result.scalar_one_or_none()

        if not todo_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target todo list not found",
            )

    # Update fields
    update_data = todo_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(todo, field, value)

    await db.commit()
    await db.refresh(todo)
    return todo


@router.post("/{todo_id}/toggle", response_model=TodoToggleResponse)
async def toggle_todo(
    todo_id: int,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> TodoToggleResponse:
    """
    Toggle the complete status of a todo.

    Args:
        todo_id: ID of the todo
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated completion status

    Raises:
        HTTPException: If todo not found or doesn't belong to user
    """
    result = await db.execute(
        select(Todo).join(TodoList).where(Todo.id == todo_id, TodoList.user_id == current_user.id)
    )
    todo = result.scalar_one_or_none()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    # Toggle complete status
    todo.complete = not todo.complete
    await db.commit()
    await db.refresh(todo)

    return TodoToggleResponse(
        id=todo.id,
        complete=todo.complete,
        message=f"Todo marked as {'complete' if todo.complete else 'incomplete'}",
    )


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> None:
    """
    Delete a todo.

    Args:
        todo_id: ID of the todo
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If todo not found or doesn't belong to user
    """
    result = await db.execute(
        select(Todo).join(TodoList).where(Todo.id == todo_id, TodoList.user_id == current_user.id)
    )
    todo = result.scalar_one_or_none()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    await db.delete(todo)
    await db.commit()
