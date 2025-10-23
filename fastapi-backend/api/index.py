"""Vercel serverless function handler for FastAPI."""
from mangum import Mangum
from src.api_service.main import app

# Mangum handler for AWS Lambda/Vercel
handler = Mangum(app, lifespan="off")
