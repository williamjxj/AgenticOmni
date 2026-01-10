"""Document chunk repository for CRUD operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import structlog

from src.storage_indexing.models import DocumentChunk

logger = structlog.get_logger(__name__)


class ChunkRepository:
    """Repository for document chunk database operations.
    
    Handles CRUD operations for document chunks.
    
    Example:
        >>> repo = ChunkRepository(db_session)
        >>> chunk = await repo.create(
        ...     document_id=123,
        ...     chunk_index=0,
        ...     content="This is the first chunk...",
        ...     chunk_type="paragraph",
        ...     token_count=50,
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
        document_id: int,
        chunk_index: int,
        content: str,
        chunk_type: str | None = None,
        start_page: int | None = None,
        end_page: int | None = None,
        token_count: int | None = None,
        parent_heading: str | None = None,
    ) -> DocumentChunk:
        """Create a new document chunk.
        
        Args:
            document_id: Parent document ID
            chunk_index: Sequential index of chunk within document
            content: Text content of the chunk
            chunk_type: Type of chunk (paragraph, heading, table, etc.)
            start_page: Starting page number
            end_page: Ending page number
            token_count: Number of tokens in chunk
            parent_heading: Parent section heading
            
        Returns:
            Created DocumentChunk instance
        """
        chunk = DocumentChunk(
            document_id=document_id,
            chunk_index=chunk_index,
            content=content,
            chunk_type=chunk_type,
            start_page=start_page,
            end_page=end_page,
            token_count=token_count,
            parent_heading=parent_heading,
        )
        
        self.db.add(chunk)
        await self.db.commit()
        await self.db.refresh(chunk)
        
        logger.debug(
            "Chunk created",
            chunk_id=chunk.chunk_id,
            document_id=document_id,
            chunk_index=chunk_index,
            token_count=token_count,
        )
        
        return chunk

    async def get_by_document(self, document_id: int) -> list[DocumentChunk]:
        """Get all chunks for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            List of DocumentChunk instances ordered by chunk_index
        """
        result = await self.db.execute(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
        )
        return list(result.scalars().all())

    async def delete_by_document(self, document_id: int) -> int:
        """Delete all chunks for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            Number of chunks deleted
        """
        chunks = await self.get_by_document(document_id)
        count = len(chunks)
        
        for chunk in chunks:
            await self.db.delete(chunk)
        
        await self.db.commit()
        
        logger.info("Chunks deleted", document_id=document_id, count=count)
        return count
