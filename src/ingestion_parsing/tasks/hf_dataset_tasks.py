"""Dramatiq tasks for HuggingFace dataset import and processing.

This module contains background tasks for importing external datasets
from HuggingFace Hub and processing them through the RAG pipeline.
"""

import asyncio
from typing import Any

import dramatiq
import structlog

from src.ingestion_parsing.services.hf_dataset_loader import HFDatasetLoader
from src.ingestion_parsing.services.chunking_service import ChunkingService
from src.storage_indexing.database import get_db, init_db, close_db
from src.storage_indexing.repositories.document_repository import DocumentRepository
from src.storage_indexing.repositories.chunk_repository import ChunkRepository
from src.storage_indexing.repositories.job_repository import JobRepository
from src.storage_indexing.models.document import ProcessingStatus
from src.storage_indexing.models.job import JobStatus, JobType

logger = structlog.get_logger(__name__)


@dramatiq.actor(max_retries=3, time_limit=1800000)  # 30 minutes timeout
def import_hf_dataset_task(
    dataset_name: str,
    tenant_id: int,
    split: str = "train",
    limit: int | None = None,
    user_id: int | None = None,
) -> dict[str, Any]:
    """Import HuggingFace dataset asynchronously.
    
    This Dramatiq task:
    1. Loads dataset from HuggingFace Hub
    2. Creates document records in database
    3. Chunks text content
    4. Triggers embedding generation
    5. Tracks progress via job repository
    
    Args:
        dataset_name: HuggingFace dataset identifier (e.g., "rajpurkar/squad")
        tenant_id: Tenant ID for data isolation
        split: Dataset split to load (train, validation)
        limit: Maximum number of records to import
        user_id: Optional user ID who initiated import
        
    Returns:
        Dictionary with import statistics
        
    Example:
        >>> import_hf_dataset_task.send(
        ...     dataset_name="rajpurkar/squad",
        ...     tenant_id=1,
        ...     limit=500
        ... )
    """
    logger.info(
        "HF dataset import task started",
        dataset_name=dataset_name,
        tenant_id=tenant_id,
        split=split,
        limit=limit,
    )
    
    try:
        # Run async import in event loop
        result = asyncio.run(_import_hf_dataset_async(
            dataset_name=dataset_name,
            tenant_id=tenant_id,
            split=split,
            limit=limit,
            user_id=user_id,
        ))
        
        logger.info(
            "HF dataset import task completed",
            dataset_name=dataset_name,
            result=result,
        )
        
        return result
        
    except Exception as e:
        logger.error(
            "HF dataset import task failed",
            dataset_name=dataset_name,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise


async def _import_hf_dataset_async(
    dataset_name: str,
    tenant_id: int,
    split: str,
    limit: int | None,
    user_id: int | None,
) -> dict[str, Any]:
    """Async helper for HF dataset import.
    
    Args:
        dataset_name: HuggingFace dataset identifier
        tenant_id: Tenant ID
        split: Dataset split
        limit: Record limit
        user_id: User ID
        
    Returns:
        Import statistics dictionary
    """
    # Close any existing connections
    await close_db()
    
    # Initialize fresh database connection
    init_db()
    
    # Initialize loader
    loader = HFDatasetLoader()
    
    # Load dataset based on type
    if dataset_name.lower() in ["rajpurkar/squad", "squad"]:
        records = loader.load_squad_dataset(
            split=split,
            limit=limit,
            streaming=False,
        )
    else:
        records = loader.load_generic_dataset(
            dataset_name=dataset_name,
            split=split,
            limit=limit,
            streaming=False,
        )
    
    logger.info(
        "Dataset loaded from HuggingFace",
        dataset_name=dataset_name,
        record_count=len(records),
    )
    
    # Get database session
    async for db_session in get_db():
        try:
            # Initialize repositories
            document_repo = DocumentRepository(db_session)
            chunk_repo = ChunkRepository(db_session)
            job_repo = JobRepository(db_session)
            chunking_service = ChunkingService()
            
            # Create a master job for tracking
            master_job = await job_repo.create(
                document_id=None,
                job_type=JobType.DOCUMENT_PARSING.value,
                tenant_id=tenant_id,
            )
            
            await job_repo.update_status(
                job_id=master_job.job_id,
                status=JobStatus.PROCESSING.value,
            )
            
            # Process each record
            documents_created = 0
            documents_skipped = 0
            chunks_created = 0
            errors = []
            
            for idx, record in enumerate(records):
                try:
                    # Check for duplicates by content hash
                    existing_doc = await document_repo.get_by_content_hash(
                        content_hash=record["content_hash"],
                        tenant_id=tenant_id,
                    )
                    
                    if existing_doc:
                        documents_skipped += 1
                        logger.debug(
                            "Document already exists, skipping",
                            content_hash=record["content_hash"],
                        )
                        continue
                    
                    # Create document record
                    document = await document_repo.create_document(
                        tenant_id=tenant_id,
                        filename=f"{dataset_name.replace('/', '_')}_{split}_{idx}.txt",
                        file_type="text/plain",
                        file_size=len(record["text"].encode()),
                        storage_path=f"hf://{dataset_name}/{split}/{idx}",
                        content_hash=record["content_hash"],
                        mime_type="text/plain",
                        uploaded_by=user_id,
                        document_metadata=record["metadata"],
                    )
                    
                    documents_created += 1
                    
                    # Chunk the text
                    chunks = chunking_service.chunk_document(
                        text=record["text"],
                        document_id=document.document_id,
                    )
                    
                    # Store chunks
                    for chunk_data in chunks:
                        await chunk_repo.create_chunk(
                            document_id=document.document_id,
                            tenant_id=tenant_id,
                            chunk_index=chunk_data.chunk_index,
                            content=chunk_data.content,
                            chunk_type=chunk_data.chunk_type,
                            token_count=chunk_data.token_count,
                        )
                        chunks_created += 1
                    
                    # Update document status
                    await document_repo.update_document_status(
                        document_id=document.document_id,
                        status=ProcessingStatus.PARSED.value,
                    )
                    
                    # Trigger embedding generation
                    from src.ingestion_parsing.tasks.embedding_tasks import trigger_embedding_generation
                    trigger_embedding_generation(document.document_id)
                    
                    # Update progress
                    progress = int((idx + 1) / len(records) * 100)
                    await job_repo.update_status(
                        job_id=master_job.job_id,
                        status=JobStatus.PROCESSING.value,
                        progress_percent=progress,
                    )
                    
                except Exception as e:
                    error_msg = f"Failed to process record {idx}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(
                        "Failed to process dataset record",
                        record_index=idx,
                        error=str(e),
                    )
            
            # Update master job status
            await job_repo.update_status(
                job_id=master_job.job_id,
                status=JobStatus.COMPLETED.value if not errors else JobStatus.FAILED.value,
                progress_percent=100,
            )
            
            result = {
                "job_id": master_job.job_id,
                "dataset_name": dataset_name,
                "split": split,
                "total_records": len(records),
                "documents_created": documents_created,
                "documents_skipped": documents_skipped,
                "chunks_created": chunks_created,
                "errors": errors[:10],  # Limit error list
                "error_count": len(errors),
            }
            
            logger.info(
                "HF dataset import completed",
                result=result,
            )
            
            return result
            
        finally:
            # Ensure session is closed
            await db_session.close()
    
    return {"error": "Failed to get database session"}


def trigger_hf_dataset_import(
    dataset_name: str,
    tenant_id: int,
    split: str = "train",
    limit: int | None = None,
    user_id: int | None = None,
) -> str:
    """Trigger HuggingFace dataset import task.
    
    Args:
        dataset_name: HuggingFace dataset identifier
        tenant_id: Tenant ID
        split: Dataset split
        limit: Record limit
        user_id: User ID
        
    Returns:
        Dramatiq message ID for tracking
    """
    message = import_hf_dataset_task.send(
        dataset_name=dataset_name,
        tenant_id=tenant_id,
        split=split,
        limit=limit,
        user_id=user_id,
    )
    return message.message_id
