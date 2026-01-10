"""Pydantic models for document upload API requests."""

from pydantic import BaseModel, Field


class UploadRequest(BaseModel):
    """Request model for document upload.
    
    Used for validating multipart/form-data upload requests.
    """

    tenant_id: int = Field(..., gt=0, description="Tenant ID for isolation")
    user_id: int | None = Field(None, gt=0, description="User ID who initiated upload")
    
    class Config:
        """Pydantic configuration."""
        
        json_schema_extra = {
            "example": {
                "tenant_id": 1,
                "user_id": 5,
            }
        }


class UploadResponse(BaseModel):
    """Response model for successful document upload.
    
    Returned after document is successfully uploaded and stored.
    """

    document_id: int = Field(..., description="Created document ID")
    filename: str = Field(..., description="Stored filename")
    original_filename: str = Field(..., description="Original uploaded filename")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="Detected MIME type")
    content_hash: str = Field(..., description="SHA-256 content hash")
    job_id: int = Field(..., description="Created processing job ID")
    status: str = Field(..., description="Processing status")
    
    class Config:
        """Pydantic configuration."""
        
        json_schema_extra = {
            "example": {
                "document_id": 123,
                "filename": "doc_20240109_abc123.pdf",
                "original_filename": "report.pdf",
                "file_size": 1024000,
                "mime_type": "application/pdf",
                "content_hash": "abc123def456...",
                "job_id": 456,
                "status": "uploaded",
            }
        }


# ============================================================================
# Batch Upload Models (T102-T103)
# ============================================================================


class BatchUploadResult(BaseModel):
    """Result for a single file in a batch upload."""

    filename: str = Field(..., description="Original filename")
    status: str = Field(..., description="Upload status (success or error)")
    document_id: int | None = Field(None, description="Document ID if successful")
    job_id: int | None = Field(None, description="Job ID if successful")
    error: str | None = Field(None, description="Error message if failed")
    file_size: int | None = Field(None, description="File size in bytes")
    mime_type: str | None = Field(None, description="Detected MIME type")


class BatchUploadResponse(BaseModel):
    """Response model for batch document upload.
    
    Contains summary statistics and individual file results.
    """

    batch_id: str = Field(..., description="Unique batch identifier")
    total: int = Field(..., description="Total number of files in batch")
    successful: int = Field(..., description="Number of successfully uploaded files")
    failed: int = Field(..., description="Number of failed uploads")
    results: list[BatchUploadResult] = Field(..., description="Individual file results")
    
    class Config:
        """Pydantic configuration."""
        
        json_schema_extra = {
            "example": {
                "batch_id": "batch_20240109_abc123",
                "total": 3,
                "successful": 2,
                "failed": 1,
                "results": [
                    {
                        "filename": "doc1.pdf",
                        "status": "success",
                        "document_id": 123,
                        "job_id": 456,
                        "file_size": 1024000,
                        "mime_type": "application/pdf",
                    },
                    {
                        "filename": "doc2.txt",
                        "status": "success",
                        "document_id": 124,
                        "job_id": 457,
                        "file_size": 5000,
                        "mime_type": "text/plain",
                    },
                    {
                        "filename": "invalid.exe",
                        "status": "error",
                        "error": "File type not allowed",
                    },
                ],
            }
        }


# ============================================================================
# Resumable Upload Models (T118-T119)
# ============================================================================


class ResumableUploadInit(BaseModel):
    """Request model for initializing a resumable upload session.
    
    Used to create an upload session for large files that can be
    uploaded in chunks and resumed if interrupted.
    """

    filename: str = Field(..., description="Original filename", min_length=1, max_length=255)
    file_size: int = Field(..., description="Total file size in bytes", gt=0, le=5_000_000_000)  # Max 5GB
    tenant_id: int = Field(..., description="Tenant ID", gt=0)
    user_id: int | None = Field(None, description="User ID who initiated upload", gt=0)
    chunk_size: int = Field(
        default=5_000_000,  # 5MB default
        description="Chunk size in bytes",
        ge=1_000_000,  # Min 1MB
        le=100_000_000,  # Max 100MB
    )
    content_hash: str | None = Field(
        None,
        description="Optional SHA-256 hash of complete file for integrity verification",
        min_length=64,
        max_length=64,
    )
    
    class Config:
        """Pydantic configuration."""
        
        json_schema_extra = {
            "example": {
                "filename": "large_document.pdf",
                "file_size": 50000000,
                "tenant_id": 1,
                "user_id": 1,
                "chunk_size": 5000000,
                "content_hash": "a1b2c3d4e5f6...",
            }
        }


class ResumableUploadSession(BaseModel):
    """Response model for resumable upload session.
    
    Returned when creating or querying an upload session.
    """

    session_id: str = Field(..., description="Unique session identifier")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="Total file size in bytes")
    chunk_size: int = Field(..., description="Recommended chunk size in bytes")
    total_chunks: int = Field(..., description="Total number of chunks")
    uploaded_bytes: int = Field(..., description="Bytes uploaded so far")
    status: str = Field(..., description="Session status (pending, uploading, merging, complete, cancelled, expired)")
    upload_url: str = Field(..., description="URL for uploading chunks")
    expires_at: str = Field(..., description="Session expiration timestamp (ISO 8601)")
    created_at: str = Field(..., description="Session creation timestamp (ISO 8601)")
    
    class Config:
        """Pydantic configuration."""
        
        json_schema_extra = {
            "example": {
                "session_id": "session_abc123def456",
                "filename": "large_document.pdf",
                "file_size": 50000000,
                "chunk_size": 5000000,
                "total_chunks": 10,
                "uploaded_bytes": 0,
                "status": "pending",
                "upload_url": "/api/v1/documents/upload/resumable/session_abc123def456",
                "expires_at": "2024-01-10T10:00:00Z",
                "created_at": "2024-01-09T10:00:00Z",
            }
        }


class ChunkUploadResponse(BaseModel):
    """Response model for chunk upload progress.
    
    Returned after each chunk is uploaded.
    """

    session_id: str = Field(..., description="Session identifier")
    uploaded_bytes: int = Field(..., description="Total bytes uploaded so far")
    total_bytes: int = Field(..., description="Total file size in bytes")
    progress_percent: float = Field(..., description="Upload progress percentage (0-100)")
    status: str = Field(..., description="Upload status (uploading, merging, complete)")
    document_id: int | None = Field(None, description="Document ID when upload is complete")
    job_id: int | None = Field(None, description="Processing job ID when upload is complete")
    
    class Config:
        """Pydantic configuration."""
        
        json_schema_extra = {
            "example": {
                "session_id": "session_abc123def456",
                "uploaded_bytes": 25000000,
                "total_bytes": 50000000,
                "progress_percent": 50.0,
                "status": "uploading",
            }
        }
