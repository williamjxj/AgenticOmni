"""Shared pytest fixtures for all tests.

This module provides fixtures for:
- Database connections and sessions
- FastAPI test client
- Mock settings
- Test data factories
"""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
import pytest_asyncio
from config.settings import Settings
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from src.api.main import create_app
from src.storage_indexing.database import get_db
from src.storage_indexing.models.base import Base


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session.

    Yields:
        asyncio.AbstractEventLoop: Event loop for async tests
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Provide test configuration settings.

    Returns:
        Settings: Test configuration with overrides
    """
    return Settings(
        database_url="postgresql+asyncpg://agenti_user:agenti_user@localhost:5436/agenticomni_test",
        database_pool_size=2,
        database_max_overflow=0,
        vector_dimensions=1536,
        api_host="127.0.0.1",
        api_port=8001,
        cors_origins="http://localhost:3000",
        log_level="DEBUG",
        log_format="json",
        secret_key="test_secret_key_for_testing_only_32_chars_min",
        enforce_tenant_isolation=True,
        redis_url="redis://localhost:6380/1",
        redis_max_connections=2,
        environment="test",
        debug=True,
        api_version="v1",
        upload_dir="./test_uploads",
        max_upload_size_mb=10,
        allowed_file_types="pdf,txt",
    )


@pytest_asyncio.fixture(scope="function")
async def test_db_engine(test_settings: Settings) -> AsyncGenerator[AsyncEngine, None]:
    """Create a test database engine.

    Creates a fresh database engine for each test function.
    Uses NullPool to avoid connection pooling issues in tests.

    Args:
        test_settings: Test configuration

    Yields:
        AsyncEngine: Test database engine
    """
    engine = create_async_engine(
        str(test_settings.database_url),
        echo=False,
        poolclass=NullPool,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a test database session with automatic rollback.

    Each test gets a fresh session that is rolled back after the test,
    ensuring test isolation.

    Args:
        test_db_engine: Test database engine

    Yields:
        AsyncSession: Test database session
    """
    async_session_maker = sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session
        # Tables are dropped after each test by test_db_engine fixture
        # so no need for explicit rollback


@pytest.fixture(scope="function")
def test_client(
    test_settings: Settings, db_session: AsyncSession
) -> Generator[TestClient, None, None]:
    """Provide a FastAPI test client.

    The test client uses the test database session and test settings.

    Args:
        test_settings: Test configuration
        db_session: Test database session

    Yields:
        TestClient: FastAPI test client
    """

    # Override the get_db dependency to use test session
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    # Create app with test settings
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def mock_settings(test_settings: Settings) -> Settings:
    """Provide mock settings for testing.

    This fixture allows tests to override specific settings values
    without affecting the global settings instance.

    Args:
        test_settings: Test configuration

    Returns:
        Settings: Mock settings instance
    """
    return test_settings


# ============================================================================
# Test Data Factories
# ============================================================================


@pytest.fixture
def sample_tenant_data() -> dict[str, Any]:
    """Provide sample tenant data for testing.

    Returns:
        dict: Tenant test data
    """
    return {
        "name": "Test Organization",
        "domain": "test-org",
        "settings": {"theme": "dark", "features": ["ocr", "rag"]},
        "status": "active",
    }


@pytest.fixture
def sample_user_data(sample_tenant_data: dict[str, Any]) -> dict[str, Any]:
    """Provide sample user data for testing.

    Args:
        sample_tenant_data: Tenant test data

    Returns:
        dict: User test data
    """
    return {
        "email": "test@example.com",
        "hashed_password": "hashed_password_here",
        "role": "admin",
        "full_name": "Test User",
        "is_active": True,
    }


@pytest.fixture
def sample_document_data() -> dict[str, Any]:
    """Provide sample document data for testing.

    Returns:
        dict: Document test data
    """
    return {
        "filename": "test_document.pdf",
        "file_type": "application/pdf",
        "file_size": 1024000,
        "storage_path": "/uploads/test_document.pdf",
        "processing_status": "pending",
        "document_metadata": {"author": "Test Author", "pages": 10},
    }


@pytest.fixture
def sample_document_chunk_data() -> dict[str, Any]:
    """Provide sample document chunk data for testing.

    Returns:
        dict: Document chunk test data
    """
    return {
        "content_text": "This is a test document chunk with some content.",
        "chunk_order": 0,
        "chunk_metadata": {"page": 1, "section": "Introduction"},
    }
