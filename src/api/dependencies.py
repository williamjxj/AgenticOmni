"""FastAPI dependencies for dependency injection.

This module provides reusable dependencies for FastAPI routes.
"""

from collections.abc import AsyncGenerator

from config.settings import Settings
from sqlalchemy.ext.asyncio import AsyncSession

from src.ingestion_parsing.storage.file_storage import FileStorage, LocalFileStorage, S3FileStorage
from src.ingestion_parsing.storage.quota_manager import QuotaManager
from src.shared.config import settings
from src.storage_indexing.database import get_db as _get_db
from src.storage_indexing.repositories.chunk_repository import ChunkRepository
from src.storage_indexing.repositories.document_repository import DocumentRepository
from src.storage_indexing.repositories.job_repository import JobRepository
from src.storage_indexing.repositories.upload_session_repository import (
    UploadSessionRepository,
)


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


# ============================================================================
# Document Upload Dependencies (T025)
# ============================================================================


def get_file_storage() -> FileStorage:
    """Get file storage backend dependency.
    
    Returns:
        FileStorage: Configured storage backend (Local or S3)
        
    Example:
        >>> @router.post("/upload")
        >>> async def upload_file(storage: FileStorage = Depends(get_file_storage)):
        >>>     await storage.upload(file_path, storage_key)
    """
    if settings.upload.storage_backend == "local":
        return LocalFileStorage(base_dir=settings.upload.upload_dir)
    elif settings.upload.storage_backend == "s3":
        # S3 configuration would come from settings
        return S3FileStorage(
            bucket=settings.upload.s3_bucket,
            region=settings.upload.s3_region,
            access_key=settings.upload.aws_access_key_id,
            secret_key=settings.upload.aws_secret_access_key,
        )
    else:
        raise ValueError(f"Unknown storage backend: {settings.upload.storage_backend}")


async def get_quota_manager() -> AsyncGenerator[QuotaManager, None]:
    """Get quota manager dependency.
    
    Yields:
        QuotaManager: Quota manager instance
        
    Example:
        >>> @router.post("/upload")
        >>> async def upload_file(quota: QuotaManager = Depends(get_quota_manager)):
        >>>     await quota.check_quota(tenant_id=1, file_size=5000000)
    """
    async for session in get_db():
        yield QuotaManager(session)


async def get_document_repository() -> AsyncGenerator[DocumentRepository, None]:
    """Get document repository dependency.
    
    Yields:
        DocumentRepository: Document repository instance
        
    Example:
        >>> @router.get("/documents/{doc_id}")
        >>> async def get_document(
        ...     doc_id: int,
        ...     repo: DocumentRepository = Depends(get_document_repository)
        ... ):
        ...     return await repo.get_by_id(doc_id, tenant_id=1)
    """
    async for session in get_db():
        yield DocumentRepository(session)


async def get_chunk_repository() -> AsyncGenerator[ChunkRepository, None]:
    """Get chunk repository dependency.
    
    Yields:
        ChunkRepository: Chunk repository instance
    """
    async for session in get_db():
        yield ChunkRepository(session)


async def get_job_repository() -> AsyncGenerator[JobRepository, None]:
    """Get job repository dependency.
    
    Yields:
        JobRepository: Job repository instance
    """
    async for session in get_db():
        yield JobRepository(session)


async def get_upload_session_repository() -> AsyncGenerator[UploadSessionRepository, None]:
    """Get upload session repository dependency.
    
    Yields:
        UploadSessionRepository: Upload session repository instance
    """
    async for session in get_db():
        yield UploadSessionRepository(session)
