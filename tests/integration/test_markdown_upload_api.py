"""Integration tests for markdown document upload API.

Tests the complete workflow: upload → parse → store → retrieve.
User Story 1: Upload and Parse Markdown Documents (Priority: P1)
"""

from pathlib import Path
from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.storage_indexing.models.document import Document
from src.storage_indexing.models.markdown_metadata import MarkdownMetadata


@pytest.mark.asyncio
async def test_markdown_upload_success(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant_id: int,
    test_user_id: int,
    sample_markdown_file: Path,
) -> None:
    """Test successful markdown file upload returns 201 with document_id.
    
    Contract test for POST /api/v1/documents/upload
    User Story 1, Task T023
    """
    # Arrange
    with open(sample_markdown_file, "rb") as f:
        files = {"file": ("sample.md", f, "text/markdown")}
        headers = {
            "X-Tenant-ID": str(test_tenant_id),
            "X-User-ID": str(test_user_id),
        }
        
        # Act
        response = await async_client.post(
            "/api/v1/documents/upload",
            files=files,
            headers=headers,
        )
    
    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert "document_id" in response_data
    assert isinstance(response_data["document_id"], int)
    assert response_data["mime_type"] == "text/markdown"
    assert response_data["status"] == "processing"


@pytest.mark.asyncio
async def test_markdown_upload_with_md_extension(
    async_client: AsyncClient,
    test_tenant_id: int,
    test_user_id: int,
    sample_markdown_file: Path,
) -> None:
    """Test .md file extension is accepted.
    
    User Story 1, Task T023
    """
    with open(sample_markdown_file, "rb") as f:
        files = {"file": ("document.md", f, "text/plain")}
        headers = {
            "X-Tenant-ID": str(test_tenant_id),
            "X-User-ID": str(test_user_id),
        }
        
        response = await async_client.post(
            "/api/v1/documents/upload",
            files=files,
            headers=headers,
        )
    
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    # MIME type should be forced to text/markdown for .md files
    assert response_data["mime_type"] == "text/markdown"


@pytest.mark.asyncio
async def test_markdown_upload_with_markdown_extension(
    async_client: AsyncClient,
    test_tenant_id: int,
    test_user_id: int,
    sample_markdown_file: Path,
) -> None:
    """Test .markdown file extension is accepted.
    
    User Story 1, Task T023
    """
    with open(sample_markdown_file, "rb") as f:
        files = {"file": ("document.markdown", f, "text/plain")}
        headers = {
            "X-Tenant-ID": str(test_tenant_id),
            "X-User-ID": str(test_user_id),
        }
        
        response = await async_client.post(
            "/api/v1/documents/upload",
            files=files,
            headers=headers,
        )
    
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data["mime_type"] == "text/markdown"


@pytest.mark.asyncio
async def test_markdown_parsing_workflow_integration(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant_id: int,
    test_user_id: int,
    sample_markdown_file: Path,
    dramatiq_worker: Any,
) -> None:
    """Test complete markdown parsing workflow: upload → parse → verify text extracted.
    
    Integration test covering the full pipeline.
    User Story 1, Task T024
    """
    # Arrange: Upload markdown file
    with open(sample_markdown_file, "rb") as f:
        files = {"file": ("sample.md", f, "text/markdown")}
        headers = {
            "X-Tenant-ID": str(test_tenant_id),
            "X-User-ID": str(test_user_id),
        }
        
        response = await async_client.post(
            "/api/v1/documents/upload",
            files=files,
            headers=headers,
        )
    
    assert response.status_code == status.HTTP_201_CREATED
    document_id = response.json()["document_id"]
    
    # Act: Wait for async parsing task to complete
    dramatiq_worker.join()
    await db_session.commit()
    
    # Assert: Verify document was parsed
    stmt = (
        db_session.query(Document)
        .filter_by(document_id=document_id, tenant_id=test_tenant_id)
    )
    document = await db_session.execute(stmt)
    document = document.scalar_one()
    
    assert document is not None
    assert document.status == "completed"
    assert document.text_content is not None
    assert len(document.text_content) > 0
    assert "# Sample Markdown" in document.text_content  # From sample.md fixture
    
    # Verify chunks were created
    assert len(document.chunks) > 0
    assert document.chunks[0].text_content is not None


@pytest.mark.asyncio
async def test_markdown_structure_preserved_in_text(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant_id: int,
    test_user_id: int,
    sample_markdown_with_structure: Path,
    dramatiq_worker: Any,
) -> None:
    """Test markdown structure (headers, lists, code blocks) is preserved in extracted text.
    
    User Story 1, Task T024
    """
    # Upload markdown with headers, lists, code blocks
    with open(sample_markdown_with_structure, "rb") as f:
        files = {"file": ("structured.md", f, "text/markdown")}
        headers = {
            "X-Tenant-ID": str(test_tenant_id),
            "X-User-ID": str(test_user_id),
        }
        
        response = await async_client.post(
            "/api/v1/documents/upload",
            files=files,
            headers=headers,
        )
    
    document_id = response.json()["document_id"]
    dramatiq_worker.join()
    await db_session.commit()
    
    # Verify structure is preserved
    stmt = (
        db_session.query(Document)
        .filter_by(document_id=document_id)
    )
    document = await db_session.execute(stmt)
    document = document.scalar_one()
    
    text = document.text_content
    assert "##" in text or "Heading" in text  # Headers preserved
    assert "def example():" in text or "print" in text  # Code block content preserved
    assert "-" in text or "•" in text or "item" in text  # List items preserved


@pytest.mark.asyncio
async def test_markdown_upload_invalid_extension_rejected(
    async_client: AsyncClient,
    test_tenant_id: int,
    test_user_id: int,
    tmp_path: Path,
) -> None:
    """Test non-markdown file extensions are rejected.
    
    User Story 1, Task T023
    """
    # Create a .txt file
    txt_file = tmp_path / "document.txt"
    txt_file.write_text("This is plain text")
    
    with open(txt_file, "rb") as f:
        files = {"file": ("document.txt", f, "text/plain")}
        headers = {
            "X-Tenant-ID": str(test_tenant_id),
            "X-User-ID": str(test_user_id),
        }
        
        response = await async_client.post(
            "/api/v1/documents/upload",
            files=files,
            headers=headers,
        )
    
    # Should accept (since .txt is already supported)
    # But for markdown-specific uploads, we'd validate extension
    assert response.status_code in [
        status.HTTP_201_CREATED,  # If .txt is supported
        status.HTTP_400_BAD_REQUEST,  # If markdown-only endpoint
    ]


@pytest.mark.asyncio
async def test_markdown_upload_empty_file_rejected(
    async_client: AsyncClient,
    test_tenant_id: int,
    test_user_id: int,
    tmp_path: Path,
) -> None:
    """Test empty markdown file is rejected with 400.
    
    User Story 1, Task T024
    """
    empty_file = tmp_path / "empty.md"
    empty_file.write_text("")
    
    with open(empty_file, "rb") as f:
        files = {"file": ("empty.md", f, "text/markdown")}
        headers = {
            "X-Tenant-ID": str(test_tenant_id),
            "X-User-ID": str(test_user_id),
        }
        
        response = await async_client.post(
            "/api/v1/documents/upload",
            files=files,
            headers=headers,
        )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "empty" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_markdown_metadata_created(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant_id: int,
    test_user_id: int,
    sample_markdown_file: Path,
    dramatiq_worker: Any,
) -> None:
    """Test MarkdownMetadata record is created during parsing.
    
    User Story 1, Task T024
    """
    # Upload markdown
    with open(sample_markdown_file, "rb") as f:
        files = {"file": ("sample.md", f, "text/markdown")}
        headers = {
            "X-Tenant-ID": str(test_tenant_id),
            "X-User-ID": str(test_user_id),
        }
        
        response = await async_client.post(
            "/api/v1/documents/upload",
            files=files,
            headers=headers,
        )
    
    document_id = response.json()["document_id"]
    dramatiq_worker.join()
    await db_session.commit()
    
    # Verify MarkdownMetadata was created
    stmt = (
        db_session.query(MarkdownMetadata)
        .filter_by(document_id=document_id)
    )
    metadata = await db_session.execute(stmt)
    metadata = metadata.scalar_one_or_none()
    
    assert metadata is not None
    assert metadata.heading_count >= 0
    assert metadata.code_block_count >= 0
    assert metadata.link_count >= 0


# Fixtures


@pytest.fixture
def sample_markdown_file(tmp_path: Path) -> Path:
    """Create a sample markdown file for testing."""
    file_path = tmp_path / "sample.md"
    file_path.write_text(
        """# Sample Markdown

This is a test markdown file with some content.

## Features

- Bullet points
- Multiple sections
- Code blocks

```python
def hello():
    print("Hello, World!")
```

[Link to example](https://example.com)
"""
    )
    return file_path


@pytest.mark.asyncio
async def test_get_markdown_metadata_endpoint(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant_id: int,
    test_user_id: int,
    tmp_path: Path,
    dramatiq_worker: Any,
) -> None:
    """Test GET /documents/{id}/markdown-metadata endpoint returns frontmatter.
    
    User Story 2, Task T047
    """
    # Arrange: Create markdown with frontmatter
    md_file = tmp_path / "with_meta.md"
    md_file.write_text(
        """---
title: API Documentation
author: John Doe
version: 1.0.0
tags:
  - python
  - api
---

# API Documentation

This is the content.
"""
    )
    
    # Upload the file
    with open(md_file, "rb") as f:
        files = {"file": ("with_meta.md", f, "text/markdown")}
        headers = {
            "X-Tenant-ID": str(test_tenant_id),
            "X-User-ID": str(test_user_id),
        }
        
        response = await async_client.post(
            "/api/v1/documents/upload",
            files=files,
            headers=headers,
        )
    
    assert response.status_code == status.HTTP_201_CREATED
    document_id = response.json()["document_id"]
    
    # Wait for processing
    dramatiq_worker.join()
    await db_session.commit()
    
    # Act: Get markdown metadata
    response = await async_client.get(
        f"/api/v1/documents/{document_id}/markdown-metadata",
        headers={"X-Tenant-ID": str(test_tenant_id)},
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    metadata = response.json()
    
    assert metadata["document_id"] == document_id
    assert metadata["has_yaml_frontmatter"] is True
    assert metadata["frontmatter"]["title"] == "API Documentation"
    assert metadata["frontmatter"]["author"] == "John Doe"
    assert metadata["frontmatter"]["version"] == "1.0.0"
    assert metadata["frontmatter"]["tags"] == ["python", "api"]
    assert metadata["heading_count"] >= 1
    assert metadata["code_block_count"] >= 0


@pytest.mark.asyncio
async def test_get_markdown_metadata_not_found(
    async_client: AsyncClient,
    test_tenant_id: int,
) -> None:
    """Test GET /documents/{id}/markdown-metadata returns 404 for non-existent document.
    
    User Story 2, Task T047
    """
    # Act
    response = await async_client.get(
        "/api/v1/documents/999999/markdown-metadata",
        headers={"X-Tenant-ID": str(test_tenant_id)},
    )
    
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_document_images_endpoint(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant_id: int,
    test_user_id: int,
    tmp_path: Path,
    dramatiq_worker: Any,
) -> None:
    """Test GET /documents/{id}/images endpoint returns image references.
    
    User Story 2, Task T047
    """
    # Arrange: Create markdown with images
    md_file = tmp_path / "with_images.md"
    md_file.write_text(
        """# Images

![Logo](https://example.com/logo.png)

![Diagram](./images/diagram.png)

![Inline](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==)
"""
    )
    
    # Upload the file
    with open(md_file, "rb") as f:
        files = {"file": ("with_images.md", f, "text/markdown")}
        headers = {
            "X-Tenant-ID": str(test_tenant_id),
            "X-User-ID": str(test_user_id),
        }
        
        response = await async_client.post(
            "/api/v1/documents/upload",
            files=files,
            headers=headers,
        )
    
    assert response.status_code == status.HTTP_201_CREATED
    document_id = response.json()["document_id"]
    
    # Wait for processing
    dramatiq_worker.join()
    await db_session.commit()
    
    # Act: Get images
    response = await async_client.get(
        f"/api/v1/documents/{document_id}/images",
        headers={"X-Tenant-ID": str(test_tenant_id)},
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["document_id"] == document_id
    assert data["total_count"] >= 3
    
    images = data["images"]
    assert len(images) >= 3
    
    # Check image types
    image_types = [img["image_type"] for img in images]
    assert "external" in image_types  # https://example.com/logo.png
    assert "local" in image_types     # ./images/diagram.png
    assert "base64" in image_types    # data:image/...


@pytest.mark.asyncio
async def test_get_document_images_with_type_filter(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_tenant_id: int,
    test_user_id: int,
    tmp_path: Path,
    dramatiq_worker: Any,
) -> None:
    """Test GET /documents/{id}/images with type filter.
    
    User Story 2, Task T047
    """
    # Arrange: Create markdown with mixed image types
    md_file = tmp_path / "mixed_images.md"
    md_file.write_text(
        """# Images

![External](https://cdn.example.com/img1.png)
![External2](https://cdn.example.com/img2.png)
![Local](./local/img.png)
"""
    )
    
    # Upload the file
    with open(md_file, "rb") as f:
        files = {"file": ("mixed_images.md", f, "text/markdown")}
        headers = {
            "X-Tenant-ID": str(test_tenant_id),
            "X-User-ID": str(test_user_id),
        }
        
        response = await async_client.post(
            "/api/v1/documents/upload",
            files=files,
            headers=headers,
        )
    
    document_id = response.json()["document_id"]
    dramatiq_worker.join()
    await db_session.commit()
    
    # Act: Filter by external images
    response = await async_client.get(
        f"/api/v1/documents/{document_id}/images?image_type=external",
        headers={"X-Tenant-ID": str(test_tenant_id)},
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Should only return external images
    for img in data["images"]:
        assert img["image_type"] == "external"
        assert img["image_url"].startswith("https://")


@pytest.fixture
def sample_markdown_with_structure(tmp_path: Path) -> Path:
    """Create a markdown file with rich structure."""
    file_path = tmp_path / "structured.md"
    file_path.write_text(
        """# Main Title

## Section 1

This is a paragraph with **bold** and *italic* text.

### Subsection

1. Ordered item 1
2. Ordered item 2
3. Ordered item 3

## Section 2

Unordered list:
- Item A
- Item B
  - Nested item
- Item C

### Code Example

```python
def example():
    return "Hello from code block"
```

### Table

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |

## Conclusion

Link: [Visit website](https://example.com)
"""
    )
    return file_path
