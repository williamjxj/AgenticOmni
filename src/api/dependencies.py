"""FastAPI dependencies for dependency injection.

This module provides reusable dependencies for FastAPI routes.
"""

from collections.abc import AsyncGenerator

from config.settings import Settings
from fastapi import Depends
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
from src.rag_orchestration.services.embedding_service import EmbeddingService
from src.rag_orchestration.services.search_service import SearchService
from src.storage_indexing.repositories.search_query_repository import SearchQueryRepository
from src.storage_indexing.repositories.search_result_repository import SearchResultRepository


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
    if settings.storage_backend == "local":
        return LocalFileStorage(base_dir=settings.upload_dir)
    elif settings.storage_backend == "s3":
        # S3 configuration would come from settings
        return S3FileStorage(
            bucket=settings.s3_bucket,
            region=settings.s3_region,
            access_key=settings.aws_access_key_id,
            secret_key=settings.aws_secret_access_key,
        )
    else:
        raise ValueError(f"Unknown storage backend: {settings.storage_backend}")


async def get_quota_manager(session: AsyncSession = Depends(get_db)) -> QuotaManager:
    """Get quota manager dependency.
    
    Args:
        session: Database session (injected)
        
    Returns:
        QuotaManager: Quota manager instance
    """
    return QuotaManager(session)


async def get_document_repository(session: AsyncSession = Depends(get_db)) -> DocumentRepository:
    """Get document repository dependency.
    
    Args:
        session: Database session (injected)
        
    Returns:
        DocumentRepository: Document repository instance
    """
    return DocumentRepository(session)


async def get_chunk_repository(session: AsyncSession = Depends(get_db)) -> ChunkRepository:
    """Get chunk repository dependency.
    
    Args:
        session: Database session (injected)
        
    Returns:
        ChunkRepository: Chunk repository instance
    """
    return ChunkRepository(session)


async def get_job_repository(session: AsyncSession = Depends(get_db)) -> JobRepository:
    """Get job repository dependency.
    
    Args:
        session: Database session (injected)
        
    Returns:
        JobRepository: Job repository instance
    """
    return JobRepository(session)


async def get_upload_session_repository(session: AsyncSession = Depends(get_db)) -> UploadSessionRepository:
    """Get upload session repository dependency.
    
    Args:
        session: Database session (injected)
        
    Returns:
        UploadSessionRepository: Upload session repository instance
    """
    return UploadSessionRepository(session)


def get_embedding_service(settings: Settings = Depends(get_settings)) -> EmbeddingService:
    """Get embedding service dependency."""
    return EmbeddingService(settings)


async def get_search_service(
    session: AsyncSession = Depends(get_db),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
) -> SearchService:
    """Get search service dependency."""
    return SearchService(
        session=session,
        embedding_service=embedding_service,
        query_repo=SearchQueryRepository(session),
        result_repo=SearchResultRepository(session)
    )
