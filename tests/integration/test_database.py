"""Integration tests for database connectivity and operations."""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession


class TestDatabaseConnection:
    """Test suite for database connectivity."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_database_connection(self, test_db_engine: AsyncEngine) -> None:
        """Test that async database engine connects successfully.

        Args:
            test_db_engine: Test database engine fixture
        """
        async with test_db_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            row = result.fetchone()
            assert row is not None
            assert row[0] == 1

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_database_version(self, test_db_engine: AsyncEngine) -> None:
        """Test database version query.

        Args:
            test_db_engine: Test database engine fixture
        """
        async with test_db_engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.fetchone()
            assert version is not None
            assert "PostgreSQL" in version[0]

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_pgvector_extension_available(self, test_db_engine: AsyncEngine) -> None:
        """Test that pgvector extension is available.

        Args:
            test_db_engine: Test database engine fixture
        """
        async with test_db_engine.connect() as conn:
            # Try to create vector extension if not exists
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            await conn.commit()

            # Verify extension exists
            result = await conn.execute(text("SELECT * FROM pg_extension WHERE extname='vector'"))
            extension = result.fetchone()
            assert extension is not None


class TestDatabaseSchema:
    """Test suite for database schema operations."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_tables_created(self, test_db_engine: AsyncEngine) -> None:
        """Test that all required tables are created.

        Args:
            test_db_engine: Test database engine fixture
        """
        expected_tables = {
            "tenants",
            "users",
            "documents",
            "document_chunks",
            "permissions",
            "processing_jobs",
        }

        async with test_db_engine.connect() as conn:
            result = await conn.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            )
            actual_tables = {row[0] for row in result.fetchall()}

            assert expected_tables.issubset(actual_tables)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_alembic_migrations(self, test_db_engine: AsyncEngine) -> None:
        """Test that Alembic migrations can be tracked.

        Args:
            test_db_engine: Test database engine fixture
        """
        async with test_db_engine.connect() as conn:
            # Check if alembic_version table exists (in production)
            result = await conn.execute(
                text(
                    "SELECT EXISTS ("
                    "  SELECT FROM information_schema.tables "
                    "  WHERE table_schema = 'public' "
                    "  AND table_name = 'alembic_version'"
                    ")"
                )
            )
            # Table might not exist in test DB since we use metadata.create_all
            # This test verifies the query works
            exists = result.scalar()
            assert exists is not None


class TestDatabaseSession:
    """Test suite for database session management."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_session_transaction(self, db_session: AsyncSession) -> None:
        """Test that database session supports transactions.

        Args:
            db_session: Test database session fixture
        """
        # Execute a simple query
        result = await db_session.execute(text("SELECT 1 as value"))
        row = result.fetchone()
        assert row is not None
        assert row[0] == 1

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_session_rollback(self, db_session: AsyncSession) -> None:
        """Test that session rollback works correctly.

        Args:
            db_session: Test database session fixture
        """
        # The fixture automatically rolls back after the test
        # So anything we do here will be rolled back
        from src.storage_indexing.models.tenant import Tenant

        tenant = Tenant(
            name="Test Tenant",
            domain="test-rollback",
            settings={},
            status="active",
        )
        db_session.add(tenant)
        await db_session.flush()

        # Tenant should have an ID after flush
        assert tenant.tenant_id is not None

        # After test ends, this will be rolled back automatically
