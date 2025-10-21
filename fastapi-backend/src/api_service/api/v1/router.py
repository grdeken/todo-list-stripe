"""API v1 router aggregating all endpoints."""
from fastapi import APIRouter

from .endpoints import auth, todo_lists, todos, subscription

api_router = APIRouter()

# Include routers with tags for OpenAPI documentation
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(todo_lists.router, prefix="/todo-lists", tags=["Todo Lists"])
api_router.include_router(todos.router, prefix="/todos", tags=["Todos"])
api_router.include_router(subscription.router, prefix="/subscription", tags=["Subscription"])
