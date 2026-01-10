"""Document repository for CRUD operations."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import structlog

from src.storage_indexing.models import Document, ProcessingStatus

logger = structlog.get_logger(__name__)


class DocumentRepository:
    """Repository for document database operations.
    
    Handles CRUD operations for documents with tenant isolation.
    
    Example:
        >>> repo = DocumentRepository(db_session)
        >>> document = await repo.create(
        ...     tenant_id=1,
        ...     uploaded_by=5,
        ...     filename="doc123.pdf",
        ...     original_filename="Report.pdf",
        ...     file_type="pdf",
        ...     mime_type="application/pdf",
        ...     file_size=1024000,
        ...     storage_path="/1/doc123.pdf",
        ...     content_hash="abc123...",
        ... )
    """

    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize repository.
        
        Args:
            db_session: Async database session
        """
        self.db = db_session

    async def create(
        self,
        *,
        tenant_id: int,
        uploaded_by: int,
        filename: str,
        original_filename: str,
        file_type: str,
        mime_type: str,
        file_size: int,
        storage_path: str,
        content_hash: str,
        language: str | None = None,
        page_count: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Document:
        """Create a new document record.
        
        Args:
            tenant_id: Tenant ID
            uploaded_by: User ID who uploaded the document
            filename: Stored filename (system-generated)
            original_filename: Original filename from upload
            file_type: File extension (pdf, docx, txt)
            mime_type: Detected MIME type
            file_size: File size in bytes
            storage_path: Path or S3 key where file is stored
            content_hash: SHA-256 hash for duplicate detection
            language: Detected language (optional)
            page_count: Number of pages (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            Created Document instance
        """
        document = Document(
            tenant_id=tenant_id,
            uploaded_by=uploaded_by,
            filename=filename,
            original_filename=original_filename,
            file_type=file_type,
            mime_type=mime_type,
            file_size=file_size,
            storage_path=storage_path,
            content_hash=content_hash,
            language=language,
            page_count=page_count,
            processing_status=ProcessingStatus.UPLOADED.value,
            document_metadata=metadata or {},
        )
        
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        
        logger.info(
            "Document created",
            document_id=document.document_id,
            tenant_id=tenant_id,
            filename=filename,
            file_size=file_size,
        )
        
        return document

    async def get_by_id(self, document_id: int, tenant_id: int) -> Document | None:
        """Get document by ID with tenant isolation.
        
        Args:
            document_id: Document ID
            tenant_id: Tenant ID for isolation
            
        Returns:
            Document instance or None if not found
        """
        result = await self.db.execute(
            select(Document).where(
                Document.document_id == document_id,
                Document.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def update_status(
        self,
        document_id: int,
        status: str,
        language: str | None = None,
        page_count: int | None = None,
    ) -> Document | None:
        """Update document processing status.
        
        Args:
            document_id: Document ID
            status: New processing status
            language: Detected language (optional)
            page_count: Number of pages (optional)
            
        Returns:
            Updated Document instance or None if not found
        """
        document = await self.db.get(Document, document_id)
        if not document:
            return None
        
        document.processing_status = status
        if language:
            document.language = language
        if page_count:
            document.page_count = page_count
        document.updated_at = datetime.now(UTC)
        
        await self.db.commit()
        await self.db.refresh(document)
        
        logger.info(
            "Document status updated",
            document_id=document_id,
            status=status,
            language=language,
            page_count=page_count,
        )
        
        return document

    async def delete(self, document_id: int, tenant_id: int) -> bool:
        """Delete document with tenant isolation.
        
        Args:
            document_id: Document ID
            tenant_id: Tenant ID for isolation
            
        Returns:
            True if deleted, False if not found
        """
        document = await self.get_by_id(document_id, tenant_id)
        if not document:
            return False
        
        await self.db.delete(document)
        await self.db.commit()
        
        logger.info("Document deleted", document_id=document_id, tenant_id=tenant_id)
        return True

    async def check_duplicate(self, tenant_id: int, content_hash: str) -> Document | None:
        """Check if document with same content hash already exists.
        
        Args:
            tenant_id: Tenant ID
            content_hash: SHA-256 content hash
            
        Returns:
            Existing Document instance or None
        """
        result = await self.db.execute(
            select(Document).where(
                Document.tenant_id == tenant_id,
                Document.content_hash == content_hash,
            )
        )
        return result.scalar_one_or_none()
