"""FastAPI application factory and configuration.

This module creates and configures the FastAPI application instance with
all middleware, routes, and event handlers.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.middleware import (
    LoggingMiddleware,
    RequestIDMiddleware,
    add_exception_handlers,
)
from src.api.routes import health
from src.shared.config import settings
from src.shared.logging_config import configure_logging, get_logger
from src.storage_indexing.database import close_db, init_db

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager.

    This function handles startup and shutdown events for the FastAPI application.

    Startup:
    - Configure logging
    - Initialize database connection pool

    Shutdown:
    - Close database connections

    Args:
        app: FastAPI application instance

    Yields:
        None
    """
    # Startup
    logger.info("application_startup", version="0.1.0", environment=settings.environment)

    # Configure logging
    configure_logging(log_level=settings.log_level, log_format=settings.log_format)
    logger.info("logging_configured", log_level=settings.log_level, log_format=settings.log_format)

    # Initialize database
    try:
        init_db()
        logger.info("database_initialized")
    except Exception as e:
        logger.error("database_initialization_failed", error=str(e), error_type=type(e).__name__)
        raise

    yield

    # Shutdown
    logger.info("application_shutdown")
    await close_db()
    logger.info("database_connection_closed")


def create_app() -> FastAPI:
    """Create and configure FastAPI application.

    Returns:
        FastAPI: Configured application instance
    """
    app = FastAPI(
        title="AgenticOmni API",
        description="AI-powered document intelligence platform with ETL-to-RAG pipeline",
        version="0.1.0",
        docs_url=f"/api/{settings.api_version}/docs",
        redoc_url=f"/api/{settings.api_version}/redoc",
        openapi_url=f"/api/{settings.api_version}/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add custom middleware (order matters: last added = first executed)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # Register exception handlers
    add_exception_handlers(app)

    # Register routes
    app.include_router(
        health.router,
        prefix=f"/api/{settings.api_version}",
        tags=["health"],
    )

    logger.info(
        "fastapi_app_created",
        docs_url=f"/api/{settings.api_version}/docs",
        cors_origins=settings.cors_origins,
    )

    return app


# Create application instance
app = create_app()
