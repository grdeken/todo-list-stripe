"""Initialize database tables in Supabase Postgres.

Run this script once to create all the necessary tables for the Todo app.

Usage:
    python scripts/init_db.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api_service.db import Base, engine


async def init_db():
    """Create all database tables."""
    print("🔄 Creating database tables...")

    async with engine.begin() as conn:
        # Drop all tables (careful in production!)
        # await conn.run_sync(Base.metadata.drop_all)

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Database tables created successfully!")
    print("\nTables created:")
    print("  - users")
    print("  - todo_lists")
    print("  - todos")
    print("  - payment_transactions")
    print("  - subscription_events")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
