"""Test data factories for creating sample entities.

This module provides factory functions for creating test data instances
of various models with realistic default values.
"""

from typing import Any

from src.storage_indexing.models.document import Document, ProcessingStatus
from src.storage_indexing.models.document_chunk import DocumentChunk
from src.storage_indexing.models.permission import Permission, PermissionLevel, ResourceType
from src.storage_indexing.models.processing_job import JobStatus, JobType, ProcessingJob
from src.storage_indexing.models.tenant import Tenant
from src.storage_indexing.models.user import User, UserRole


def create_tenant(
    name: str = "Test Organization",
    domain: str = "test-org",
    settings: dict[str, Any] | None = None,
    status: str = "active",
) -> Tenant:
    """Create a test tenant instance.

    Args:
        name: Tenant organization name
        domain: Tenant domain slug
        settings: Tenant-specific settings
        status: Tenant status

    Returns:
        Tenant: Test tenant instance
    """
    if settings is None:
        settings = {
            "theme": "light",
            "features": ["ocr", "rag", "document_upload"],
            "limits": {"max_documents": 10000, "max_storage_gb": 100},
        }

    return Tenant(
        name=name,
        domain=domain,
        settings=settings,
        status=status,
    )


def create_user(
    tenant_id: int,
    email: str = "testuser@example.com",
    role: UserRole = UserRole.USER,
    full_name: str = "Test User",
    is_active: bool = True,
) -> User:
    """Create a test user instance.

    Args:
        tenant_id: Associated tenant ID
        email: User email address
        role: User role
        full_name: User full name
        is_active: Whether user is active

    Returns:
        User: Test user instance
    """
    return User(
        tenant_id=tenant_id,
        email=email,
        hashed_password="$2b$12$test_hashed_password_placeholder",
        role=role,
        full_name=full_name,
        is_active=is_active,
    )


def create_document(
    tenant_id: int,
    filename: str = "test_document.pdf",
    file_type: str = "application/pdf",
    file_size: int = 1024000,
    storage_path: str = "/uploads/test_document.pdf",
    processing_status: ProcessingStatus = ProcessingStatus.PENDING,
) -> Document:
    """Create a test document instance.

    Args:
        tenant_id: Associated tenant ID
        filename: Document filename
        file_type: Document MIME type
        file_size: File size in bytes
        storage_path: Storage path
        processing_status: Processing status

    Returns:
        Document: Test document instance
    """
    return Document(
        tenant_id=tenant_id,
        filename=filename,
        file_type=file_type,
        file_size=file_size,
        storage_path=storage_path,
        processing_status=processing_status.value,
        document_metadata={
            "author": "Test Author",
            "pages": 10,
            "language": "en",
            "created_date": "2026-01-09",
        },
    )


def create_document_chunk(
    document_id: int,
    content_text: str = "This is a sample document chunk for testing purposes.",
    chunk_order: int = 0,
    embedding_vector: list[float] | None = None,
) -> DocumentChunk:
    """Create a test document chunk instance.

    Args:
        document_id: Associated document ID
        content_text: Chunk text content
        chunk_order: Order within document
        embedding_vector: Optional embedding vector

    Returns:
        DocumentChunk: Test document chunk instance
    """
    return DocumentChunk(
        document_id=document_id,
        content_text=content_text,
        embedding_vector=embedding_vector,
        chunk_order=chunk_order,
        chunk_metadata={
            "page": 1,
            "section": "Introduction",
            "char_count": len(content_text),
        },
    )


def create_permission(
    user_id: int,
    resource_type: ResourceType = ResourceType.DOCUMENT,
    resource_id: int = 1,
    permission_level: PermissionLevel = PermissionLevel.READ,
    granted_by: int | None = None,
) -> Permission:
    """Create a test permission instance.

    Args:
        user_id: Associated user ID
        resource_type: Resource type
        resource_id: Resource ID
        permission_level: Permission level
        granted_by: ID of user who granted permission

    Returns:
        Permission: Test permission instance
    """
    return Permission(
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        permission_level=permission_level,
        granted_by=granted_by,
    )


def create_processing_job(
    document_id: int,
    tenant_id: int,
    job_type: JobType = JobType.OCR,
    status: JobStatus = JobStatus.PENDING,
    max_retries: int = 3,
) -> ProcessingJob:
    """Create a test processing job instance.

    Args:
        document_id: Associated document ID
        tenant_id: Associated tenant ID
        job_type: Type of processing job
        status: Job status
        max_retries: Maximum retry attempts

    Returns:
        ProcessingJob: Test processing job instance
    """
    return ProcessingJob(
        document_id=document_id,
        tenant_id=tenant_id,
        job_type=job_type,
        status=status,
        retry_count=0,
        max_retries=max_retries,
    )
