"""API routes for document upload and management."""

import math
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import JSONResponse, StreamingResponse

import structlog

from src.api.dependencies import (
    get_chunk_repository,
    get_document_repository,
    get_file_storage,
    get_job_repository,
    get_quota_manager,
    get_upload_session_repository,
)
from src.storage_indexing.repositories.markdown_repository import (
    ImageReferenceRepository,
    MarkdownMetadataRepository,
)
from src.storage_indexing.repositories.folder_batch_repository import FolderBatchRepository
from src.ingestion_parsing.services.folder_service import FolderService
from src.ingestion_parsing.tasks.folder_tasks import trigger_folder_batch_processing
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
from src.storage_indexing.repositories.chunk_repository import ChunkRepository
from src.storage_indexing.repositories.upload_session_repository import (
    UploadSessionRepository,
)

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])


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
    
    # Determine MIME type, forcing text/markdown for .md files
    detected_mime_type = file.content_type
    filename_lower = (file.filename or "").lower()
    if filename_lower.endswith((".md", ".markdown")):
        detected_mime_type = "text/markdown"
        logger.debug(
            "Forced MIME type to text/markdown for markdown file",
            filename=file.filename,
            original_content_type=file.content_type,
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
        
        # Determine if this is a duplicate (job is None for duplicates with existing processing)
        is_duplicate = job is None
        
        # Build response
        response = UploadResponse(
            document_id=document.document_id,
            filename=document.filename,
            original_filename=document.original_filename,
            file_size=document.file_size,
            mime_type=document.mime_type,
            content_hash=document.content_hash,
            job_id=job.job_id if job else None,
            status=document.processing_status,
            is_duplicate=is_duplicate,
        )
        
        logger.info(
            "Document upload completed",
            document_id=document.document_id,
            job_id=job.job_id if job else None,
            is_duplicate=is_duplicate,
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


@router.get("/{document_id}/download", status_code=status.HTTP_200_OK)
async def download_document(
    document_id: int,
    tenant_id: int,
    document_repo: DocumentRepository = Depends(get_document_repository),
    storage: FileStorage = Depends(get_file_storage),
) -> StreamingResponse:
    """Download the original file for a document.

    Args:
        document_id: Document ID
        tenant_id: Tenant ID for isolation
        document_repo: Document repository (injected)
        storage: File storage backend (injected)

    Returns:
        Streaming file response with Content-Disposition for browser save-as

    Raises:
        HTTPException 404: Document not found or file missing from storage
    """
    document = await document_repo.get_by_id(document_id, tenant_id)

    if not document:
        logger.warning("Document not found for download", document_id=document_id, tenant_id=tenant_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    try:
        file_bytes = await storage.download(document.storage_path)
    except FileNotFoundError:
        logger.error(
            "File not found in storage",
            document_id=document_id,
            storage_path=document.storage_path,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found in storage",
        )

    import io
    from fastapi.responses import StreamingResponse

    content_type = document.mime_type or "application/octet-stream"
    safe_filename = document.original_filename or document.filename

    logger.info(
        "Document download initiated",
        document_id=document_id,
        filename=safe_filename,
        file_size=len(file_bytes),
    )

    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{safe_filename}"',
            "Content-Length": str(len(file_bytes)),
        },
    )


@router.get("/{document_id}/text-preview", status_code=status.HTTP_200_OK)
async def get_document_text_preview(
    document_id: int,
    max_pages: Annotated[int, Query(description="Maximum pages to include", ge=1, le=100)] = 5,
    preview_length: Annotated[int, Query(description="Maximum characters to return", ge=100, le=10000)] = 1000,
    document_repo: DocumentRepository = Depends(get_document_repository),
    chunk_repo: ChunkRepository = Depends(get_chunk_repository),
    request: Request = None,
) -> JSONResponse:
    """Get text preview from document chunks.
    
    Returns a preview of the extracted text from the document's chunks.
    Useful for displaying a preview without downloading the entire document.
    
    Args:
        document_id: Document ID
        max_pages: Maximum number of pages to include
        preview_length: Maximum character length for preview
        document_repo: Document repository (injected)
        chunk_repo: Chunk repository (injected)
        request: FastAPI request for getting DB session
        
    Returns:
        Text preview with metadata
        
    Raises:
        HTTPException 404: Document not found or no chunks available
    """
    # Get tenant_id from query params or headers
    tenant_id = int(request.query_params.get("tenant_id", 1))
    
    # Get document
    document = await document_repo.get_by_id(document_id, tenant_id)
    if not document:
        logger.warning(
            "Document not found for text preview",
            document_id=document_id,
            tenant_id=tenant_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    # Check if document has been parsed
    if document.processing_status != "parsed":
        logger.warning(
            "Document not yet parsed",
            document_id=document_id,
            status=document.processing_status,
        )
        return JSONResponse(
            content={
                "document_id": document_id,
                "status": document.processing_status,
                "preview_text": "",
                "total_chunks": 0,
                "page_count": document.page_count or 0,
                "is_truncated": False,
                "message": "Document has not been parsed yet",
            }
        )
    
    # Get chunks from repository
    chunks = await chunk_repo.get_by_document(document_id)
    
    if not chunks:
        logger.info(
            "No chunks found for document",
            document_id=document_id,
        )
        return JSONResponse(
            content={
                "document_id": document_id,
                "status": "parsed",
                "preview_text": "",
                "total_chunks": 0,
                "page_count": document.page_count or 0,
                "is_truncated": False,
                "message": "No text chunks available",
            }
        )
    
    # Filter chunks by page if needed
    if max_pages and document.page_count:
        chunks = [
            chunk for chunk in chunks
            if chunk.start_page is None or chunk.start_page <= max_pages
        ]
    
    # Sort by chunk order
    chunks.sort(key=lambda c: c.chunk_order)
    
    # Concatenate chunk text
    preview_text = ""
    for chunk in chunks:
        chunk_content = chunk.content_text or ""
        if len(preview_text) + len(chunk_content) > preview_length:
            # Add partial chunk to reach preview_length
            remaining = preview_length - len(preview_text)
            preview_text += chunk_content[:remaining]
            break
        preview_text += chunk_content + "\n\n"
    
    is_truncated = len(preview_text) >= preview_length or (
        max_pages and document.page_count and document.page_count > max_pages
    )
    
    logger.info(
        "Text preview generated",
        document_id=document_id,
        chunks_used=len([c for c in chunks if c.content_text in preview_text]),
        total_chunks=len(chunks),
        preview_length=len(preview_text),
    )
    
    return JSONResponse(
        content={
            "document_id": document_id,
            "status": "parsed",
            "preview_text": preview_text.strip(),
            "total_chunks": len(chunks),
            "page_count": document.page_count or 0,
            "is_truncated": is_truncated,
            "message": "Preview generated successfully",
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
    
    # Build query with filters
    from sqlalchemy import select, func
    from src.storage_indexing.models import Document
    
    query = select(Document).where(Document.tenant_id == tenant_id)
    
    # Apply filters
    if status_filter:
        query = query.where(Document.processing_status == status_filter)
    if file_type:
        query = query.where(Document.file_type == file_type)
    
    # Order by created_at desc
    query = query.order_by(Document.created_at.desc())
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await document_repo.db.scalar(count_query)
    
    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    
    # Execute query
    result = await document_repo.db.execute(query)
    documents = result.scalars().all()
    
    # Calculate total pages
    total_pages = (total + limit - 1) // limit if total > 0 else 0
    
    # Format response
    document_list = [
        {
            "document_id": doc.document_id,
            "original_filename": doc.original_filename,
            "file_type": doc.file_type,
            "file_size": doc.file_size,
            "processing_status": doc.processing_status,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
            "language": doc.language,
            "page_count": doc.page_count,
            "embedding_status": "pending",  # TODO: Add actual embedding status
        }
        for doc in documents
    ]
    
    logger.info(
        "Documents listed",
        tenant_id=tenant_id,
        total=total,
        page=page,
        returned=len(document_list),
    )
    
    return JSONResponse(
        content={
            "documents": document_list,
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
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


@router.get(
    "/{document_id}/markdown-metadata",
    status_code=status.HTTP_200_OK,
)
async def get_markdown_metadata(
    document_id: int,
    request: Request,
    document_repo: DocumentRepository = Depends(get_document_repository),
) -> dict:
    """Get markdown-specific metadata for a document.
    
    Returns frontmatter, structural counts, and other markdown-specific metadata.
    
    Args:
        document_id: Document identifier
        request: FastAPI request (for getting DB session)
        document_repo: Document repository (injected)
        
    Returns:
        Markdown metadata including frontmatter and counts
        
    Raises:
        HTTPException 404: Document or metadata not found
    """
    # Get tenant_id from headers
    tenant_id = int(request.headers.get("X-Tenant-ID", 0))
    
    # Get document
    document = await document_repo.get_by_id(document_id, tenant_id)
    if not document:
        logger.warning(
            "Document not found for metadata request",
            document_id=document_id,
            tenant_id=tenant_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    # Check if markdown metadata exists
    if not document.markdown_metadata:
        logger.warning(
            "Markdown metadata not found",
            document_id=document_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Markdown metadata not found for this document",
        )
    
    metadata = document.markdown_metadata
    
    logger.info(
        "Markdown metadata retrieved",
        document_id=document_id,
        has_frontmatter=metadata.has_yaml_frontmatter,
    )
    
    return {
        "document_id": document_id,
        "frontmatter": metadata.frontmatter,
        "heading_count": metadata.heading_count,
        "code_block_count": metadata.code_block_count,
        "mermaid_diagram_count": metadata.mermaid_diagram_count,
        "table_count": metadata.table_count,
        "link_count": metadata.link_count,
        "image_count": metadata.image_count,
        "link_urls": metadata.link_urls,
        "has_yaml_frontmatter": metadata.has_yaml_frontmatter,
        "created_at": metadata.created_at.isoformat() if metadata.created_at else None,
    }


@router.get(
    "/{document_id}/images",
    status_code=status.HTTP_200_OK,
)
async def get_document_images(
    document_id: int,
    request: Request,
    image_type: str | None = Query(None, description="Filter by image type: local, base64, external"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    document_repo: DocumentRepository = Depends(get_document_repository),
) -> dict:
    """Get image references for a markdown document.
    
    Returns all images referenced in the markdown with their metadata.
    Supports filtering by image type and pagination.
    
    Args:
        document_id: Document identifier
        request: FastAPI request (for getting DB session)
        image_type: Optional filter by type (local, base64, external)
        page: Page number for pagination
        page_size: Items per page
        document_repo: Document repository (injected)
        
    Returns:
        List of image references with metadata
        
    Raises:
        HTTPException 404: Document not found
        HTTPException 400: Invalid image_type filter
    """
    # Get tenant_id from headers
    tenant_id = int(request.headers.get("X-Tenant-ID", 0))
    
    # Validate image_type filter
    if image_type and image_type not in ["local", "base64", "external"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image_type. Must be one of: local, base64, external",
        )
    
    # Get document
    document = await document_repo.get_by_id(document_id, tenant_id)
    if not document:
        logger.warning(
            "Document not found for images request",
            document_id=document_id,
            tenant_id=tenant_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    # Get image references
    images = document.image_references
    
    # Filter by type if specified
    if image_type:
        images = [img for img in images if img.image_type == image_type]
    
    # Sort by position
    images = sorted(images, key=lambda img: img.position_in_document or 0)
    
    # Paginate
    total_count = len(images)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_images = images[start_idx:end_idx]
    
    logger.info(
        "Document images retrieved",
        document_id=document_id,
        total_count=total_count,
        page=page,
        filtered_type=image_type,
    )
    
    return {
        "document_id": document_id,
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total_count / page_size) if total_count > 0 else 0,
        "images": [
            {
                "id": img.id,
                "image_url": img.image_url,
                "alt_text": img.alt_text,
                "image_type": img.image_type,
                "is_local_path": img.is_local_path,
                "is_base64": img.is_base64,
                "is_external_url": img.is_external_url,
                "resolved_path": img.resolved_path,
                "file_size_bytes": img.file_size_bytes,
                "ocr_pending": img.ocr_pending,
                "ocr_completed_at": img.ocr_completed_at.isoformat() if img.ocr_completed_at else None,
                "position_in_document": img.position_in_document,
            }
            for img in paginated_images
        ],
    }


@router.post(
    "/upload-folder",
    status_code=status.HTTP_201_CREATED,
)
async def upload_folder(
    request: Request,
    folder_path: str = Form(..., description="Path to folder containing markdown files"),
    tenant_id: int = Form(..., gt=0, description="Tenant ID"),
    user_id: int | None = Form(None, gt=0, description="User ID"),
) -> dict:
    """Upload an entire folder of markdown files for batch processing.
    
    Recursively discovers all markdown files in the folder and processes them.
    Returns a batch ID for tracking progress.
    
    Args:
        request: FastAPI request
        folder_path: Path to the folder to upload
        tenant_id: Tenant identifier
        user_id: User who initiated the upload
        
    Returns:
        Batch information with batch_id and status_url
        
    Raises:
        HTTPException 400: Invalid folder or no markdown files found
        HTTPException 413: Too many files in folder
    """
    from pathlib import Path
    
    logger.info(
        "Folder upload initiated",
        folder_path=folder_path,
        tenant_id=tenant_id,
        user_id=user_id,
    )
    
    try:
        folder = Path(folder_path)
        
        if not folder.exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Folder not found: {folder_path}",
            )
        
        if not folder.is_dir():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Path is not a directory: {folder_path}",
            )
        
        # Discover markdown files
        folder_service = FolderService()
        markdown_files = await folder_service.discover_markdown_files(folder)
        
        # Check if any files found
        if len(markdown_files) == 0:
            logger.warning("No markdown files found in folder", folder_path=folder_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No markdown files found in folder",
            )
        
        # Check max files limit
        max_files = getattr(settings, "folder_max_files", 500)
        if len(markdown_files) > max_files:
            logger.warning(
                "Too many files in folder",
                folder_path=folder_path,
                file_count=len(markdown_files),
                max_files=max_files,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Folder contains too many files ({len(markdown_files)}). Maximum allowed: {max_files}",
            )
        
        # Create FolderBatch record
        async for db_session in get_db():
            try:
                batch_repo = FolderBatchRepository(db_session)
                
                batch = await folder_service.create_batch(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    folder_path=folder_path,
                    original_folder_name=folder.name,
                )
                
                db_session.add(batch)
                await db_session.commit()
                await db_session.refresh(batch)
                
                # Trigger async processing
                trigger_folder_batch_processing(batch.id, tenant_id)
                
                logger.info(
                    "Folder batch created and processing triggered",
                    batch_id=batch.id,
                    tenant_id=tenant_id,
                    total_files=len(markdown_files),
                )
                
                return {
                    "batch_id": batch.id,
                    "status_url": f"/api/v1/documents/folder-batches/{batch.id}",
                    "folder_name": batch.original_folder_name,
                    "total_files_discovered": len(markdown_files),
                    "status": batch.status,
                    "created_at": batch.created_at.isoformat() if batch.created_at else None,
                }
            
            finally:
                await db_session.close()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Folder upload failed",
            folder_path=folder_path,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Folder upload failed: {str(e)}",
        )


@router.get(
    "/folder-batches/{batch_id}",
    status_code=status.HTTP_200_OK,
)
async def get_folder_batch_status(
    batch_id: int,
    request: Request,
    page: int = Query(1, ge=1, description="Page number for documents list"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> dict:
    """Get folder batch status and progress.
    
    Returns the current status of a folder batch upload, including
    progress tracking and list of processed documents.
    
    Args:
        batch_id: FolderBatch identifier
        request: FastAPI request
        page: Page number for pagination
        page_size: Items per page
        
    Returns:
        Batch status with progress information and documents list
        
    Raises:
        HTTPException 404: Batch not found
    """
    tenant_id = int(request.headers.get("X-Tenant-ID", 0))
    
    async for db_session in get_db():
        try:
            batch_repo = FolderBatchRepository(db_session)
            document_repo = DocumentRepository(db_session)
            
            # Get batch
            batch = await batch_repo.get_by_id(batch_id, tenant_id)
            if not batch:
                logger.warning(
                    "FolderBatch not found",
                    batch_id=batch_id,
                    tenant_id=tenant_id,
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Folder batch not found",
                )
            
            # Get documents for this batch
            from sqlalchemy import select
            from src.storage_indexing.models.document import Document
            
            stmt = (
                select(Document)
                .where(Document.folder_batch_id == batch_id)
                .where(Document.tenant_id == tenant_id)
                .order_by(Document.created_at)
            )
            
            result = await db_session.execute(stmt)
            all_documents = list(result.scalars().all())
            
            # Paginate documents
            total_documents = len(all_documents)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_documents = all_documents[start_idx:end_idx]
            
            # Calculate estimated completion time (if still processing)
            estimated_completion_seconds = None
            if batch.status == "processing" and batch.files_processed > 0:
                # Simple estimation: average 2 seconds per file
                remaining_files = batch.total_files_discovered - batch.files_processed
                estimated_completion_seconds = remaining_files * 2
            
            logger.info(
                "Folder batch status retrieved",
                batch_id=batch_id,
                status=batch.status,
                progress=batch.progress_percentage,
            )
            
            return {
                "batch_id": batch.id,
                "status": batch.status,
                "folder_name": batch.original_folder_name,
                "folder_path": batch.folder_path,
                "total_files_discovered": batch.total_files_discovered,
                "files_processed": batch.files_processed,
                "files_failed": batch.files_failed,
                "progress_percentage": batch.progress_percentage,
                "is_complete": batch.is_complete,
                "error_message": batch.error_message,
                "created_at": batch.created_at.isoformat() if batch.created_at else None,
                "updated_at": batch.updated_at.isoformat() if batch.updated_at else None,
                "completed_at": batch.completed_at.isoformat() if batch.completed_at else None,
                "estimated_completion_seconds": estimated_completion_seconds,
                "documents": {
                    "total_count": total_documents,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": math.ceil(total_documents / page_size) if total_documents > 0 else 0,
                    "items": [
                        {
                            "document_id": doc.document_id,
                            "filename": doc.filename,
                            "relative_path": doc.original_filename,
                            "status": doc.processing_status,
                            "file_size": doc.file_size,
                            "created_at": doc.created_at.isoformat() if doc.created_at else None,
                        }
                        for doc in paginated_documents
                    ],
                },
            }
        
        finally:
            await db_session.close()
