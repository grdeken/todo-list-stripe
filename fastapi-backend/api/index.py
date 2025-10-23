"""Vercel serverless function handler for FastAPI."""
# Import the FastAPI app directly - Vercel will handle it
from src.api_service.main import app

# Export app for Vercel
__all__ = ["app"]
