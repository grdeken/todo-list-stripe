"""TodoList endpoints for CRUD operations."""
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ....models import TodoList
from ....schemas import TodoListCreate, TodoListResponse, TodoListUpdate, TodoListWithTodosResponse
from ...deps import CurrentUser, DatabaseSession

router = APIRouter()


@router.get("/", response_model=list[TodoListWithTodosResponse])
async def get_todo_lists(
    db: DatabaseSession,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> list[TodoList]:
    """
    Get all todo lists for the current user with their todos.

    Args:
        db: Database session
        current_user: Current authenticated user
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return

    Returns:
        List of todo lists with nested todos
    """
    result = await db.execute(
        select(TodoList)
        .where(TodoList.user_id == current_user.id)
        .options(selectinload(TodoList.todos))
        .offset(skip)
        .limit(limit)
        .order_by(TodoList.created_at.desc())
    )
    return list(result.scalars().all())


@router.post("/", response_model=TodoListWithTodosResponse, status_code=status.HTTP_201_CREATED)
async def create_todo_list(
    todo_list_data: TodoListCreate,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> TodoList:
    """
    Create a new todo list.

    Args:
        todo_list_data: Todo list creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created todo list
    """
    db_todo_list = TodoList(
        name=todo_list_data.name,
        user_id=current_user.id,
    )
    db.add(db_todo_list)
    await db.commit()
    await db.refresh(db_todo_list, attribute_names=["todos"])
    return db_todo_list


@router.get("/{todo_list_id}", response_model=TodoListWithTodosResponse)
async def get_todo_list(
    todo_list_id: int,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> TodoList:
    """
    Get a specific todo list with its todos.

    Args:
        todo_list_id: ID of the todo list
        db: Database session
        current_user: Current authenticated user

    Returns:
        Todo list with nested todos

    Raises:
        HTTPException: If todo list not found or doesn't belong to user
    """
    result = await db.execute(
        select(TodoList)
        .where(TodoList.id == todo_list_id, TodoList.user_id == current_user.id)
        .options(selectinload(TodoList.todos))
    )
    todo_list = result.scalar_one_or_none()

    if not todo_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo list not found",
        )

    return todo_list


@router.patch("/{todo_list_id}", response_model=TodoListWithTodosResponse)
async def update_todo_list(
    todo_list_id: int,
    todo_list_data: TodoListUpdate,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> TodoList:
    """
    Update a todo list.

    Args:
        todo_list_id: ID of the todo list
        todo_list_data: Todo list update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated todo list with todos

    Raises:
        HTTPException: If todo list not found or doesn't belong to user
    """
    result = await db.execute(
        select(TodoList)
        .where(TodoList.id == todo_list_id, TodoList.user_id == current_user.id)
        .options(selectinload(TodoList.todos))
    )
    todo_list = result.scalar_one_or_none()

    if not todo_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo list not found",
        )

    # Update fields
    update_data = todo_list_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(todo_list, field, value)

    await db.commit()
    await db.refresh(todo_list, attribute_names=["todos"])
    return todo_list


@router.delete("/{todo_list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_list(
    todo_list_id: int,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> None:
    """
    Delete a todo list and all its todos.

    Args:
        todo_list_id: ID of the todo list
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If todo list not found or doesn't belong to user
    """
    result = await db.execute(
        select(TodoList).where(TodoList.id == todo_list_id, TodoList.user_id == current_user.id)
    )
    todo_list = result.scalar_one_or_none()

    if not todo_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo list not found",
        )

    await db.delete(todo_list)
    await db.commit()
