"""Dramatiq tasks for folder batch processing.

Handles asynchronous folder traversal, document creation, and progress tracking.
"""

import asyncio
from pathlib import Path

import dramatiq
import structlog

from src.ingestion_parsing.tasks.worker import redis_broker  # Ensure broker is initialized
from src.ingestion_parsing.services.folder_service import FolderService
from src.ingestion_parsing.tasks.document_tasks import parse_document_task
from src.storage_indexing.database import get_db
from src.storage_indexing.models.document import Document
from src.storage_indexing.repositories.document_repository import DocumentRepository
from src.storage_indexing.repositories.folder_batch_repository import (
    FolderBatchRepository,
)

logger = structlog.get_logger(__name__)


@dramatiq.actor(max_retries=3, time_limit=600000)  # 10 minutes timeout
def process_folder_batch(batch_id: int, tenant_id: int) -> None:
    """Process a folder batch: discover files, create documents, queue parsing.
    
    This Dramatiq task:
    1. Discovers all markdown files in the folder
    2. Creates Document records for each file
    3. Queues parsing tasks for each document
    4. Updates batch status and progress
    
    Args:
        batch_id: FolderBatch identifier
        tenant_id: Tenant identifier for multi-tenancy
        
    Example:
        >>> process_folder_batch.send(batch_id=123, tenant_id=1)
    """
    logger.info("Process folder batch task started", batch_id=batch_id, tenant_id=tenant_id)
    
    try:
        asyncio.run(_process_folder_batch_async(batch_id, tenant_id))
        logger.info("Process folder batch task completed", batch_id=batch_id)
    except Exception as e:
        logger.error(
            "Process folder batch task failed",
            batch_id=batch_id,
            tenant_id=tenant_id,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise


async def _process_folder_batch_async(batch_id: int, tenant_id: int) -> None:
    """Async helper for folder batch processing.
    
    Args:
        batch_id: FolderBatch identifier
        tenant_id: Tenant identifier
    """
    # Ensure database is initialized
    from src.storage_indexing.database import init_db
    init_db()
    
    async for db_session in get_db():
        try:
            # Initialize repositories
            batch_repo = FolderBatchRepository(db_session)
            document_repo = DocumentRepository(db_session)
            
            # Get batch
            batch = await batch_repo.get_by_id(batch_id, tenant_id)
            if not batch:
                logger.error("FolderBatch not found", batch_id=batch_id, tenant_id=tenant_id)
                return
            
            # Discover markdown files
            folder_service = FolderService()
            folder_path = Path(batch.folder_path)
            
            logger.info("Starting file discovery", batch_id=batch_id, folder_path=str(folder_path))
            
            try:
                markdown_files = await folder_service.discover_markdown_files(folder_path)
            except FileNotFoundError:
                batch.status = "failed"
                batch.error_message = f"Folder not found: {folder_path}"
                await db_session.commit()
                logger.error("Folder not found", folder_path=str(folder_path))
                return
            
            # Update total files discovered
            batch.total_files_discovered = len(markdown_files)
            await db_session.commit()
            
            logger.info(
                "File discovery completed",
                batch_id=batch_id,
                total_files=len(markdown_files),
            )
            
            # Check if any files found
            if len(markdown_files) == 0:
                batch.status = "failed"
                batch.error_message = "No markdown files found in folder"
                await db_session.commit()
                logger.warning("No markdown files found", batch_id=batch_id)
                return
            
            # Create Document records and queue parsing tasks
            batch.status = "processing"
            await db_session.commit()
            
            for file_path in markdown_files:
                try:
                    # Calculate relative path
                    relative_path = file_path.relative_to(folder_path)
                    
                    # Create Document record
                    document = Document(
                        tenant_id=tenant_id,
                        uploaded_by=batch.user_id,
                        filename=file_path.name,
                        original_filename=str(relative_path),
                        file_size=file_path.stat().st_size,
                        mime_type="text/markdown",
                        storage_path=str(file_path),
                        content_hash="",  # Will be generated during parsing
                        folder_batch_id=batch_id,
                        processing_status="pending",
                    )
                    
                    db_session.add(document)
                    await db_session.flush()
                    
                    # Queue parsing task
                    parse_document_task.send(document.document_id)
                    
                    logger.debug(
                        "Document created and parsing queued",
                        batch_id=batch_id,
                        document_id=document.document_id,
                        filename=file_path.name,
                    )
                
                except Exception as e:
                    logger.error(
                        "Failed to create document",
                        batch_id=batch_id,
                        file_path=str(file_path),
                        error=str(e),
                    )
                    batch.files_failed += 1
            
            await db_session.commit()
            
            logger.info(
                "All parsing tasks queued",
                batch_id=batch_id,
                total_files=len(markdown_files),
                files_failed=batch.files_failed,
            )
        
        finally:
            await db_session.close()


@dramatiq.actor(max_retries=5, time_limit=30000)  # 30 seconds timeout
def update_folder_batch_progress(
    batch_id: int,
    tenant_id: int,
    processed: int = 0,
    failed: int = 0,
) -> None:
    """Update folder batch progress counters.
    
    Increments files_processed or files_failed counters and updates batch status
    when all files are processed.
    
    Args:
        batch_id: FolderBatch identifier
        tenant_id: Tenant identifier
        processed: Number of successfully processed files to add
        failed: Number of failed files to add
        
    Example:
        >>> update_folder_batch_progress.send(
        ...     batch_id=123,
        ...     tenant_id=1,
        ...     processed=1,
        ...     failed=0,
        ... )
    """
    logger.debug(
        "Update folder batch progress task started",
        batch_id=batch_id,
        processed=processed,
        failed=failed,
    )
    
    try:
        asyncio.run(_update_folder_batch_progress_async(batch_id, tenant_id, processed, failed))
    except Exception as e:
        logger.error(
            "Update folder batch progress task failed",
            batch_id=batch_id,
            error=str(e),
        )
        raise


async def _update_folder_batch_progress_async(
    batch_id: int,
    tenant_id: int,
    processed: int,
    failed: int,
) -> None:
    """Async helper for updating folder batch progress.
    
    Args:
        batch_id: FolderBatch identifier
        tenant_id: Tenant identifier
        processed: Files processed successfully
        failed: Files that failed processing
    """
    # Ensure database is initialized
    from src.storage_indexing.database import init_db
    init_db()
    
    async for db_session in get_db():
        try:
            batch_repo = FolderBatchRepository(db_session)
            
            # Update progress
            batch = await batch_repo.update_progress(
                batch_id=batch_id,
                tenant_id=tenant_id,
                processed_count=processed,
                failed_count=failed,
            )
            
            if batch:
                logger.info(
                    "Folder batch progress updated",
                    batch_id=batch_id,
                    files_processed=batch.files_processed,
                    files_failed=batch.files_failed,
                    total_files=batch.total_files_discovered,
                    status=batch.status,
                    progress_percentage=batch.progress_percentage,
                )
        
        finally:
            await db_session.close()


# Helper function to trigger folder batch processing
def trigger_folder_batch_processing(batch_id: int, tenant_id: int) -> None:
    """Trigger async folder batch processing.
    
    Call this from the upload API to queue a folder batch processing job.
    
    Args:
        batch_id: FolderBatch identifier
        tenant_id: Tenant identifier
        
    Example:
        >>> from src.ingestion_parsing.tasks.folder_tasks import trigger_folder_batch_processing
        >>> trigger_folder_batch_processing(batch_id=123, tenant_id=1)
    """
    process_folder_batch.send(batch_id, tenant_id)
    logger.info("Folder batch processing triggered", batch_id=batch_id, tenant_id=tenant_id)
