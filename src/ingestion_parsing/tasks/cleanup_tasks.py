"""Periodic cleanup tasks for expired upload sessions and temporary files.

This module contains Dramatiq actors for background cleanup operations.
"""

import asyncio
from pathlib import Path

import dramatiq
import structlog

from src.ingestion_parsing.services.upload_service import UploadService
from src.shared.config import settings
from src.storage_indexing.database import engine
from sqlalchemy.ext.asyncio import AsyncSession
from src.storage_indexing.repositories.upload_session_repository import (
    UploadSessionRepository,
)

logger = structlog.get_logger(__name__)


@dramatiq.actor(
    time_limit=300_000,  # 5 minutes
    max_retries=3,
)
def cleanup_expired_sessions() -> dict[str, int]:
    """Clean up expired upload sessions and their temporary files.
    
    This task runs periodically to:
    1. Find upload sessions that have expired (> 24 hours old)
    2. Mark them as expired in the database
    3. Delete their temporary chunk files
    
    Returns:
        Dictionary with cleanup statistics
        
    Example:
        >>> cleanup_expired_sessions.send()  # Enqueue task
        >>> # Or run periodically with cron/scheduler
    """
    return asyncio.run(_cleanup_expired_sessions_async())


async def _cleanup_expired_sessions_async() -> dict[str, int]:
    """Async implementation of expired session cleanup.
    
    Returns:
        Dictionary with counts: expired, cleaned, failed
    """
    logger.info("Starting expired sessions cleanup")
    
    expired_count = 0
    cleaned_count = 0
    failed_count = 0
    
    async with AsyncSession(engine) as db:
        session_repo = UploadSessionRepository(db)
        
        # Get expired sessions
        expired_sessions = await session_repo.get_expired_sessions()
        expired_count = len(expired_sessions)
        
        logger.info(
            "Found expired sessions",
            count=expired_count,
        )
        
        # Process each expired session
        for session in expired_sessions:
            try:
                # Mark as expired
                await session_repo.mark_expired(str(session.session_id))
                
                # Clean up chunk directory
                chunk_dir = Path(settings.upload_dir) / "tmp" / str(session.session_id)
                if chunk_dir.exists():
                    upload_service = UploadService(
                        storage=None,
                        quota_manager=None,
                        document_repo=None,
                        job_repo=None,
                    )
                    await upload_service.cleanup_chunks(chunk_dir)
                    cleaned_count += 1
                    
                logger.info(
                    "Cleaned up expired session",
                    session_id=str(session.session_id),
                    filename=session.filename,
                )
                
            except Exception as e:
                failed_count += 1
                logger.error(
                    "Failed to clean up expired session",
                    session_id=str(session.session_id),
                    error=str(e),
                )
    
    result = {
        "expired": expired_count,
        "cleaned": cleaned_count,
        "failed": failed_count,
    }
    
    logger.info(
        "Expired sessions cleanup completed",
        **result,
    )
    
    return result


@dramatiq.actor(
    time_limit=600_000,  # 10 minutes
    max_retries=3,
)
def cleanup_temp_files() -> dict[str, int]:
    """Clean up orphaned temporary files.
    
    Removes temporary files that are older than 24 hours and not associated
    with any active upload session.
    
    Returns:
        Dictionary with cleanup statistics
    """
    return asyncio.run(_cleanup_temp_files_async())


async def _cleanup_temp_files_async() -> dict[str, int]:
    """Async implementation of temporary files cleanup.
    
    Returns:
        Dictionary with counts: scanned, deleted, failed
    """
    import time
    
    logger.info("Starting temporary files cleanup")
    
    temp_dir = Path(settings.upload_dir) / "tmp"
    if not temp_dir.exists():
        logger.info("Temporary directory does not exist", temp_dir=str(temp_dir))
        return {"scanned": 0, "deleted": 0, "failed": 0}
    
    scanned_count = 0
    deleted_count = 0
    failed_count = 0
    
    # Find directories older than 24 hours
    current_time = time.time()
    max_age_seconds = 24 * 60 * 60  # 24 hours
    
    for session_dir in temp_dir.iterdir():
        if not session_dir.is_dir():
            continue
            
        scanned_count += 1
        
        try:
            # Check directory age
            dir_age = current_time - session_dir.stat().st_mtime
            
            if dir_age > max_age_seconds:
                # Delete directory and contents
                for file in session_dir.iterdir():
                    file.unlink()
                session_dir.rmdir()
                deleted_count += 1
                
                logger.info(
                    "Deleted orphaned temp directory",
                    directory=session_dir.name,
                    age_hours=dir_age / 3600,
                )
                
        except Exception as e:
            failed_count += 1
            logger.error(
                "Failed to clean up temp directory",
                directory=session_dir.name,
                error=str(e),
            )
    
    result = {
        "scanned": scanned_count,
        "deleted": deleted_count,
        "failed": failed_count,
    }
    
    logger.info(
        "Temporary files cleanup completed",
        **result,
    )
    
    return result


# Schedule cleanup tasks (example using APScheduler or similar)
def schedule_cleanup_tasks() -> None:
    """Schedule periodic cleanup tasks.
    
    This function should be called on application startup to schedule
    periodic cleanup tasks using a task scheduler like APScheduler.
    
    Example:
        >>> from apscheduler.schedulers.background import BackgroundScheduler
        >>> scheduler = BackgroundScheduler()
        >>> scheduler.add_job(
        ...     cleanup_expired_sessions.send,
        ...     'interval',
        ...     hours=1,
        ...     id='cleanup_expired_sessions',
        ... )
        >>> scheduler.start()
    """
    logger.info("Cleanup tasks scheduling should be configured in production")
    # Implementation depends on your task scheduler
    # Options: APScheduler, Celery Beat, Kubernetes CronJob, etc.
