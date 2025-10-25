"""Application configuration using Pydantic Settings."""
import json
from typing import Any, Optional

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Application
    PROJECT_NAME: str = "FastAPI Todo List API"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    CORS_ALLOW_CREDENTIALS: bool = True

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: Any) -> list[str]:
        """Parse ALLOWED_ORIGINS from string or list."""
        if isinstance(v, str):
            # Try to parse as JSON first (for environment variables)
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass
            # If not JSON, treat as comma-separated values
            return [origin.strip() for origin in v.split(",")]
        if isinstance(v, list):
            return v
        return ["http://localhost:5173", "http://localhost:3000"]

    # Database
    # REQUIRED: Must be set via environment variable
    # For local development, use PostgreSQL or set in .env file
    DATABASE_URL: str

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL is set and uses PostgreSQL."""
        if not v:
            raise ValueError(
                "DATABASE_URL must be set in environment variables or .env file. "
                "Example: postgresql+asyncpg://user:password@host:5432/dbname"
            )
        if not v.startswith("postgresql"):
            raise ValueError(
                "DATABASE_URL must use PostgreSQL. "
                "SQLite is not supported in production. "
                "Example: postgresql+asyncpg://user:password@host:5432/dbname"
            )
        return v

    # Security
    SECRET_KEY: str  # No default - must be set via environment variable
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate SECRET_KEY meets minimum security requirements."""
        if not v or len(v) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters long. "
                "Generate one using: openssl rand -hex 32"
            )
        if v == "your-secret-key-change-in-production":
            raise ValueError(
                "SECRET_KEY cannot be the default value. "
                "Generate a secure key using: openssl rand -hex 32"
            )
        return v

    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 100

    # Stripe Configuration
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PREMIUM_PRICE_ID: str = ""  # Stripe Price ID for premium subscription

    # Subscription Settings
    FREE_TIER_TODO_LIMIT: int = 5
    PREMIUM_MONTHLY_PRICE_CENTS: int = 999  # $9.99 in cents

    # Google OAuth Configuration
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = ""
    # Scopes for Google OAuth (profile, email, and calendar for future use)
    GOOGLE_OAUTH_SCOPES: list[str] = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/calendar.readonly",  # For future Calendar integration
        "https://www.googleapis.com/auth/calendar.events",     # For future Calendar integration
    ]


settings = Settings()
