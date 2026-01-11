"""Dramatiq tasks for document processing."""

import asyncio

import dramatiq
import structlog

from src.ingestion_parsing.tasks.worker import redis_broker  # Ensure broker is initialized
from src.ingestion_parsing.services.parsing_service import ParsingService
from src.storage_indexing.database import get_db
from src.storage_indexing.repositories.chunk_repository import ChunkRepository
from src.storage_indexing.repositories.document_repository import DocumentRepository
from src.storage_indexing.repositories.job_repository import JobRepository
from src.storage_indexing.repositories.markdown_repository import (
    ImageReferenceRepository,
    MarkdownMetadataRepository,
)

logger = structlog.get_logger(__name__)


@dramatiq.actor(max_retries=3, time_limit=300000)  # 5 minutes timeout
def parse_document_task(document_id: int) -> None:
    """Parse document asynchronously.
    
    This Dramatiq task:
    1. Gets database session
    2. Initializes parsing service
    3. Parses document and creates chunks
    4. Updates job status and progress
    
    Retries up to 3 times with exponential backoff on transient failures.
    
    Args:
        document_id: ID of document to parse
        
    Example:
        >>> parse_document_task.send(document_id=123)
    """
    logger.info("Parse document task started", document_id=document_id)
    
    try:
        # Run async parsing in event loop
        asyncio.run(_parse_document_async(document_id))
        
        logger.info("Parse document task completed", document_id=document_id)
        
    except Exception as e:
        logger.error(
            "Parse document task failed",
            document_id=document_id,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise


async def _parse_document_async(document_id: int) -> None:
    """Async helper for document parsing.
    
    Args:
        document_id: ID of document to parse
    """
    # Ensure database is initialized
    from src.storage_indexing.database import init_db
    init_db()
    
    # Get database session
    async for db_session in get_db():
        try:
            # Initialize repositories
            document_repo = DocumentRepository(db_session)
            chunk_repo = ChunkRepository(db_session)
            job_repo = JobRepository(db_session)
            markdown_metadata_repo = MarkdownMetadataRepository(db_session)
            image_reference_repo = ImageReferenceRepository(db_session)
            
            # Initialize parsing service
            parsing_service = ParsingService(
                document_repo=document_repo,
                chunk_repo=chunk_repo,
                job_repo=job_repo,
                markdown_metadata_repo=markdown_metadata_repo,
                image_reference_repo=image_reference_repo,
            )
            
            # Get document to check if it's part of a folder batch
            document = await document_repo.get_by_id(document_id, tenant_id=0)
            
            # Parse document (includes progress tracking)
            await parsing_service.parse_document(document_id)
            
            # If part of folder batch, update progress
            if document and document.folder_batch_id:
                from src.ingestion_parsing.tasks.folder_tasks import (
                    update_folder_batch_progress,
                )
                
                # Get tenant_id from document
                tenant_id = document.tenant_id
                
                # Update folder batch progress
                update_folder_batch_progress.send(
                    batch_id=document.folder_batch_id,
                    tenant_id=tenant_id,
                    processed=1,
                    failed=0,
                )
            
        except Exception as e:
            # If parsing failed and part of folder batch, update failed count
            try:
                document = await document_repo.get_by_id(document_id, tenant_id=0)
                if document and document.folder_batch_id:
                    from src.ingestion_parsing.tasks.folder_tasks import (
                        update_folder_batch_progress,
                    )
                    
                    update_folder_batch_progress.send(
                        batch_id=document.folder_batch_id,
                        tenant_id=document.tenant_id,
                        processed=0,
                        failed=1,
                    )
            except Exception:
                pass  # Don't fail the task if progress update fails
            
            raise e
        
        finally:
            # Ensure session is closed
            await db_session.close()


# Helper function to trigger parsing from API
def trigger_document_parsing(document_id: int) -> None:
    """Trigger async document parsing.
    
    Call this from the upload API to queue a parsing job.
    
    Args:
        document_id: ID of document to parse
        
    Example:
        >>> from src.ingestion_parsing.tasks.document_tasks import trigger_document_parsing
        >>> trigger_document_parsing(document_id=123)
    """
    parse_document_task.send(document_id)
    logger.info("Document parsing triggered", document_id=document_id)
