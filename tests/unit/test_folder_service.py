"""Unit tests for FolderService.

Tests folder traversal, markdown file discovery, and circular symlink detection.
User Story 3: Batch Folder Ingestion (Priority: P2)
"""

import os
from pathlib import Path

import pytest

from src.ingestion_parsing.services.folder_service import FolderService


@pytest.mark.asyncio
async def test_discover_markdown_files_basic(tmp_path: Path) -> None:
    """Test basic markdown file discovery in a folder.
    
    User Story 3, Task T066
    """
    # Arrange
    folder = tmp_path / "docs"
    folder.mkdir()
    
    (folder / "readme.md").write_text("# README")
    (folder / "guide.md").write_text("# Guide")
    (folder / "notes.txt").write_text("Not markdown")
    
    service = FolderService()
    
    # Act
    files = await service.discover_markdown_files(folder)
    
    # Assert
    assert len(files) == 2
    filenames = [f.name for f in files]
    assert "readme.md" in filenames
    assert "guide.md" in filenames
    assert "notes.txt" not in filenames


@pytest.mark.asyncio
async def test_discover_markdown_files_recursive(tmp_path: Path) -> None:
    """Test recursive discovery of markdown files in nested folders.
    
    User Story 3, Task T066
    """
    # Arrange
    root = tmp_path / "project"
    root.mkdir()
    
    (root / "README.md").write_text("# Root README")
    
    docs = root / "docs"
    docs.mkdir()
    (docs / "guide.md").write_text("# Guide")
    
    api = docs / "api"
    api.mkdir()
    (api / "reference.md").write_text("# API Reference")
    
    service = FolderService()
    
    # Act
    files = await service.discover_markdown_files(root)
    
    # Assert
    assert len(files) == 3
    filenames = [f.name for f in files]
    assert "README.md" in filenames
    assert "guide.md" in filenames
    assert "reference.md" in filenames


@pytest.mark.asyncio
async def test_discover_markdown_files_with_test_folder_fixture() -> None:
    """Test discovery using existing test_folder fixture.
    
    User Story 3, Task T066
    """
    # Arrange
    test_folder = Path("tests/fixtures/sample_documents/test_folder")
    
    if not test_folder.exists():
        pytest.skip("Test folder fixture not found")
    
    service = FolderService()
    
    # Act
    files = await service.discover_markdown_files(test_folder)
    
    # Assert
    assert len(files) > 0
    assert all(f.suffix.lower() in [".md", ".markdown"] for f in files)


@pytest.mark.asyncio
async def test_discover_markdown_files_circular_symlink_detection(
    tmp_path: Path,
) -> None:
    """Test that circular symlinks are detected and don't cause infinite loops.
    
    User Story 3, Task T067
    """
    # Arrange
    root = tmp_path / "circular"
    root.mkdir()
    
    (root / "file1.md").write_text("# File 1")
    
    subdir = root / "subdir"
    subdir.mkdir()
    (subdir / "file2.md").write_text("# File 2")
    
    # Create circular symlink
    try:
        circular_link = subdir / "circular"
        circular_link.symlink_to(root, target_is_directory=True)
    except OSError:
        pytest.skip("Cannot create symlinks on this system")
    
    service = FolderService()
    
    # Act - should not hang or crash
    files = await service.discover_markdown_files(root)
    
    # Assert - should find files without infinite loop
    assert len(files) == 2
    filenames = [f.name for f in files]
    assert "file1.md" in filenames
    assert "file2.md" in filenames


@pytest.mark.asyncio
async def test_discover_markdown_files_max_depth_limit(tmp_path: Path) -> None:
    """Test that max depth limit is respected.
    
    User Story 3, Task T072
    """
    # Arrange: Create deeply nested structure
    current = tmp_path / "deep"
    current.mkdir()
    
    # Create 25 levels deep (exceeds default max of 20)
    for i in range(25):
        (current / f"file{i}.md").write_text(f"# File {i}")
        next_dir = current / f"level{i}"
        next_dir.mkdir()
        current = next_dir
    
    (current / "deep_file.md").write_text("# Deep File")
    
    service = FolderService(max_depth=20)
    
    # Act
    files = await service.discover_markdown_files(tmp_path / "deep")
    
    # Assert - should find files up to depth 20, not beyond
    assert len(files) <= 20  # Should stop at max depth


@pytest.mark.asyncio
async def test_discover_markdown_files_permission_error_handling(
    tmp_path: Path,
) -> None:
    """Test graceful handling of permission errors.
    
    User Story 3, Task T073
    """
    # Arrange
    root = tmp_path / "restricted"
    root.mkdir()
    
    (root / "accessible.md").write_text("# Accessible")
    
    restricted = root / "restricted_dir"
    restricted.mkdir()
    (restricted / "hidden.md").write_text("# Hidden")
    
    # Remove read permissions
    try:
        os.chmod(restricted, 0o000)
    except OSError:
        pytest.skip("Cannot change permissions on this system")
    
    service = FolderService()
    
    try:
        # Act - should not crash
        files = await service.discover_markdown_files(root)
        
        # Assert - should find accessible file, skip restricted
        filenames = [f.name for f in files]
        assert "accessible.md" in filenames
        # hidden.md may or may not be found depending on permissions
    finally:
        # Restore permissions for cleanup
        try:
            os.chmod(restricted, 0o755)
        except OSError:
            pass


@pytest.mark.asyncio
async def test_discover_markdown_files_empty_folder(tmp_path: Path) -> None:
    """Test discovery in empty folder returns empty list.
    
    User Story 3, Task T066
    """
    # Arrange
    empty = tmp_path / "empty"
    empty.mkdir()
    
    service = FolderService()
    
    # Act
    files = await service.discover_markdown_files(empty)
    
    # Assert
    assert len(files) == 0


@pytest.mark.asyncio
async def test_discover_markdown_files_mixed_extensions(tmp_path: Path) -> None:
    """Test discovery finds both .md and .markdown extensions.
    
    User Story 3, Task T066
    """
    # Arrange
    folder = tmp_path / "mixed"
    folder.mkdir()
    
    (folder / "file1.md").write_text("# File 1")
    (folder / "file2.markdown").write_text("# File 2")
    (folder / "file3.MD").write_text("# File 3")  # Uppercase
    (folder / "file4.txt").write_text("Not markdown")
    
    service = FolderService()
    
    # Act
    files = await service.discover_markdown_files(folder)
    
    # Assert
    assert len(files) == 3
    extensions = [f.suffix.lower() for f in files]
    assert ".md" in extensions or ".markdown" in extensions


@pytest.mark.asyncio
async def test_discover_markdown_files_preserves_relative_paths(
    tmp_path: Path,
) -> None:
    """Test that relative paths are preserved for discovered files.
    
    User Story 3, Task T078
    """
    # Arrange
    root = tmp_path / "project"
    root.mkdir()
    
    docs = root / "docs"
    docs.mkdir()
    (docs / "guide.md").write_text("# Guide")
    
    api = docs / "api"
    api.mkdir()
    (api / "reference.md").write_text("# Reference")
    
    service = FolderService()
    
    # Act
    files = await service.discover_markdown_files(root)
    
    # Assert
    relative_paths = [f.relative_to(root) for f in files]
    assert Path("docs/guide.md") in relative_paths
    assert Path("docs/api/reference.md") in relative_paths


@pytest.mark.asyncio
async def test_discover_markdown_files_ignores_hidden_files(tmp_path: Path) -> None:
    """Test that hidden files (starting with .) are optionally ignored.
    
    User Story 3, Task T066
    """
    # Arrange
    folder = tmp_path / "with_hidden"
    folder.mkdir()
    
    (folder / "visible.md").write_text("# Visible")
    (folder / ".hidden.md").write_text("# Hidden")
    
    hidden_dir = folder / ".hidden_dir"
    hidden_dir.mkdir()
    (hidden_dir / "file.md").write_text("# In Hidden Dir")
    
    service = FolderService(ignore_hidden=True)
    
    # Act
    files = await service.discover_markdown_files(folder)
    
    # Assert
    filenames = [f.name for f in files]
    assert "visible.md" in filenames
    # Hidden files should be ignored if ignore_hidden=True
    if service.ignore_hidden:
        assert ".hidden.md" not in filenames


@pytest.mark.asyncio
async def test_create_batch(db_session_mock) -> None:
    """Test FolderBatch creation.
    
    User Story 3, Task T074
    """
    # Arrange
    service = FolderService()
    
    # Act
    batch = await service.create_batch(
        tenant_id=1,
        user_id=5,
        folder_path="/uploads/docs",
        original_folder_name="docs",
    )
    
    # Assert
    assert batch.tenant_id == 1
    assert batch.user_id == 5
    assert batch.folder_path == "/uploads/docs"
    assert batch.original_folder_name == "docs"
    assert batch.status == "discovering"
    assert batch.total_files_discovered == 0
    assert batch.files_processed == 0
    assert batch.files_failed == 0


# Mock fixture for database session
@pytest.fixture
def db_session_mock():
    """Mock database session for unit tests."""
    class MockSession:
        def add(self, obj):
            pass
        
        async def flush(self):
            pass
        
        async def commit(self):
            pass
    
    return MockSession()
