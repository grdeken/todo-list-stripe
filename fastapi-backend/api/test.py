"""Vercel serverless handler for FastAPI Todo App."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Test: Try importing just settings first
try:
    from src.api_service.core.config import settings
    settings_loaded = True
    settings_error = None
except Exception as e:
    settings_loaded = False
    settings_error = str(e)

# Create FastAPI application
app = FastAPI(
    title="FastAPI Todo List API",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://todo-list-front-end-tau.vercel.app", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "settings_loaded": settings_loaded,
        "settings_error": settings_error
    }


@app.get("/")
async def root() -> dict:
    """Root endpoint with API information."""
    return {
        "name": "FastAPI Todo List API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
