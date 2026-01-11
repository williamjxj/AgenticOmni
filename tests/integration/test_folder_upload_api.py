"""Integration tests for folder upload API.

Tests batch folder upload with recursive markdown file discovery.
User Story 3: Batch Folder Ingestion (Priority: P2)
"""

from pathlib import Path
from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.storage_indexing.models.folder_batch import FolderBatch


@pytest.mark.asyncio
async def test_upload_folder_success(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant_id: int,
    test_user_id: int,
    test_folder_structure: Path,
) -> None:
    """Test successful folder upload returns 201 with batch_id and status_url.
    
    User Story 3, Task T064
    """
    # Arrange: Create folder with multiple markdown files
    # test_folder_structure fixture creates this
    
    # Act: Upload folder
    # Note: In real implementation, this would be multipart/form-data with folder structure
    # For now, we'll test the endpoint exists and returns correct structure
    response = await async_client.post(
        "/api/v1/documents/upload-folder",
        json={
            "folder_path": str(test_folder_structure),
            "tenant_id": test_tenant_id,
            "user_id": test_user_id,
        },
    )
    
    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    
    assert "batch_id" in data
    assert "status_url" in data
    assert "folder_name" in data
    assert "total_files_discovered" in data
    assert data["status"] == "discovering"


@pytest.mark.asyncio
async def test_get_folder_batch_status(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant_id: int,
    test_folder_batch: FolderBatch,
) -> None:
    """Test GET /folder-batches/{batch_id} returns progress tracking info.
    
    User Story 3, Task T065
    """
    # Arrange: test_folder_batch fixture creates a FolderBatch
    batch_id = test_folder_batch.id
    
    # Act
    response = await async_client.get(
        f"/api/v1/documents/folder-batches/{batch_id}",
        headers={"X-Tenant-ID": str(test_tenant_id)},
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["batch_id"] == batch_id
    assert "status" in data
    assert "total_files_discovered" in data
    assert "files_processed" in data
    assert "files_failed" in data
    assert "progress_percentage" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_folder_batch_processing_workflow(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant_id: int,
    test_user_id: int,
    test_folder_with_10_files: Path,
    dramatiq_worker: Any,
) -> None:
    """Test complete folder batch processing: upload → discover → process → verify all 10 files.
    
    User Story 3, Task T068
    """
    # Arrange: Folder with 10 markdown files
    # test_folder_with_10_files fixture creates this
    
    # Act: Upload folder
    response = await async_client.post(
        "/api/v1/documents/upload-folder",
        json={
            "folder_path": str(test_folder_with_10_files),
            "tenant_id": test_tenant_id,
            "user_id": test_user_id,
        },
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    batch_id = response.json()["batch_id"]
    
    # Wait for async processing
    dramatiq_worker.join()
    await db_session.commit()
    
    # Assert: Check batch status
    response = await async_client.get(
        f"/api/v1/documents/folder-batches/{batch_id}",
        headers={"X-Tenant-ID": str(test_tenant_id)},
    )
    
    data = response.json()
    assert data["total_files_discovered"] == 10
    assert data["files_processed"] == 10
    assert data["files_failed"] == 0
    assert data["status"] in ["completed", "processing"]
    assert data["progress_percentage"] == 100.0


@pytest.mark.asyncio
async def test_folder_upload_preserves_relative_paths(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant_id: int,
    test_user_id: int,
    nested_folder_structure: Path,
    dramatiq_worker: Any,
) -> None:
    """Test that relative paths are preserved in document metadata.
    
    User Story 3, Task T068
    """
    # Arrange: Nested folder structure
    # nested_folder_structure: docs/api/README.md, docs/guides/quickstart.md, etc.
    
    # Act: Upload folder
    response = await async_client.post(
        "/api/v1/documents/upload-folder",
        json={
            "folder_path": str(nested_folder_structure),
            "tenant_id": test_tenant_id,
            "user_id": test_user_id,
        },
    )
    
    batch_id = response.json()["batch_id"]
    dramatiq_worker.join()
    await db_session.commit()
    
    # Assert: Get batch with documents
    response = await async_client.get(
        f"/api/v1/documents/folder-batches/{batch_id}",
        headers={"X-Tenant-ID": str(test_tenant_id)},
    )
    
    data = response.json()
    documents = data.get("documents", [])
    
    # Check that relative paths are preserved
    relative_paths = [doc.get("relative_path") for doc in documents]
    assert any("api/README.md" in path for path in relative_paths if path)
    assert any("guides/quickstart.md" in path for path in relative_paths if path)


@pytest.mark.asyncio
async def test_folder_upload_max_files_validation(
    async_client: AsyncClient,
    test_tenant_id: int,
    test_user_id: int,
    folder_with_too_many_files: Path,
) -> None:
    """Test that folders exceeding max file limit are rejected.
    
    User Story 3, Task T087
    """
    # Arrange: Folder with > 500 files (from settings)
    
    # Act
    response = await async_client.post(
        "/api/v1/documents/upload-folder",
        json={
            "folder_path": str(folder_with_too_many_files),
            "tenant_id": test_tenant_id,
            "user_id": test_user_id,
        },
    )
    
    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "too many files" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_folder_upload_no_markdown_files(
    async_client: AsyncClient,
    test_tenant_id: int,
    test_user_id: int,
    tmp_path: Path,
) -> None:
    """Test error handling when folder contains no markdown files.
    
    User Story 3, Task T090
    """
    # Arrange: Folder with no .md files
    empty_folder = tmp_path / "empty"
    empty_folder.mkdir()
    (empty_folder / "readme.txt").write_text("Not markdown")
    (empty_folder / "data.json").write_text("{}")
    
    # Act
    response = await async_client.post(
        "/api/v1/documents/upload-folder",
        json={
            "folder_path": str(empty_folder),
            "tenant_id": test_tenant_id,
            "user_id": test_user_id,
        },
    )
    
    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "no markdown files" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_folder_batch_pagination(
    async_client: AsyncClient,
    test_tenant_id: int,
    test_folder_batch_with_documents: FolderBatch,
) -> None:
    """Test pagination for document list in folder batch response.
    
    User Story 3, Task T086
    """
    # Arrange
    batch_id = test_folder_batch_with_documents.id
    
    # Act: Get first page
    response = await async_client.get(
        f"/api/v1/documents/folder-batches/{batch_id}?page=1&page_size=5",
        headers={"X-Tenant-ID": str(test_tenant_id)},
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["page"] == 1
    assert data["page_size"] == 5
    assert "total_pages" in data
    assert len(data["documents"]) <= 5


# Fixtures


@pytest.fixture
def test_folder_structure(tmp_path: Path) -> Path:
    """Create a test folder structure with markdown files."""
    folder = tmp_path / "test_docs"
    folder.mkdir()
    
    (folder / "README.md").write_text("# README\n\nMain documentation.")
    (folder / "guide.md").write_text("# Guide\n\nUser guide.")
    (folder / "api.md").write_text("# API\n\nAPI reference.")
    
    return folder


@pytest.fixture
def test_folder_with_10_files(tmp_path: Path) -> Path:
    """Create a folder with exactly 10 markdown files."""
    folder = tmp_path / "batch_test"
    folder.mkdir()
    
    for i in range(10):
        (folder / f"doc{i}.md").write_text(f"# Document {i}\n\nContent {i}")
    
    return folder


@pytest.fixture
def nested_folder_structure(tmp_path: Path) -> Path:
    """Create a nested folder structure."""
    root = tmp_path / "docs"
    root.mkdir()
    
    api_dir = root / "api"
    api_dir.mkdir()
    (api_dir / "README.md").write_text("# API\n\nAPI docs")
    (api_dir / "endpoints.md").write_text("# Endpoints\n\nAPI endpoints")
    
    guides_dir = root / "guides"
    guides_dir.mkdir()
    (guides_dir / "quickstart.md").write_text("# Quickstart\n\nGet started")
    (guides_dir / "advanced.md").write_text("# Advanced\n\nAdvanced topics")
    
    return root


@pytest.fixture
def folder_with_too_many_files(tmp_path: Path) -> Path:
    """Create a folder with more than max allowed files."""
    folder = tmp_path / "too_many"
    folder.mkdir()
    
    # Create 501 files (assuming max is 500)
    for i in range(501):
        (folder / f"file{i}.md").write_text(f"# File {i}")
    
    return folder


@pytest.fixture
async def test_folder_batch(
    db_session: AsyncSession,
    test_tenant_id: int,
    test_user_id: int,
) -> FolderBatch:
    """Create a test FolderBatch record."""
    from src.storage_indexing.models.folder_batch import FolderBatch
    
    batch = FolderBatch(
        tenant_id=test_tenant_id,
        user_id=test_user_id,
        folder_path="/test/docs",
        original_folder_name="docs",
        total_files_discovered=5,
        files_processed=3,
        files_failed=0,
        status="processing",
    )
    
    db_session.add(batch)
    await db_session.commit()
    await db_session.refresh(batch)
    
    return batch


@pytest.fixture
async def test_folder_batch_with_documents(
    db_session: AsyncSession,
    test_tenant_id: int,
    test_user_id: int,
) -> FolderBatch:
    """Create a FolderBatch with associated documents."""
    from src.storage_indexing.models.folder_batch import FolderBatch
    from src.storage_indexing.models.document import Document
    
    batch = FolderBatch(
        tenant_id=test_tenant_id,
        user_id=test_user_id,
        folder_path="/test/batch",
        original_folder_name="batch",
        total_files_discovered=10,
        files_processed=10,
        files_failed=0,
        status="completed",
    )
    
    db_session.add(batch)
    await db_session.flush()
    
    # Create 10 documents
    for i in range(10):
        doc = Document(
            tenant_id=test_tenant_id,
            user_id=test_user_id,
            filename=f"doc{i}.md",
            original_filename=f"doc{i}.md",
            file_size=1024,
            mime_type="text/markdown",
            storage_path=f"/storage/doc{i}.md",
            content_hash=f"hash{i}",
            folder_batch_id=batch.id,
        )
        db_session.add(doc)
    
    await db_session.commit()
    await db_session.refresh(batch)
    
    return batch
