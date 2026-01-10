"""Document upload service.

Handles file upload validation, storage, and database operations.
"""

import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, BinaryIO

import aiofiles
import structlog

from src.shared.config import settings
from src.ingestion_parsing.storage.file_storage import FileStorage
from src.ingestion_parsing.storage.quota_manager import QuotaManager
from src.shared.exceptions import (
    FileTooLargeError,
    FileTypeNotAllowedError,
    MalwareScanFailedError,
)
from src.shared.validators import (
    detect_file_type,
    generate_content_hash,
    scan_for_malware,
    validate_file_size,
    validate_file_type,
    validate_filename,
)
from src.storage_indexing.repositories.document_repository import DocumentRepository
from src.storage_indexing.repositories.job_repository import JobRepository

logger = structlog.get_logger(__name__)


class UploadService:
    """Service for handling document uploads.
    
    Manages the complete upload workflow:
    1. Validation (file type, size, quota)
    2. Storage (local or S3)
    3. Database operations (document record, processing job)
    4. Quota updates
    
    Example:
        >>> service = UploadService(
        ...     storage=file_storage,
        ...     quota_manager=quota_manager,
        ...     document_repo=document_repo,
        ...     job_repo=job_repo,
        ... )
        >>> document, job = await service.upload_file(
        ...     file=uploaded_file,
        ...     filename="report.pdf",
        ...     tenant_id=1,
        ...     user_id=5,
        ... )
    """

    def __init__(
        self,
        storage: FileStorage,
        quota_manager: QuotaManager,
        document_repo: DocumentRepository,
        job_repo: JobRepository,
    ) -> None:
        """Initialize upload service.
        
        Args:
            storage: File storage backend
            quota_manager: Quota management service
            document_repo: Document repository
            job_repo: Job repository
        """
        self.storage = storage
        self.quota_manager = quota_manager
        self.document_repo = document_repo
        self.job_repo = job_repo

    async def validate_upload(
        self,
        file_path: str,
        original_filename: str,
        tenant_id: int,
    ) -> tuple[str, int]:
        """Validate uploaded file.
        
        Performs all validation checks:
        - Filename safety (path traversal)
        - File type (magic bytes)
        - File size (within limit)
        - Storage quota (tenant limit)
        - Malware scan (if enabled)
        
        Args:
            file_path: Path to uploaded file
            original_filename: Original filename from upload
            tenant_id: Tenant ID for quota check
            
        Returns:
            Tuple of (detected_mime_type, file_size_bytes)
            
        Raises:
            FileTypeNotAllowedError: If file type not allowed
            FileTooLargeError: If file exceeds size limit
            QuotaExceededError: If tenant quota would be exceeded
            MalwareScanFailedError: If malware detected
        """
        # Validate filename
        if not validate_filename(original_filename):
            raise FileTypeNotAllowedError(
                "Invalid filename: contains path traversal characters",
                file_type=original_filename,
            )
        
        # Detect file type using magic bytes
        detected_mime_type = detect_file_type(file_path)
        
        # Check if file type is allowed
        allowed_types = self._get_allowed_mime_types()
        if not validate_file_type(detected_mime_type, allowed_types):
            raise FileTypeNotAllowedError(
                f"File type '{detected_mime_type}' is not allowed. "
                f"Allowed types: {', '.join(settings.upload.get_allowed_file_types_list())}",
                file_type=detected_mime_type,
                allowed_types=settings.upload.get_allowed_file_types_list(),
            )
        
        # Check file size
        file_size = Path(file_path).stat().st_size
        max_size_bytes = settings.max_upload_size_mb * 1024 * 1024
        
        if not validate_file_size(file_size, max_size_bytes):
            raise FileTooLargeError(
                f"File size {file_size / 1024 / 1024:.2f}MB exceeds maximum allowed size of "
                f"{settings.upload.max_upload_size_mb}MB",
                file_size=file_size,
                max_size=max_size_bytes,
            )
        
        # Check tenant quota
        await self.quota_manager.check_quota(tenant_id=tenant_id, file_size=file_size)
        
        # Malware scan (if enabled)
        if settings.upload.enable_malware_scanning:
            is_clean, virus_name = await scan_for_malware(
                file_path=file_path,
                clamav_host=settings.upload.clamav_host,
                clamav_port=settings.upload.clamav_port,
            )
            if not is_clean:
                raise MalwareScanFailedError(
                    f"Malware detected: {virus_name}",
                    virus_name=virus_name,
                )
        
        logger.info(
            "File validation passed",
            original_filename=original_filename,
            mime_type=detected_mime_type,
            file_size=file_size,
            tenant_id=tenant_id,
        )
        
        return detected_mime_type, file_size

    async def upload_file(
        self,
        file: BinaryIO,
        filename: str,
        tenant_id: int,
        user_id: int | None = None,
    ) -> tuple[any, any]:
        """Upload and process a file.
        
        Complete upload workflow:
        1. Save file to temporary location
        2. Validate file (type, size, quota)
        3. Generate content hash
        4. Store in persistent storage
        5. Create document record
        6. Create processing job
        7. Update tenant quota
        8. Clean up temporary file
        
        Args:
            file: File object from upload
            filename: Original filename
            tenant_id: Tenant ID
            user_id: User ID who uploaded (optional)
            
        Returns:
            Tuple of (Document, ProcessingJob)
            
        Raises:
            Various validation errors (see validate_upload)
        """
        # Create temporary file for processing
        temp_file = None
        try:
            # Save uploaded file to temporary location
            temp_dir = Path(settings.upload.temp_upload_dir)
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            temp_file = temp_dir / f"upload_{uuid.uuid4().hex}"
            
            async with aiofiles.open(temp_file, "wb") as f:
                content = await file.read() if hasattr(file, "read") else file
                await f.write(content)
            
            # Validate file
            mime_type, file_size = await self.validate_upload(
                file_path=str(temp_file),
                original_filename=filename,
                tenant_id=tenant_id,
            )
            
            # Generate content hash for duplicate detection
            content_hash = generate_content_hash(str(temp_file))
            
            # Check for duplicate
            existing_doc = await self.document_repo.check_duplicate(
                tenant_id=tenant_id,
                content_hash=content_hash,
            )
            if existing_doc:
                logger.info(
                    "Duplicate document detected",
                    existing_document_id=existing_doc.document_id,
                    content_hash=content_hash,
                )
                # Return existing document (optional: could raise error instead)
                # For now, proceed with new upload
            
            # Generate storage filename
            file_extension = Path(filename).suffix or self._get_extension_from_mime(mime_type)
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            unique_id = uuid.uuid4().hex[:8]
            stored_filename = f"doc_{timestamp}_{unique_id}{file_extension}"
            
            # Build storage path with tenant isolation
            storage_key = f"{tenant_id}/{stored_filename}"
            
            # Upload to persistent storage
            storage_path = await self.storage.upload(
                file_path=str(temp_file),
                storage_key=storage_key,
            )
            
            # Create document record
            document = await self.document_repo.create(
                tenant_id=tenant_id,
                uploaded_by=user_id or 0,
                filename=stored_filename,
                original_filename=filename,
                file_type=file_extension.lstrip("."),
                mime_type=mime_type,
                file_size=file_size,
                storage_path=storage_path,
                content_hash=content_hash,
            )
            
            # Create processing job
            job = await self.job_repo.create(
                document_id=document.document_id,
                job_type="parse_document",
                started_by=user_id,
            )
            
            # Update tenant storage quota
            await self.quota_manager.update_usage(
                tenant_id=tenant_id,
                size_delta=file_size,
            )
            
            logger.info(
                "File uploaded successfully",
                document_id=document.document_id,
                job_id=job.job_id,
                filename=stored_filename,
                file_size=file_size,
                tenant_id=tenant_id,
                user_id=user_id,
            )
            
            return document, job
            
        finally:
            # Clean up temporary file
            if temp_file and Path(temp_file).exists():
                Path(temp_file).unlink()
                logger.debug("Temporary file cleaned up", temp_file=str(temp_file))

    def _get_allowed_mime_types(self) -> list[str]:
        """Get list of allowed MIME types from settings.
        
        Returns:
            List of allowed MIME type strings
        """
        from src.shared.validators import get_mime_type_map
        
        mime_map = get_mime_type_map()
        allowed_extensions = settings.upload.get_allowed_file_types_list()
        
        return [mime_map.get(ext, "") for ext in allowed_extensions if ext in mime_map]

    def _get_extension_from_mime(self, mime_type: str) -> str:
        """Get file extension from MIME type.
        
        Args:
            mime_type: MIME type string
            
        Returns:
            File extension with leading dot (e.g., '.pdf')
        """
        mime_to_ext = {
            "application/pdf": ".pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
            "application/msword": ".doc",
            "text/plain": ".txt",
        }
        return mime_to_ext.get(mime_type, ".bin")

    async def batch_upload(
        self,
        files: list[tuple[BinaryIO, str]],  # List of (file, filename)
        tenant_id: int,
        user_id: int | None = None,
        max_batch_size: int = 10,
    ) -> dict[str, Any]:
        """Upload multiple files in a batch.
        
        Processes files sequentially, continuing even if individual files fail.
        Performs quota check for entire batch before starting.
        
        Args:
            files: List of (file_object, filename) tuples
            tenant_id: Tenant ID
            user_id: User ID who uploaded (optional)
            max_batch_size: Maximum number of files per batch
            
        Returns:
            Dictionary with batch results and statistics
            
        Raises:
            ValueError: If batch size exceeds limit
            
        Example:
            >>> files = [(file1, "doc1.pdf"), (file2, "doc2.txt")]
            >>> results = await service.batch_upload(files, tenant_id=1)
            >>> print(f"Uploaded {results['successful']} of {results['total']}")
        """
        batch_id = f"batch_{uuid.uuid4().hex[:12]}"
        
        logger.info(
            "Starting batch upload",
            batch_id=batch_id,
            file_count=len(files),
            tenant_id=tenant_id,
        )
        
        # Validate batch size
        if len(files) > max_batch_size:
            raise ValueError(
                f"Batch size {len(files)} exceeds maximum allowed size of {max_batch_size}"
            )
        
        # Calculate total batch size for quota check
        total_batch_size = 0
        file_sizes = []
        
        for file_obj, filename in files:
            # Get file size
            file_obj.seek(0, 2)  # Seek to end
            file_size = file_obj.tell()
            file_obj.seek(0)  # Reset to beginning
            file_sizes.append(file_size)
            total_batch_size += file_size
        
        # Check quota for entire batch
        try:
            await self.quota_manager.check_quota(
                tenant_id=tenant_id,
                file_size=total_batch_size,
            )
        except Exception as e:
            logger.warning(
                "Batch upload rejected: quota exceeded",
                batch_id=batch_id,
                total_size=total_batch_size,
                tenant_id=tenant_id,
            )
            raise
        
        # Process files sequentially
        results = []
        successful_count = 0
        failed_count = 0
        
        for i, ((file_obj, filename), file_size) in enumerate(zip(files, file_sizes)):
            logger.info(
                "Processing file in batch",
                batch_id=batch_id,
                file_number=i + 1,
                total_files=len(files),
                filename=filename,
            )
            
            try:
                # Upload individual file
                document, job = await self.upload_file(
                    file=file_obj,
                    filename=filename,
                    tenant_id=tenant_id,
                    user_id=user_id,
                )
                
                results.append({
                    "filename": filename,
                    "status": "success",
                    "document_id": document.document_id,
                    "job_id": job.job_id,
                    "file_size": document.file_size,
                    "mime_type": document.mime_type,
                })
                successful_count += 1
                
            except Exception as e:
                logger.warning(
                    "File upload failed in batch",
                    batch_id=batch_id,
                    filename=filename,
                    error=str(e),
                )
                
                results.append({
                    "filename": filename,
                    "status": "error",
                    "error": str(e),
                })
                failed_count += 1
        
        logger.info(
            "Batch upload completed",
            batch_id=batch_id,
            total=len(files),
            successful=successful_count,
            failed=failed_count,
        )
        
        return {
            "batch_id": batch_id,
            "total": len(files),
            "successful": successful_count,
            "failed": failed_count,
            "results": results,
        }

    async def merge_chunks(
        self,
        session_id: str,
        chunk_dir: Path,
        num_chunks: int,
        expected_hash: str | None = None,
    ) -> Path:
        """Merge uploaded chunks into a single file.
        
        Reads all chunk files in sequence and merges them into a single file.
        Validates the final file size and content hash.
        
        Args:
            session_id: Upload session identifier
            chunk_dir: Directory containing chunk files
            num_chunks: Expected number of chunks
            expected_hash: Expected SHA-256 hash for validation (optional)
            
        Returns:
            Path to merged file
            
        Raises:
            ValueError: If chunks are missing or hash doesn't match
            
        Example:
            >>> merged_path = await service.merge_chunks(
            ...     session_id="session_abc123",
            ...     chunk_dir=Path("/tmp/uploads/session_abc123"),
            ...     num_chunks=10,
            ...     expected_hash="a1b2c3...",
            ... )
        """
        import hashlib
        
        logger.info(
            "Starting chunk merge",
            session_id=session_id,
            num_chunks=num_chunks,
            chunk_dir=str(chunk_dir),
        )
        
        # Verify all chunks exist
        missing_chunks = []
        for i in range(num_chunks):
            chunk_file = chunk_dir / f"chunk_{i}"
            if not chunk_file.exists():
                missing_chunks.append(i)
        
        if missing_chunks:
            raise ValueError(
                f"Missing chunks: {missing_chunks}. Cannot complete merge."
            )
        
        # Merge chunks
        merged_file = chunk_dir / "merged"
        hasher = hashlib.sha256()
        total_bytes = 0
        
        async with aiofiles.open(merged_file, "wb") as outfile:
            for i in range(num_chunks):
                chunk_file = chunk_dir / f"chunk_{i}"
                
                async with aiofiles.open(chunk_file, "rb") as infile:
                    chunk_data = await infile.read()
                    await outfile.write(chunk_data)
                    hasher.update(chunk_data)
                    total_bytes += len(chunk_data)
                
                logger.debug(
                    "Merged chunk",
                    session_id=session_id,
                    chunk_number=i,
                    chunk_size=len(chunk_data),
                )
        
        # Validate hash if provided
        actual_hash = hasher.hexdigest()
        if expected_hash and actual_hash != expected_hash:
            # Clean up merged file
            merged_file.unlink()
            raise ValueError(
                f"Content hash mismatch. Expected: {expected_hash}, Got: {actual_hash}"
            )
        
        logger.info(
            "Chunk merge completed",
            session_id=session_id,
            total_bytes=total_bytes,
            content_hash=actual_hash,
        )
        
        return merged_file

    async def cleanup_chunks(self, chunk_dir: Path) -> None:
        """Clean up temporary chunk files after merge or cancellation.
        
        Removes all chunk files and the chunk directory.
        
        Args:
            chunk_dir: Directory containing chunk files
            
        Example:
            >>> await service.cleanup_chunks(Path("/tmp/uploads/session_abc123"))
        """
        if not chunk_dir.exists():
            return
        
        try:
            # Remove all files in directory
            for file in chunk_dir.iterdir():
                file.unlink()
            
            # Remove directory
            chunk_dir.rmdir()
            
            logger.info("Cleaned up chunk directory", chunk_dir=str(chunk_dir))
            
        except Exception as e:
            logger.warning(
                "Failed to clean up chunks",
                chunk_dir=str(chunk_dir),
                error=str(e),
            )
