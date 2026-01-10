"""API routes for document upload and management."""

import math
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile, status
from fastapi.responses import JSONResponse

import structlog

from src.api.dependencies import (
    get_document_repository,
    get_file_storage,
    get_job_repository,
    get_quota_manager,
    get_upload_session_repository,
)
from src.ingestion_parsing.models.upload_request import (
    BatchUploadResponse,
    BatchUploadResult,
    ChunkUploadResponse,
    ResumableUploadInit,
    ResumableUploadSession,
    UploadResponse,
)
from src.ingestion_parsing.services.upload_service import UploadService
from src.ingestion_parsing.storage.file_storage import FileStorage
from src.ingestion_parsing.storage.quota_manager import QuotaManager
from src.shared.exceptions import (
    FileTooLargeError,
    FileTypeNotAllowedError,
    MalwareScanFailedError,
    QuotaExceededError,
)
from src.storage_indexing.repositories.document_repository import DocumentRepository
from src.storage_indexing.repositories.job_repository import JobRepository
from src.storage_indexing.repositories.upload_session_repository import (
    UploadSessionRepository,
)

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=UploadResponse)
async def upload_document(
    file: Annotated[UploadFile, File(description="File to upload")],
    tenant_id: Annotated[int, Form(description="Tenant ID", gt=0)],
    user_id: Annotated[int | None, Form(description="User ID", gt=0)] = None,
    storage: FileStorage = Depends(get_file_storage),
    quota_manager: QuotaManager = Depends(get_quota_manager),
    document_repo: DocumentRepository = Depends(get_document_repository),
    job_repo: JobRepository = Depends(get_job_repository),
) -> UploadResponse:
    """Upload a single document.
    
    Handles multipart/form-data file upload with validation, storage, and processing job creation.
    
    Args:
        file: Uploaded file
        tenant_id: Tenant ID for isolation
        user_id: User ID who initiated upload (optional)
        storage: File storage backend (injected)
        quota_manager: Quota manager (injected)
        document_repo: Document repository (injected)
        job_repo: Job repository (injected)
        
    Returns:
        UploadResponse with document and job details
        
    Raises:
        HTTPException 400: Invalid file type
        HTTPException 413: File too large or quota exceeded
        HTTPException 422: Validation error
    """
    logger.info(
        "Document upload initiated",
        filename=file.filename,
        content_type=file.content_type,
        tenant_id=tenant_id,
        user_id=user_id,
    )
    
    try:
        # Initialize upload service
        upload_service = UploadService(
            storage=storage,
            quota_manager=quota_manager,
            document_repo=document_repo,
            job_repo=job_repo,
        )
        
        # Upload and process file
        document, job = await upload_service.upload_file(
            file=file.file,
            filename=file.filename or "unnamed_file",
            tenant_id=tenant_id,
            user_id=user_id,
        )
        
        # Build response
        response = UploadResponse(
            document_id=document.document_id,
            filename=document.filename,
            original_filename=document.original_filename,
            file_size=document.file_size,
            mime_type=document.mime_type,
            content_hash=document.content_hash,
            job_id=job.job_id,
            status=document.processing_status,
        )
        
        logger.info(
            "Document uploaded successfully",
            document_id=document.document_id,
            job_id=job.job_id,
            tenant_id=tenant_id,
        )
        
        return response
        
    except FileTypeNotAllowedError as e:
        logger.warning(
            "Upload rejected: file type not allowed",
            filename=file.filename,
            file_type=e.file_type,
            tenant_id=tenant_id,
        )
        raise
        
    except FileTooLargeError as e:
        logger.warning(
            "Upload rejected: file too large",
            filename=file.filename,
            file_size=e.file_size,
            max_size=e.max_size,
            tenant_id=tenant_id,
        )
        raise
        
    except QuotaExceededError as e:
        logger.warning(
            "Upload rejected: quota exceeded",
            filename=file.filename,
            tenant_id=tenant_id,
            used_bytes=e.used_bytes,
            quota_bytes=e.quota_bytes,
        )
        raise
        
    except MalwareScanFailedError as e:
        logger.error(
            "Upload rejected: malware detected",
            filename=file.filename,
            virus_name=e.virus_name,
            tenant_id=tenant_id,
        )
        raise
        
    except Exception as e:
        logger.error(
            "Upload failed with unexpected error",
            filename=file.filename,
            tenant_id=tenant_id,
            error=str(e),
            exception_type=type(e).__name__,
        )
        raise


@router.post("/batch-upload", status_code=status.HTTP_200_OK, response_model=BatchUploadResponse)
async def batch_upload_documents(
    files: Annotated[list[UploadFile], File(description="Multiple files to upload")],
    tenant_id: Annotated[int, Form(description="Tenant ID", gt=0)],
    user_id: Annotated[int | None, Form(description="User ID", gt=0)] = None,
    storage: FileStorage = Depends(get_file_storage),
    quota_manager: QuotaManager = Depends(get_quota_manager),
    document_repo: DocumentRepository = Depends(get_document_repository),
    job_repo: JobRepository = Depends(get_job_repository),
) -> BatchUploadResponse:
    """Upload multiple documents in a batch.
    
    Processes files sequentially, continuing even if individual files fail.
    Returns detailed status for each file.
    
    Args:
        files: List of files to upload
        tenant_id: Tenant ID for isolation
        user_id: User ID who initiated upload (optional)
        storage: File storage backend (injected)
        quota_manager: Quota manager (injected)
        document_repo: Document repository (injected)
        job_repo: Job repository (injected)
        
    Returns:
        BatchUploadResponse with summary and individual file results
        
    Raises:
        HTTPException 400: Batch size exceeds limit or validation error
    """
    logger.info(
        "Batch upload initiated",
        file_count=len(files),
        tenant_id=tenant_id,
        user_id=user_id,
    )
    
    # Validate batch size (max 10 files)
    max_batch_size = 10
    if len(files) > max_batch_size:
        logger.warning(
            "Batch upload rejected: size limit exceeded",
            file_count=len(files),
            max_size=max_batch_size,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "type": "batch_size_exceeded",
                    "message": f"Batch size {len(files)} exceeds maximum of {max_batch_size} files",
                }
            },
        )
    
    try:
        # Initialize upload service
        upload_service = UploadService(
            storage=storage,
            quota_manager=quota_manager,
            document_repo=document_repo,
            job_repo=job_repo,
        )
        
        # Prepare files for batch upload
        file_list = [(file.file, file.filename or f"file_{i}") for i, file in enumerate(files)]
        
        # Execute batch upload
        results = await upload_service.batch_upload(
            files=file_list,
            tenant_id=tenant_id,
            user_id=user_id,
            max_batch_size=max_batch_size,
        )
        
        # Build response
        batch_results = [
            BatchUploadResult(**result) for result in results["results"]
        ]
        
        response = BatchUploadResponse(
            batch_id=results["batch_id"],
            total=results["total"],
            successful=results["successful"],
            failed=results["failed"],
            results=batch_results,
        )
        
        logger.info(
            "Batch upload completed",
            batch_id=results["batch_id"],
            total=results["total"],
            successful=results["successful"],
            failed=results["failed"],
        )
        
        return response
        
    except ValueError as e:
        logger.warning("Batch upload validation failed", error=str(e))
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "type": "validation_error",
                    "message": str(e),
                }
            },
        )
        
    except QuotaExceededError as e:
        logger.warning(
            "Batch upload rejected: quota exceeded",
            tenant_id=tenant_id,
            error=str(e),
        )
        raise
        
    except Exception as e:
        logger.error(
            "Batch upload failed with unexpected error",
            tenant_id=tenant_id,
            error=str(e),
            exception_type=type(e).__name__,
        )
        raise


@router.get("/{document_id}", status_code=status.HTTP_200_OK)
async def get_document(
    document_id: int,
    tenant_id: int,
    document_repo: DocumentRepository = Depends(get_document_repository),
) -> JSONResponse:
    """Get document metadata by ID.
    
    Args:
        document_id: Document ID
        tenant_id: Tenant ID for isolation
        document_repo: Document repository (injected)
        
    Returns:
        Document metadata
        
    Raises:
        HTTPException 404: Document not found
    """
    document = await document_repo.get_by_id(document_id, tenant_id)
    
    if not document:
        logger.warning("Document not found", document_id=document_id, tenant_id=tenant_id)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": {"type": "not_found", "message": "Document not found"}},
        )
    
    return JSONResponse(
        content={
            "document_id": document.document_id,
            "filename": document.filename,
            "original_filename": document.original_filename,
            "file_type": document.file_type,
            "mime_type": document.mime_type,
            "file_size": document.file_size,
            "processing_status": document.processing_status,
            "content_hash": document.content_hash,
            "uploaded_at": document.created_at.isoformat() if document.created_at else None,
            "language": document.language,
            "page_count": document.page_count,
        }
    )


@router.get("", status_code=status.HTTP_200_OK)
async def list_documents(
    tenant_id: Annotated[int, Query(description="Tenant ID for filtering")],
    page: Annotated[int, Query(description="Page number", ge=1)] = 1,
    limit: Annotated[int, Query(description="Items per page", ge=1, le=100)] = 20,
    status_filter: Annotated[str | None, Query(description="Filter by processing status")] = None,
    file_type: Annotated[str | None, Query(description="Filter by file type (pdf, docx, txt)")] = None,
    document_repo: DocumentRepository = Depends(get_document_repository),
) -> JSONResponse:
    """List documents with pagination and filtering.
    
    Supports pagination and filtering by status and file type.
    
    Args:
        tenant_id: Tenant ID for isolation
        page: Page number (1-indexed)
        limit: Number of items per page (1-100)
        status_filter: Filter by processing status (optional)
        file_type: Filter by file type (optional)
        document_repo: Document repository (injected)
        
    Returns:
        Paginated list of documents
        
    Example:
        GET /api/v1/documents?tenant_id=1&page=1&limit=20&status=uploaded&file_type=pdf
    """
    logger.info(
        "Listing documents",
        tenant_id=tenant_id,
        page=page,
        limit=limit,
        status_filter=status_filter,
        file_type=file_type,
    )
    
    # For now, return a placeholder response
    # Full implementation would query the database with filters
    
    return JSONResponse(
        content={
            "documents": [],
            "page": page,
            "limit": limit,
            "total": 0,
            "total_pages": 0,
            "filters": {
                "status": status_filter,
                "file_type": file_type,
            },
        }
    )


# ============================================================================
# Resumable Upload Endpoints (T120, T122, T130-T131)
# ============================================================================


@router.post("/upload/resumable", status_code=status.HTTP_200_OK, response_model=ResumableUploadSession)
async def init_resumable_upload(
    request: ResumableUploadInit,
    session_repo: UploadSessionRepository = Depends(get_upload_session_repository),
    quota_manager: QuotaManager = Depends(get_quota_manager),
) -> ResumableUploadSession:
    """Initialize a resumable upload session for large files.
    
    Creates an upload session that allows files to be uploaded in chunks
    and resumed if interrupted.
    
    Args:
        request: Resumable upload initialization request
        session_repo: Upload session repository (injected)
        quota_manager: Quota manager (injected)
        
    Returns:
        Created upload session with session ID and upload URL
        
    Raises:
        HTTPException 413: Quota exceeded
    """
    logger.info(
        "Initializing resumable upload",
        filename=request.filename,
        file_size=request.file_size,
        tenant_id=request.tenant_id,
    )
    
    # Check quota
    try:
        await quota_manager.check_quota(
            tenant_id=request.tenant_id,
            file_size=request.file_size,
        )
    except QuotaExceededError as e:
        logger.warning(
            "Resumable upload rejected: quota exceeded",
            tenant_id=request.tenant_id,
            file_size=request.file_size,
        )
        raise
    
    # Create session
    session = await session_repo.create(
        filename=request.filename,
        total_size_bytes=request.file_size,
        tenant_id=request.tenant_id,
        user_id=request.user_id or 1,  # Default to user 1 if not provided
        chunk_size_bytes=request.chunk_size,
    )
    
    # Calculate total chunks
    total_chunks = math.ceil(request.file_size / request.chunk_size)
    
    return ResumableUploadSession(
        session_id=str(session.session_id),
        filename=session.filename,
        file_size=session.total_size_bytes,
        chunk_size=session.chunk_size_bytes,
        total_chunks=total_chunks,
        uploaded_bytes=session.uploaded_size_bytes,
        status=session.status,
        upload_url=f"/api/v1/documents/upload/resumable/{session.session_id}",
        expires_at=session.expires_at.isoformat(),
        created_at=session.created_at.isoformat(),
    )


@router.patch("/upload/resumable/{session_id}", status_code=status.HTTP_200_OK, response_model=ChunkUploadResponse)
async def upload_chunk(
    session_id: str,
    request: Request,
    session_repo: UploadSessionRepository = Depends(get_upload_session_repository),
    storage: FileStorage = Depends(get_file_storage),
    document_repo: DocumentRepository = Depends(get_document_repository),
    job_repo: JobRepository = Depends(get_job_repository),
    quota_manager: QuotaManager = Depends(get_quota_manager),
) -> ChunkUploadResponse:
    """Upload a chunk of a resumable upload session.
    
    Accepts a chunk of data with Content-Range header specifying the byte range.
    When all chunks are uploaded, automatically merges them and creates the document.
    
    Args:
        session_id: Upload session identifier
        request: HTTP request with chunk data and Content-Range header
        session_repo: Upload session repository (injected)
        storage: File storage (injected)
        document_repo: Document repository (injected)
        job_repo: Job repository (injected)
        quota_manager: Quota manager (injected)
        
    Returns:
        Upload progress with current status
        
    Raises:
        HTTPException 404: Session not found
        HTTPException 410: Session expired or cancelled
        HTTPException 400: Invalid Content-Range header
    """
    from src.shared.config import settings
    
    # Get session
    session = await session_repo.get_by_id(session_id)
    if not session:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": {"type": "not_found", "message": "Upload session not found"}},
        )
    
    # Check session status
    if session.status in ["expired", "cancelled"]:
        return JSONResponse(
            status_code=status.HTTP_410_GONE,
            content={"error": {"type": "session_expired", "message": f"Upload session is {session.status}"}},
        )
    
    # Parse Content-Range header (e.g., "bytes 0-4999999/10000000")
    content_range = request.headers.get("Content-Range", "")
    if not content_range.startswith("bytes "):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": {"type": "invalid_header", "message": "Missing or invalid Content-Range header"}},
        )
    
    try:
        range_part, total_part = content_range[6:].split("/")
        start, end = map(int, range_part.split("-"))
        total_size = int(total_part)
    except (ValueError, IndexError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": {"type": "invalid_header", "message": "Invalid Content-Range format"}},
        )
    
    # Read chunk data
    chunk_data = await request.body()
    chunk_number = start // session.chunk_size_bytes
    
    # Create chunk directory
    chunk_dir = Path(settings.upload_dir) / "tmp" / session_id
    chunk_dir.mkdir(parents=True, exist_ok=True)
    
    # Save chunk
    chunk_file = chunk_dir / f"chunk_{chunk_number}"
    async with aiofiles.open(chunk_file, "wb") as f:
        await f.write(chunk_data)
    
    # Update progress
    new_uploaded_bytes = session.uploaded_size_bytes + len(chunk_data)
    await session_repo.update_progress(
        session_id=session_id,
        uploaded_bytes=new_uploaded_bytes,
        status="uploading",
    )
    
    progress_percent = (new_uploaded_bytes / session.total_size_bytes) * 100
    
    logger.info(
        "Chunk uploaded",
        session_id=session_id,
        chunk_number=chunk_number,
        chunk_size=len(chunk_data),
        progress_percent=progress_percent,
    )
    
    # Check if upload is complete
    if new_uploaded_bytes >= session.total_size_bytes:
        logger.info("All chunks uploaded, starting merge", session_id=session_id)
        
        # Merge chunks
        upload_service = UploadService(
            storage=storage,
            quota_manager=quota_manager,
            document_repo=document_repo,
            job_repo=job_repo,
        )
        
        total_chunks = math.ceil(session.total_size_bytes / session.chunk_size_bytes)
        try:
            merged_file = await upload_service.merge_chunks(
                session_id=str(session_id),
                chunk_dir=chunk_dir,
                num_chunks=total_chunks,
                expected_hash=None,  # No hash validation for now
            )
            
            # Upload merged file and create document
            with open(merged_file, "rb") as f:
                document, job = await upload_service.upload_file(
                    file=f,
                    filename=session.filename,
                    tenant_id=session.tenant_id,
                    user_id=session.user_id,
                )
            
            # Clean up chunks
            await upload_service.cleanup_chunks(chunk_dir)
            
            # Mark session complete
            await session_repo.mark_complete(session_id=session_id, document_id=document.document_id)
            
            return ChunkUploadResponse(
                session_id=session_id,
                uploaded_bytes=session.total_size_bytes,
                total_bytes=session.total_size_bytes,
                progress_percent=100.0,
                status="complete",
                document_id=document.document_id,
                job_id=job.job_id,
            )
            
        except Exception as e:
            logger.error("Chunk merge failed", session_id=session_id, error=str(e))
            await upload_service.cleanup_chunks(chunk_dir)
            raise
    
    return ChunkUploadResponse(
        session_id=session_id,
        uploaded_bytes=new_uploaded_bytes,
        total_bytes=session.total_size_bytes,
        progress_percent=progress_percent,
        status="uploading",
    )


@router.get("/upload/resumable/{session_id}", status_code=status.HTTP_200_OK, response_model=ResumableUploadSession)
async def get_resumable_upload_progress(
    session_id: str,
    session_repo: UploadSessionRepository = Depends(get_upload_session_repository),
) -> ResumableUploadSession:
    """Get the progress of a resumable upload session.
    
    Args:
        session_id: Upload session identifier
        session_repo: Upload session repository (injected)
        
    Returns:
        Upload session with current progress
        
    Raises:
        HTTPException 404: Session not found
    """
    session = await session_repo.get_by_id(session_id)
    if not session:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": {"type": "not_found", "message": "Upload session not found"}},
        )
    
    total_chunks = math.ceil(session.total_size_bytes / session.chunk_size_bytes)
    
    return ResumableUploadSession(
        session_id=str(session.session_id),
        filename=session.filename,
        file_size=session.total_size_bytes,
        chunk_size=session.chunk_size_bytes,
        total_chunks=total_chunks,
        uploaded_bytes=session.uploaded_size_bytes,
        status=session.status,
        upload_url=f"/api/v1/documents/upload/resumable/{session.session_id}",
        expires_at=session.expires_at.isoformat(),
        created_at=session.created_at.isoformat(),
    )


@router.delete("/upload/resumable/{session_id}", status_code=status.HTTP_200_OK)
async def cancel_resumable_upload(
    session_id: str,
    session_repo: UploadSessionRepository = Depends(get_upload_session_repository),
    storage: FileStorage = Depends(get_file_storage),
) -> JSONResponse:
    """Cancel a resumable upload session and clean up chunks.
    
    Args:
        session_id: Upload session identifier
        session_repo: Upload session repository (injected)
        storage: File storage (injected)
        
    Returns:
        Cancellation confirmation
        
    Raises:
        HTTPException 404: Session not found
    """
    from src.shared.config import settings
    
    session = await session_repo.get_by_id(session_id)
    if not session:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": {"type": "not_found", "message": "Upload session not found"}},
        )
    
    # Mark as cancelled
    await session_repo.mark_cancelled(session_id)
    
    # Clean up chunks
    chunk_dir = Path(settings.upload_dir) / "tmp" / session_id
    upload_service = UploadService(
        storage=storage,
        quota_manager=None,  # Not needed for cleanup
        document_repo=None,
        job_repo=None,
    )
    await upload_service.cleanup_chunks(chunk_dir)
    
    logger.info("Resumable upload cancelled", session_id=session_id)
    
    return JSONResponse(
        content={
            "session_id": session_id,
            "status": "cancelled",
            "message": "Upload session cancelled and cleaned up",
        }
    )
