"""Database connection management and session factory.

This module provides async database engine configuration and session management
for use throughout the application.
"""

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from src.shared.config import settings
from src.shared.exceptions import DatabaseError
from src.shared.logging_config import get_logger

logger = get_logger(__name__)

# SQLAlchemy declarative base for ORM models
Base: Any = declarative_base()

# Global engine instance (initialized by init_db)
_engine: AsyncEngine | None = None
_async_session_maker: async_sessionmaker[AsyncSession] | None = None


def init_db() -> AsyncEngine:
    """Initialize the database engine and session maker.

    This should be called once during application startup.

    Returns:
        AsyncEngine: The configured database engine

    Raises:
        DatabaseError: If database initialization fails
    """
    global _engine, _async_session_maker

    if _engine is not None:
        logger.warning("database_already_initialized")
        return _engine

    try:
        # Create async engine
        _engine = create_async_engine(
            str(settings.database_url),
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_pre_ping=True,  # Verify connections before using
            echo=settings.debug,  # Log SQL statements in debug mode
        )

        # Create session factory
        _async_session_maker = async_sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

        logger.info(
            "database_initialized",
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
        )

        return _engine

    except Exception as e:
        logger.error(
            "database_initialization_failed",
            error=str(e),
            error_type=type(e).__name__,
        )
        raise DatabaseError(
            "Failed to initialize database engine",
            details={"error": str(e)},
        ) from e


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session.

    This function is designed to be used as a FastAPI dependency.
    It provides a database session for the duration of a request,
    automatically handling commits and rollbacks.

    Yields:
        AsyncSession: Database session

    Example:
        >>> @router.get("/users")
        >>> async def get_users(db: AsyncSession = Depends(get_db)):
        >>>     result = await db.execute(select(User))
        >>>     return result.scalars().all()
    """
    if _async_session_maker is None:
        raise DatabaseError("Database not initialized. Call init_db() first.")

    async with _async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(
                "database_session_error",
                error=str(e),
                error_type=type(e).__name__,
            )
            raise
        finally:
            await session.close()


async def close_db() -> None:
    """Close the database engine and clean up connections.

    This should be called during application shutdown.
    """
    global _engine, _async_session_maker

    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session_maker = None
        logger.info("database_connection_closed")
