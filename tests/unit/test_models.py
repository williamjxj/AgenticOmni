"""Unit tests for SQLAlchemy models."""

from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.storage_indexing.models.document import Document, ProcessingStatus
from src.storage_indexing.models.document_chunk import DocumentChunk
from src.storage_indexing.models.tenant import Tenant
from src.storage_indexing.models.user import User, UserRole


class TestTenantModel:
    """Test suite for Tenant model."""

    @pytest.mark.asyncio
    async def test_tenant_model_creation(
        self,
        db_session: AsyncSession,
        sample_tenant_data: dict,
    ) -> None:
        """Test that Tenant model can be created and saved.

        Args:
            db_session: Test database session
            sample_tenant_data: Sample tenant data fixture
        """
        tenant = Tenant(**sample_tenant_data)

        db_session.add(tenant)
        await db_session.commit()
        await db_session.refresh(tenant)

        assert tenant.tenant_id is not None
        assert tenant.name == sample_tenant_data["name"]
        assert tenant.domain == sample_tenant_data["domain"]
        assert tenant.status == sample_tenant_data["status"]
        assert tenant.created_at is not None
        assert isinstance(tenant.created_at, datetime)

    @pytest.mark.asyncio
    async def test_tenant_domain_uniqueness(
        self,
        db_session: AsyncSession,
        sample_tenant_data: dict,
    ) -> None:
        """Test that tenant domain must be unique.

        Args:
            db_session: Test database session
            sample_tenant_data: Sample tenant data fixture
        """
        # Create first tenant
        tenant1 = Tenant(**sample_tenant_data)
        db_session.add(tenant1)
        await db_session.commit()

        # Try to create second tenant with same domain
        tenant2 = Tenant(**sample_tenant_data)
        db_session.add(tenant2)

        with pytest.raises(Exception):  # IntegrityError or similar
            await db_session.commit()


class TestUserModel:
    """Test suite for User model."""

    @pytest.mark.asyncio
    async def test_user_creation_with_tenant(
        self,
        db_session: AsyncSession,
        sample_tenant_data: dict,
        sample_user_data: dict,
    ) -> None:
        """Test that User model can be created with tenant relationship.

        Args:
            db_session: Test database session
            sample_tenant_data: Sample tenant data fixture
            sample_user_data: Sample user data fixture
        """
        # Create tenant first
        tenant = Tenant(**sample_tenant_data)
        db_session.add(tenant)
        await db_session.commit()
        await db_session.refresh(tenant)

        # Create user with tenant_id
        user = User(tenant_id=tenant.tenant_id, **sample_user_data)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.user_id is not None
        assert user.tenant_id == tenant.tenant_id
        assert user.email == sample_user_data["email"]
        assert user.role == UserRole.ADMIN
        assert user.is_active is True

    @pytest.mark.asyncio
    async def test_user_tenant_relationship(
        self,
        db_session: AsyncSession,
        sample_tenant_data: dict,
        sample_user_data: dict,
    ) -> None:
        """Test that User-Tenant foreign key relationship works.

        Args:
            db_session: Test database session
            sample_tenant_data: Sample tenant data fixture
            sample_user_data: Sample user data fixture
        """
        # Create tenant
        tenant = Tenant(**sample_tenant_data)
        db_session.add(tenant)
        await db_session.commit()
        await db_session.refresh(tenant)

        # Create user
        user = User(tenant_id=tenant.tenant_id, **sample_user_data)
        db_session.add(user)
        await db_session.commit()

        # Verify foreign key constraint
        assert user.tenant_id == tenant.tenant_id


class TestDocumentModel:
    """Test suite for Document model."""

    @pytest.mark.asyncio
    async def test_document_creation(
        self,
        db_session: AsyncSession,
        sample_tenant_data: dict,
        sample_document_data: dict,
    ) -> None:
        """Test that Document model can be created.

        Args:
            db_session: Test database session
            sample_tenant_data: Sample tenant data fixture
            sample_document_data: Sample document data fixture
        """
        # Create tenant first
        tenant = Tenant(**sample_tenant_data)
        db_session.add(tenant)
        await db_session.commit()
        await db_session.refresh(tenant)

        # Create document
        document = Document(tenant_id=tenant.tenant_id, **sample_document_data)
        db_session.add(document)
        await db_session.commit()
        await db_session.refresh(document)

        assert document.document_id is not None
        assert document.filename == sample_document_data["filename"]
        assert document.processing_status == ProcessingStatus.PENDING.value
        assert document.document_metadata is not None

    @pytest.mark.asyncio
    async def test_document_metadata_field(
        self,
        db_session: AsyncSession,
        sample_tenant_data: dict,
        sample_document_data: dict,
    ) -> None:
        """Test that document_metadata field stores JSON correctly.

        Args:
            db_session: Test database session
            sample_tenant_data: Sample tenant data fixture
            sample_document_data: Sample document data fixture
        """
        # Create tenant
        tenant = Tenant(**sample_tenant_data)
        db_session.add(tenant)
        await db_session.commit()
        await db_session.refresh(tenant)

        # Create document with metadata
        document = Document(tenant_id=tenant.tenant_id, **sample_document_data)
        db_session.add(document)
        await db_session.commit()
        await db_session.refresh(document)

        # Verify metadata
        assert isinstance(document.document_metadata, dict)
        assert document.document_metadata["author"] == "Test Author"
        assert document.document_metadata["pages"] == 10


class TestDocumentChunkModel:
    """Test suite for DocumentChunk model."""

    @pytest.mark.asyncio
    async def test_document_chunk_creation(
        self,
        db_session: AsyncSession,
        sample_tenant_data: dict,
        sample_document_data: dict,
        sample_document_chunk_data: dict,
    ) -> None:
        """Test that DocumentChunk model can be created.

        Args:
            db_session: Test database session
            sample_tenant_data: Sample tenant data fixture
            sample_document_data: Sample document data fixture
            sample_document_chunk_data: Sample document chunk data fixture
        """
        # Create tenant and document
        tenant = Tenant(**sample_tenant_data)
        db_session.add(tenant)
        await db_session.commit()
        await db_session.refresh(tenant)

        document = Document(tenant_id=tenant.tenant_id, **sample_document_data)
        db_session.add(document)
        await db_session.commit()
        await db_session.refresh(document)

        # Create chunk
        chunk = DocumentChunk(
            document_id=document.document_id,
            **sample_document_chunk_data,
        )
        db_session.add(chunk)
        await db_session.commit()
        await db_session.refresh(chunk)

        assert chunk.chunk_id is not None
        assert chunk.document_id == document.document_id
        assert chunk.content_text == sample_document_chunk_data["content_text"]
        assert chunk.chunk_order == 0
        assert chunk.chunk_metadata is not None
