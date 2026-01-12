"""Dramatiq tasks for embedding generation.

Feature: 005-view-embedded-docs (Search Fix)
"""

import asyncio

import dramatiq
import structlog

from src.ingestion_parsing.tasks.worker import redis_broker  # Ensure broker is initialized
from src.rag_orchestration.services.embedding_service import EmbeddingService
from src.shared.config import settings
from src.storage_indexing.database import get_db, init_db, close_db
from src.storage_indexing.models.document_chunk import DocumentChunk
from src.storage_indexing.repositories.document_repository import DocumentRepository
from sqlalchemy import select

logger = structlog.get_logger(__name__)


@dramatiq.actor(max_retries=3, time_limit=600000)  # 10 minutes timeout
def generate_embeddings_task(document_id: int) -> None:
    """Generate embeddings for all chunks of a document asynchronously.
    
    This Dramatiq task:
    1. Gets all chunks for the document
    2. Generates embeddings for each chunk
    3. Updates chunks with embedding vectors
    4. Handles errors gracefully with retries
    
    Retries up to 3 times with exponential backoff on transient failures.
    
    Args:
        document_id: ID of document whose chunks need embeddings
        
    Example:
        >>> generate_embeddings_task.send(document_id=123)
    """
    logger.info("Generate embeddings task started", document_id=document_id)
    
    try:
        # Run async embedding generation in event loop
        asyncio.run(_generate_embeddings_async(document_id))
        
        logger.info("Generate embeddings task completed", document_id=document_id)
        
    except Exception as e:
        logger.error(
            "Generate embeddings task failed",
            document_id=document_id,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise


async def _generate_embeddings_async(document_id: int) -> None:
    """Async helper for embedding generation.
    
    Args:
        document_id: ID of document whose chunks need embeddings
    """
    # Close any existing connections from previous event loops
    await close_db()
    
    # Initialize fresh database connection for this event loop
    init_db()
    
    # Initialize embedding service
    embedding_service = EmbeddingService(settings)
    
    # Get database session
    async for db_session in get_db():
        try:
            # Get all chunks for this document that don't have embeddings
            query = (
                select(DocumentChunk)
                .where(DocumentChunk.document_id == document_id)
                .where(DocumentChunk.embedding_vector.is_(None))
            )
            
            result = await db_session.execute(query)
            chunks = result.scalars().all()
            
            if not chunks:
                logger.info(
                    "No chunks need embeddings",
                    document_id=document_id
                )
                return
            
            logger.info(
                "Generating embeddings for chunks",
                document_id=document_id,
                chunk_count=len(chunks)
            )
            
            # Generate embeddings for each chunk
            processed = 0
            failed = 0
            
            for chunk in chunks:
                try:
                    # Skip empty chunks
                    if not chunk.content_text or not chunk.content_text.strip():
                        logger.warning(
                            "Skipping empty chunk",
                            chunk_id=chunk.chunk_id,
                            document_id=document_id,
                        )
                        continue
                    
                    # Generate embedding
                    embedding = await embedding_service.get_embedding(chunk.content_text)
                    
                    # Update chunk with embedding
                    chunk.embedding_vector = embedding
                    chunk.embedding_model = settings.embedding_model
                    
                    processed += 1
                    
                    logger.debug(
                        "Embedding generated",
                        chunk_id=chunk.chunk_id,
                        document_id=document_id,
                        embedding_dim=len(embedding),
                    )
                    
                except Exception as e:
                    logger.error(
                        "Failed to generate embedding for chunk",
                        chunk_id=chunk.chunk_id,
                        document_id=document_id,
                        error=str(e),
                        error_type=type(e).__name__,
                    )
                    failed += 1
                    continue
            
            # Commit all embeddings
            await db_session.commit()
            
            logger.info(
                "Embeddings generated successfully",
                document_id=document_id,
                processed=processed,
                failed=failed,
            )
            
        except Exception as e:
            logger.error(
                "Failed to generate embeddings",
                document_id=document_id,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise e
        
        finally:
            # Ensure session is closed
            await db_session.close()


# Helper function to trigger embedding generation from parsing task
def trigger_embedding_generation(document_id: int) -> None:
    """Trigger async embedding generation.
    
    Call this from the parsing task after chunks are created.
    
    Args:
        document_id: ID of document to generate embeddings for
        
    Example:
        >>> from src.ingestion_parsing.tasks.embedding_tasks import trigger_embedding_generation
        >>> trigger_embedding_generation(document_id=123)
    """
    generate_embeddings_task.send(document_id)
    logger.info("Embedding generation triggered", document_id=document_id)
