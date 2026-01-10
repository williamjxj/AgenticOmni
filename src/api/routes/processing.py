"""API routes for processing job status tracking."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

import structlog

from src.api.dependencies import get_job_repository
from src.ingestion_parsing.tasks.document_tasks import trigger_document_parsing
from src.storage_indexing.models import ProcessingStatus
from src.storage_indexing.repositories.job_repository import JobRepository

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/v1/processing", tags=["processing"])


@router.get("/jobs/{job_id}", status_code=status.HTTP_200_OK)
async def get_job_status(
    job_id: int,
    tenant_id: Annotated[int | None, Query(description="Tenant ID for isolation")] = None,
    job_repo: JobRepository = Depends(get_job_repository),
) -> JSONResponse:
    """Get processing job status and progress.
    
    Returns current status, progress percentage, and estimated time remaining
    for a processing job.
    
    Args:
        job_id: Job ID
        tenant_id: Tenant ID for isolation (optional, for future multi-tenancy)
        job_repo: Job repository (injected)
        
    Returns:
        Job status information
        
    Raises:
        HTTPException 404: Job not found
    """
    logger.info("Getting job status", job_id=job_id, tenant_id=tenant_id)
    
    job = await job_repo.get_by_id(job_id)
    
    if not job:
        logger.warning("Job not found", job_id=job_id)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": {"type": "not_found", "message": "Job not found"}},
        )
    
    # TODO: Add tenant isolation check when authentication is implemented
    # if tenant_id and job.document.tenant_id != tenant_id:
    #     return JSONResponse(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         content={"error": {"type": "forbidden", "message": "Access denied"}},
    #     )
    
    # Build response
    response_data = {
        "job_id": job.job_id,
        "document_id": job.document_id,
        "job_type": job.job_type,
        "status": job.status,
        "progress_percent": job.progress_percent or 0,
        "estimated_time_remaining": job.estimated_time_remaining,
        "error_message": job.error_message,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
    }
    
    logger.info(
        "Job status retrieved",
        job_id=job_id,
        status=job.status,
        progress=job.progress_percent,
    )
    
    return JSONResponse(content=response_data)


@router.post("/jobs/{job_id}/retry", status_code=status.HTTP_200_OK)
async def retry_job(
    job_id: int,
    job_repo: JobRepository = Depends(get_job_repository),
) -> JSONResponse:
    """Retry a failed processing job.
    
    Resets job status to pending and triggers reprocessing.
    
    Args:
        job_id: Job ID
        job_repo: Job repository (injected)
        
    Returns:
        Success message
        
    Raises:
        HTTPException 404: Job not found
        HTTPException 400: Job not in failed state
    """
    logger.info("Retrying job", job_id=job_id)
    
    job = await job_repo.get_by_id(job_id)
    
    if not job:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": {"type": "not_found", "message": "Job not found"}},
        )
    
    # Check if job can be retried
    if job.status not in [ProcessingStatus.FAILED.value, ProcessingStatus.CANCELLED.value]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "type": "invalid_state",
                    "message": f"Job cannot be retried in current state: {job.status}",
                }
            },
        )
    
    # Reset job status
    await job_repo.update_status(
        job_id=job_id,
        status=ProcessingStatus.PENDING.value,
        progress_percent=0,
        error_message=None,
    )
    
    # Trigger reprocessing
    trigger_document_parsing(job.document_id)
    
    logger.info("Job retry triggered", job_id=job_id, document_id=job.document_id)
    
    return JSONResponse(
        content={
            "message": "Job retry triggered successfully",
            "job_id": job_id,
            "status": ProcessingStatus.PENDING.value,
        }
    )


@router.post("/jobs/{job_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_job(
    job_id: int,
    job_repo: JobRepository = Depends(get_job_repository),
) -> JSONResponse:
    """Cancel a processing job.
    
    Marks job as cancelled if it's in pending or processing state.
    
    Args:
        job_id: Job ID
        job_repo: Job repository (injected)
        
    Returns:
        Success message
        
    Raises:
        HTTPException 404: Job not found
        HTTPException 400: Job cannot be cancelled
    """
    logger.info("Cancelling job", job_id=job_id)
    
    job = await job_repo.get_by_id(job_id)
    
    if not job:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": {"type": "not_found", "message": "Job not found"}},
        )
    
    # Check if job can be cancelled
    if job.status in [ProcessingStatus.COMPLETED.value, ProcessingStatus.CANCELLED.value]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "type": "invalid_state",
                    "message": f"Job cannot be cancelled in current state: {job.status}",
                }
            },
        )
    
    # Update job status to cancelled
    await job_repo.update_status(
        job_id=job_id,
        status=ProcessingStatus.CANCELLED.value,
    )
    
    logger.info("Job cancelled", job_id=job_id)
    
    return JSONResponse(
        content={
            "message": "Job cancelled successfully",
            "job_id": job_id,
            "status": ProcessingStatus.CANCELLED.value,
        }
    )


@router.get("/jobs", status_code=status.HTTP_200_OK)
async def list_jobs(
    document_id: Annotated[int | None, Query(description="Filter by document ID")] = None,
    status_filter: Annotated[str | None, Query(description="Filter by status")] = None,
    limit: Annotated[int, Query(description="Maximum number of jobs to return", ge=1, le=100)] = 10,
    job_repo: JobRepository = Depends(get_job_repository),
) -> JSONResponse:
    """List processing jobs with optional filters.
    
    Args:
        document_id: Filter by document ID (optional)
        status_filter: Filter by status (optional)
        limit: Maximum number of jobs to return
        job_repo: Job repository (injected)
        
    Returns:
        List of jobs
    """
    logger.info("Listing jobs", document_id=document_id, status_filter=status_filter, limit=limit)
    
    if document_id:
        jobs = await job_repo.get_by_document(document_id)
    else:
        # Get pending jobs as default
        jobs = await job_repo.get_pending_jobs(limit=limit)
    
    # Apply status filter if provided
    if status_filter:
        jobs = [job for job in jobs if job.status == status_filter]
    
    # Limit results
    jobs = jobs[:limit]
    
    # Build response
    jobs_data = []
    for job in jobs:
        jobs_data.append({
            "job_id": job.job_id,
            "document_id": job.document_id,
            "job_type": job.job_type,
            "status": job.status,
            "progress_percent": job.progress_percent or 0,
            "created_at": job.created_at.isoformat() if job.created_at else None,
        })
    
    return JSONResponse(content={"jobs": jobs_data, "count": len(jobs_data)})
