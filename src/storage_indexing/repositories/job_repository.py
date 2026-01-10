"""Processing job repository for status tracking."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import structlog

from src.storage_indexing.models import ProcessingJob, ProcessingStatus

logger = structlog.get_logger(__name__)


class JobRepository:
    """Repository for processing job database operations.
    
    Handles CRUD operations for processing jobs and status tracking.
    
    Example:
        >>> repo = JobRepository(db_session)
        >>> job = await repo.create(
        ...     document_id=123,
        ...     job_type="parsing",
        ...     started_by=5,
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
        job_type: str,
        started_by: int | None = None,
    ) -> ProcessingJob:
        """Create a new processing job.
        
        Args:
            document_id: Document ID being processed
            job_type: Type of job (parsing, chunking, embedding, etc.)
            started_by: User ID who started the job
            
        Returns:
            Created ProcessingJob instance
        """
        job = ProcessingJob(
            document_id=document_id,
            job_type=job_type,
            status=ProcessingStatus.PENDING.value,
            started_by=started_by,
            progress_percent=0,
        )
        
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        
        logger.info(
            "Processing job created",
            job_id=job.job_id,
            document_id=document_id,
            job_type=job_type,
        )
        
        return job

    async def get_by_id(self, job_id: int) -> ProcessingJob | None:
        """Get job by ID.
        
        Args:
            job_id: Job ID
            
        Returns:
            ProcessingJob instance or None if not found
        """
        return await self.db.get(ProcessingJob, job_id)

    async def update_status(
        self,
        job_id: int,
        status: str,
        progress_percent: int | None = None,
        estimated_time_remaining: int | None = None,
        error_message: str | None = None,
    ) -> ProcessingJob | None:
        """Update job status and progress.
        
        Args:
            job_id: Job ID
            status: New status
            progress_percent: Progress percentage (0-100)
            estimated_time_remaining: Estimated seconds remaining
            error_message: Error message if status is FAILED
            
        Returns:
            Updated ProcessingJob instance or None if not found
        """
        job = await self.get_by_id(job_id)
        if not job:
            return None
        
        job.status = status
        if progress_percent is not None:
            job.progress_percent = progress_percent
        if estimated_time_remaining is not None:
            job.estimated_time_remaining = estimated_time_remaining
        if error_message:
            job.error_message = error_message
        
        # Update timestamps based on status
        if status == ProcessingStatus.PROCESSING.value and not job.started_at:
            job.started_at = datetime.now(UTC)
        elif status in [ProcessingStatus.COMPLETED.value, ProcessingStatus.FAILED.value]:
            job.completed_at = datetime.now(UTC)
        
        await self.db.commit()
        await self.db.refresh(job)
        
        logger.info(
            "Job status updated",
            job_id=job_id,
            status=status,
            progress_percent=progress_percent,
        )
        
        return job

    async def get_by_document(self, document_id: int) -> list[ProcessingJob]:
        """Get all jobs for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            List of ProcessingJob instances ordered by creation time
        """
        result = await self.db.execute(
            select(ProcessingJob)
            .where(ProcessingJob.document_id == document_id)
            .order_by(ProcessingJob.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_pending_jobs(self, limit: int = 10) -> list[ProcessingJob]:
        """Get pending jobs for processing.
        
        Args:
            limit: Maximum number of jobs to return
            
        Returns:
            List of pending ProcessingJob instances
        """
        result = await self.db.execute(
            select(ProcessingJob)
            .where(ProcessingJob.status == ProcessingStatus.PENDING.value)
            .order_by(ProcessingJob.created_at)
            .limit(limit)
        )
        return list(result.scalars().all())
