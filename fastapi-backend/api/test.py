"""Vercel serverless handler for FastAPI Todo App with Postgres."""
from mangum import Mangum
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.api_service.core.config import settings
from src.api_service.api.v1.router import api_router

# Create FastAPI application (no lifespan for serverless)
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add session middleware (required for OAuth state management)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    max_age=3600,  # Session expires after 1 hour
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router with all routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.VERSION}


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with API information."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health",
    }

# Mangum handler for Vercel (AWS Lambda compatible)
# lifespan="off" prevents database initialization in the handler
handler = Mangum(app, lifespan="off")
