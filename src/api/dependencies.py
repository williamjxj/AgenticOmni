"""FastAPI dependencies for dependency injection.

This module provides reusable dependencies for FastAPI routes.
"""

from collections.abc import AsyncGenerator

from config.settings import Settings
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.config import settings
from src.storage_indexing.database import get_db as _get_db


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency.

    This is a wrapper around storage_indexing.database.get_db() for use
    as a FastAPI dependency.

    Yields:
        AsyncSession: Database session

    Example:
        >>> @router.get("/users")
        >>> async def list_users(db: AsyncSession = Depends(get_db)):
        >>>     result = await db.execute(select(User))
        >>>     return result.scalars().all()
    """
    async for session in _get_db():
        yield session


def get_settings() -> Settings:
    """Get application settings dependency.

    Returns:
        Settings: Application settings instance

    Example:
        >>> @router.get("/info")
        >>> async def app_info(settings: Settings = Depends(get_settings)):
        >>>     return {"version": settings.api_version}
    """
    return settings
