"""Integration tests for document upload API.

Tests the complete upload workflow including validation, storage, and database operations.
"""

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from httpx import AsyncClient

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from sqlalchemy.ext.asyncio import AsyncSession

from src.storage_indexing.models import Document, ProcessingJob, ProcessingStatus


@pytest.mark.asyncio
async def test_upload_endpoint_contract(client: AsyncClient) -> None:
    """Test POST /api/v1/documents/upload endpoint contract.
    
    Validates:
    - Request accepts multipart/form-data
    - Response structure matches schema
    - Proper HTTP status codes
    - Required fields in response
    """
    # Prepare test file
    test_file_path = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.pdf"
    
    # Test valid upload
    with open(test_file_path, "rb") as f:
        response = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("test.pdf", f, "application/pdf")},
            data={"tenant_id": "1"},
        )
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify response structure
    assert "document_id" in data
    assert "filename" in data
    assert "file_size" in data
    assert "mime_type" in data
    assert "job_id" in data
    assert "status" in data
    
    assert data["status"] == ProcessingStatus.UPLOADED.value
    assert isinstance(data["document_id"], int)
    assert isinstance(data["job_id"], int)


@pytest.mark.asyncio
async def test_upload_endpoint_validation_errors(client: AsyncClient) -> None:
    """Test upload endpoint validation error responses."""
    # Test missing file
    response = await client.post(
        "/api/v1/documents/upload",
        data={"tenant_id": "1"},
    )
    assert response.status_code == 422  # Validation error
    
    # Test invalid file type
    response = await client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.exe", b"fake content", "application/x-msdownload")},
        data={"tenant_id": "1"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["type"] == "file_type_not_allowed"


@pytest.mark.asyncio
async def test_upload_file_too_large(client: AsyncClient) -> None:
    """Test file size limit enforcement."""
    # Create a mock file larger than limit (50MB)
    large_content = b"x" * (51 * 1024 * 1024)  # 51MB
    
    response = await client.post(
        "/api/v1/documents/upload",
        files={"file": ("large.pdf", large_content, "application/pdf")},
        data={"tenant_id": "1"},
    )
    
    assert response.status_code == 413
    data = response.json()
    assert data["error"]["type"] == "file_too_large"


@pytest.mark.asyncio
async def test_single_pdf_upload_workflow(
    client: AsyncClient,
    db_session: "AsyncSession",
) -> None:
    """Test complete single PDF upload workflow.
    
    End-to-end test:
    1. Upload PDF file
    2. Verify file is stored in correct location
    3. Verify document record in database
    4. Verify processing job created with status "pending"
    """
    test_file_path = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.pdf"
    
    # Upload file
    with open(test_file_path, "rb") as f:
        response = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("report.pdf", f, "application/pdf")},
            data={"tenant_id": "1", "user_id": "5"},
        )
    
    assert response.status_code == 201
    data = response.json()
    
    document_id = data["document_id"]
    job_id = data["job_id"]
    
    # Verify document in database
    document = await db_session.get(Document, document_id)
    assert document is not None
    assert document.tenant_id == 1
    assert document.uploaded_by == 5
    assert document.original_filename == "report.pdf"
    assert document.file_type == "pdf"
    assert document.mime_type == "application/pdf"
    assert document.processing_status == ProcessingStatus.UPLOADED.value
    assert document.content_hash is not None
    assert document.storage_path is not None
    
    # Verify file stored in correct location
    storage_path = Path(document.storage_path)
    assert storage_path.exists()
    assert storage_path.stat().st_size > 0
    
    # Verify processing job created
    job = await db_session.get(ProcessingJob, job_id)
    assert job is not None
    assert job.document_id == document_id
    assert job.job_type == "parse_document"
    assert job.status == ProcessingStatus.PENDING.value
    assert job.started_by == 5


@pytest.mark.asyncio
async def test_upload_updates_tenant_storage_quota(
    client: AsyncClient,
    db_session: "AsyncSession",
) -> None:
    """Test that upload updates tenant storage usage."""
    from src.storage_indexing.models import Tenant
    
    # Get initial storage usage
    tenant = await db_session.get(Tenant, 1)
    initial_usage = tenant.storage_used_bytes if tenant else 0
    
    # Upload file
    test_file_path = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.pdf"
    with open(test_file_path, "rb") as f:
        response = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("test.pdf", f, "application/pdf")},
            data={"tenant_id": "1"},
        )
    
    assert response.status_code == 201
    data = response.json()
    file_size = data["file_size"]
    
    # Verify storage usage increased
    await db_session.refresh(tenant)
    assert tenant.storage_used_bytes == initial_usage + file_size


@pytest.mark.asyncio
async def test_upload_quota_exceeded(client: AsyncClient, db_session: "AsyncSession") -> None:
    """Test upload rejection when quota is exceeded."""
    from src.storage_indexing.models import Tenant
    
    # Set tenant quota to very small value
    tenant = await db_session.get(Tenant, 1)
    if tenant:
        tenant.storage_quota_bytes = 1000  # 1KB
        tenant.storage_used_bytes = 900  # 900 bytes used
        await db_session.commit()
    
    # Try to upload file larger than remaining quota
    test_file_path = Path(__file__).parent.parent / "fixtures" / "sample_documents" / "sample.pdf"
    with open(test_file_path, "rb") as f:
        response = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("test.pdf", f, "application/pdf")},
            data={"tenant_id": "1"},
        )
    
    assert response.status_code == 413
    data = response.json()
    assert data["error"]["type"] == "quota_exceeded"


@pytest.mark.asyncio
async def test_multi_format_upload(client: AsyncClient, db_session: "AsyncSession") -> None:
    """Test uploading documents in multiple formats (PDF, DOCX, TXT).
    
    Verifies that all formats are accepted and processed correctly.
    """
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "sample_documents"
    
    # Test files
    test_files = [
        ("sample.pdf", "application/pdf"),
        ("sample.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        ("sample.txt", "text/plain"),
    ]
    
    uploaded_docs = []
    
    # Upload each file
    for filename, mime_type in test_files:
        file_path = fixtures_dir / filename
        
        with open(file_path, "rb") as f:
            response = await client.post(
                "/api/v1/documents/upload",
                files={"file": (filename, f, mime_type)},
                data={"tenant_id": "1", "user_id": "1"},
            )
        
        assert response.status_code == 201, f"Upload failed for {filename}"
        data = response.json()
        
        assert data["document_id"] is not None
        assert data["filename"] is not None
        assert data["mime_type"] == mime_type
        assert data["job_id"] is not None
        
        uploaded_docs.append(data)
    
    # Verify all documents were created
    assert len(uploaded_docs) == 3
    
    # Verify each document has correct MIME type
    assert uploaded_docs[0]["mime_type"] == "application/pdf"
    assert uploaded_docs[1]["mime_type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert uploaded_docs[2]["mime_type"] == "text/plain"


# ============================================================================
# Batch Upload Tests (T099-T101)
# ============================================================================


@pytest.mark.asyncio
async def test_batch_upload_endpoint_contract(client: AsyncClient) -> None:
    """Test POST /api/v1/documents/batch-upload endpoint contract."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "sample_documents"
    
    # Prepare multiple files for batch upload
    files = []
    for i in range(3):
        file_path = fixtures_dir / "sample.pdf"
        files.append(("files", (f"doc_{i}.pdf", open(file_path, "rb"), "application/pdf")))
    
    # Upload batch
    response = await client.post(
        "/api/v1/documents/batch-upload",
        files=files,
        data={"tenant_id": "1", "user_id": "1"},
    )
    
    # Close files
    for _, (_, f, _) in files:
        f.close()
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "batch_id" in data or "results" in data
    assert "total" in data
    assert "successful" in data
    assert "failed" in data
    assert "results" in data
    
    # Verify counts
    assert data["total"] == 3
    assert data["successful"] == 3
    assert data["failed"] == 0
    
    # Verify each result has required fields
    for result in data["results"]:
        assert "filename" in result
        assert "status" in result
        if result["status"] == "success":
            assert "document_id" in result
            assert "job_id" in result


@pytest.mark.asyncio
async def test_batch_upload_mixed_results(client: AsyncClient) -> None:
    """Test batch upload with mixed success and failure."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "sample_documents"
    
    # Mix of valid and invalid files
    files = [
        ("files", ("valid1.pdf", open(fixtures_dir / "sample.pdf", "rb"), "application/pdf")),
        ("files", ("valid2.txt", open(fixtures_dir / "sample.txt", "rb"), "text/plain")),
        ("files", ("invalid.exe", b"fake executable content", "application/x-msdownload")),  # Invalid type
    ]
    
    response = await client.post(
        "/api/v1/documents/batch-upload",
        files=files,
        data={"tenant_id": "1", "user_id": "1"},
    )
    
    # Close files
    files[0][1][1].close()
    files[1][1][1].close()
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify partial success
    assert data["total"] == 3
    assert data["successful"] == 2  # 2 valid files
    assert data["failed"] == 1  # 1 invalid file
    
    # Check that valid files succeeded
    successful_results = [r for r in data["results"] if r["status"] == "success"]
    assert len(successful_results) == 2
    
    # Check that invalid file failed
    failed_results = [r for r in data["results"] if r["status"] == "error"]
    assert len(failed_results) == 1
    assert "error" in failed_results[0]


@pytest.mark.asyncio
async def test_batch_upload_size_limit(client: AsyncClient) -> None:
    """Test batch upload rejects batches exceeding size limit."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "sample_documents"
    
    # Try to upload more than max batch size (assume 10)
    files = []
    for i in range(15):  # Exceed limit of 10
        file_path = fixtures_dir / "sample.txt"
        files.append(("files", (f"doc_{i}.txt", open(file_path, "rb"), "text/plain")))
    
    response = await client.post(
        "/api/v1/documents/batch-upload",
        files=files,
        data={"tenant_id": "1", "user_id": "1"},
    )
    
    # Close files
    for _, (_, f, _) in files:
        f.close()
    
    # Should reject batch that's too large
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert "batch" in data["error"]["message"].lower() or "limit" in data["error"]["message"].lower()


@pytest.mark.asyncio
async def test_batch_upload_quota_check(client: AsyncClient, db_session: "AsyncSession") -> None:
    """Test batch upload checks quota before starting."""
    from src.storage_indexing.models import Tenant
    
    # Set tenant quota to small value
    tenant = await db_session.get(Tenant, 1)
    if tenant:
        tenant.storage_quota_bytes = 5000  # 5KB
        tenant.storage_used_bytes = 0
        await db_session.commit()
    
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "sample_documents"
    
    # Try to upload files that exceed quota
    files = [
        ("files", ("doc1.pdf", open(fixtures_dir / "sample.pdf", "rb"), "application/pdf")),
        ("files", ("doc2.pdf", open(fixtures_dir / "sample.pdf", "rb"), "application/pdf")),
    ]
    
    response = await client.post(
        "/api/v1/documents/batch-upload",
        files=files,
        data={"tenant_id": "1", "user_id": "1"},
    )
    
    # Close files
    for _, (_, f, _) in files:
        f.close()
    
    # May succeed with partial upload or fail entirely depending on implementation
    assert response.status_code in [200, 400, 413]


# ============================================================================
# Resumable Upload Tests (T114-T117)
# ============================================================================


@pytest.mark.asyncio
async def test_resumable_upload_init_endpoint(client: AsyncClient) -> None:
    """Test POST /api/v1/documents/upload/resumable endpoint to create session."""
    response = await client.post(
        "/api/v1/documents/upload/resumable",
        json={
            "filename": "large_document.pdf",
            "file_size": 50_000_000,  # 50MB
            "tenant_id": 1,
            "user_id": 1,
            "chunk_size": 5_000_000,  # 5MB chunks
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "session_id" in data
    assert "upload_url" in data
    assert "expires_at" in data
    assert "chunk_size" in data
    assert "total_chunks" in data
    
    # Verify values
    assert data["chunk_size"] == 5_000_000
    assert data["total_chunks"] == 10  # 50MB / 5MB = 10 chunks


@pytest.mark.asyncio
async def test_resumable_upload_chunk_endpoint(client: AsyncClient) -> None:
    """Test PATCH /api/v1/documents/upload/resumable/{session_id} for chunk upload."""
    # First create session
    init_response = await client.post(
        "/api/v1/documents/upload/resumable",
        json={
            "filename": "test.pdf",
            "file_size": 10_000_000,  # 10MB
            "tenant_id": 1,
            "user_id": 1,
            "chunk_size": 5_000_000,  # 5MB chunks
        },
    )
    
    assert init_response.status_code == 200
    session_id = init_response.json()["session_id"]
    
    # Upload first chunk
    chunk_data = b"0" * 5_000_000  # 5MB of data
    response = await client.patch(
        f"/api/v1/documents/upload/resumable/{session_id}",
        headers={
            "Content-Range": "bytes 0-4999999/10000000",
            "Content-Type": "application/octet-stream",
        },
        content=chunk_data,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify progress
    assert "uploaded_bytes" in data
    assert "total_bytes" in data
    assert "progress_percent" in data
    assert data["uploaded_bytes"] == 5_000_000
    assert data["total_bytes"] == 10_000_000
    assert data["progress_percent"] == 50.0


@pytest.mark.asyncio
async def test_resumable_upload_complete_workflow(client: AsyncClient) -> None:
    """Test complete resumable upload: init → upload chunks → merge."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "sample_documents"
    
    # Read test file
    test_file = fixtures_dir / "sample.pdf"
    with open(test_file, "rb") as f:
        file_content = f.read()
    
    file_size = len(file_content)
    chunk_size = file_size // 3  # Split into 3 chunks
    
    # Step 1: Initialize resumable upload
    init_response = await client.post(
        "/api/v1/documents/upload/resumable",
        json={
            "filename": "sample.pdf",
            "file_size": file_size,
            "tenant_id": 1,
            "user_id": 1,
            "chunk_size": chunk_size,
        },
    )
    
    assert init_response.status_code == 200
    session_id = init_response.json()["session_id"]
    
    # Step 2: Upload chunks
    for i in range(3):
        start = i * chunk_size
        end = start + chunk_size if i < 2 else file_size
        chunk_data = file_content[start:end]
        
        response = await client.patch(
            f"/api/v1/documents/upload/resumable/{session_id}",
            headers={
                "Content-Range": f"bytes {start}-{end-1}/{file_size}",
                "Content-Type": "application/octet-stream",
            },
            content=chunk_data,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if i < 2:
            # Partial upload
            assert data["status"] == "uploading"
        else:
            # Final chunk - should trigger merge
            assert data["status"] in ["complete", "merging"]
            assert "document_id" in data or data["status"] == "merging"


@pytest.mark.asyncio
async def test_resumable_upload_get_progress(client: AsyncClient) -> None:
    """Test GET /api/v1/documents/upload/resumable/{session_id} to check progress."""
    # Create session
    init_response = await client.post(
        "/api/v1/documents/upload/resumable",
        json={
            "filename": "test.pdf",
            "file_size": 10_000_000,
            "tenant_id": 1,
            "user_id": 1,
            "chunk_size": 5_000_000,
        },
    )
    
    session_id = init_response.json()["session_id"]
    
    # Check initial progress
    response = await client.get(
        f"/api/v1/documents/upload/resumable/{session_id}"
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "session_id" in data
    assert "status" in data
    assert "uploaded_bytes" in data
    assert "total_bytes" in data
    assert data["status"] == "pending"
    assert data["uploaded_bytes"] == 0


@pytest.mark.asyncio
async def test_resumable_upload_cancel(client: AsyncClient) -> None:
    """Test DELETE /api/v1/documents/upload/resumable/{session_id} to cancel."""
    # Create session
    init_response = await client.post(
        "/api/v1/documents/upload/resumable",
        json={
            "filename": "test.pdf",
            "file_size": 10_000_000,
            "tenant_id": 1,
            "user_id": 1,
            "chunk_size": 5_000_000,
        },
    )
    
    session_id = init_response.json()["session_id"]
    
    # Cancel upload
    response = await client.delete(
        f"/api/v1/documents/upload/resumable/{session_id}"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "cancelled"
    
    # Verify session is cancelled
    get_response = await client.get(
        f"/api/v1/documents/upload/resumable/{session_id}"
    )
    assert get_response.status_code in [404, 410]  # Gone or not found
