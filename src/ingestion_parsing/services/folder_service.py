"""Folder service for batch markdown file discovery and processing.

Handles recursive folder traversal, markdown file discovery, and batch creation.
"""

import logging
import os
from pathlib import Path
from typing import Any

import structlog

from src.shared.config import settings
from src.storage_indexing.models.folder_batch import FolderBatch

logger = structlog.get_logger(__name__)


class FolderService:
    """Service for folder-based markdown file operations.
    
    Provides recursive folder traversal, markdown file discovery,
    circular symlink detection, and batch management.
    
    Example:
        >>> service = FolderService(max_depth=20)
        >>> files = await service.discover_markdown_files(Path("/docs"))
        >>> print(f"Found {len(files)} markdown files")
    """
    
    def __init__(
        self,
        max_depth: int | None = None,
        ignore_hidden: bool = True,
    ) -> None:
        """Initialize folder service.
        
        Args:
            max_depth: Maximum directory depth to traverse (default from settings)
            ignore_hidden: Whether to ignore hidden files/directories (default True)
        """
        self.max_depth = max_depth or getattr(settings, "folder_max_depth", 20)
        self.ignore_hidden = ignore_hidden
        self._visited_inodes: set[tuple[int, int]] = set()
    
    async def discover_markdown_files(
        self,
        folder_path: Path,
        _current_depth: int = 0,
    ) -> list[Path]:
        """Recursively discover all markdown files in a folder.
        
        Traverses the directory tree and finds all .md and .markdown files.
        Handles circular symlinks, max depth limits, and permission errors.
        
        Args:
            folder_path: Root folder to search
            _current_depth: Internal parameter for tracking recursion depth
            
        Returns:
            List of Path objects for discovered markdown files
            
        Raises:
            FileNotFoundError: If folder_path doesn't exist
            
        Example:
            >>> service = FolderService()
            >>> files = await service.discover_markdown_files(Path("/docs"))
            >>> for file in files:
            ...     print(file.relative_to(Path("/docs")))
        """
        if not folder_path.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        
        if not folder_path.is_dir():
            raise ValueError(f"Path is not a directory: {folder_path}")
        
        # Check max depth
        if _current_depth >= self.max_depth:
            logger.warning(
                "Max depth reached, stopping traversal",
                folder_path=str(folder_path),
                max_depth=self.max_depth,
            )
            return []
        
        markdown_files: list[Path] = []
        
        try:
            for entry in folder_path.iterdir():
                # Skip hidden files/directories if configured
                if self.ignore_hidden and entry.name.startswith("."):
                    continue
                
                try:
                    # Check for circular symlinks
                    if entry.is_symlink():
                        stat_info = entry.stat()
                        inode_key = (stat_info.st_dev, stat_info.st_ino)
                        
                        if inode_key in self._visited_inodes:
                            logger.warning(
                                "Circular symlink detected, skipping",
                                path=str(entry),
                            )
                            continue
                        
                        self._visited_inodes.add(inode_key)
                    
                    # Process directories recursively
                    if entry.is_dir():
                        nested_files = await self.discover_markdown_files(
                            entry,
                            _current_depth=_current_depth + 1,
                        )
                        markdown_files.extend(nested_files)
                    
                    # Check if file is markdown
                    elif entry.is_file():
                        if self._is_markdown_file(entry):
                            markdown_files.append(entry)
                
                except PermissionError:
                    logger.warning(
                        "Permission denied, skipping",
                        path=str(entry),
                    )
                    continue
                except OSError as e:
                    logger.warning(
                        "OS error accessing path, skipping",
                        path=str(entry),
                        error=str(e),
                    )
                    continue
        
        except PermissionError:
            logger.warning(
                "Permission denied for directory",
                folder_path=str(folder_path),
            )
        
        return markdown_files
    
    def _is_markdown_file(self, file_path: Path) -> bool:
        """Check if a file is a markdown file.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file has .md or .markdown extension
        """
        return file_path.suffix.lower() in [".md", ".markdown"]
    
    async def create_batch(
        self,
        tenant_id: int,
        user_id: int | None,
        folder_path: str,
        original_folder_name: str,
    ) -> FolderBatch:
        """Create a new FolderBatch record.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User who initiated the upload
            folder_path: Path to the uploaded folder
            original_folder_name: Original name of the folder
            
        Returns:
            Created FolderBatch instance
            
        Example:
            >>> batch = await service.create_batch(
            ...     tenant_id=1,
            ...     user_id=5,
            ...     folder_path="/uploads/docs",
            ...     original_folder_name="docs",
            ... )
            >>> print(f"Batch {batch.id} created with status: {batch.status}")
        """
        batch = FolderBatch(
            tenant_id=tenant_id,
            user_id=user_id,
            folder_path=folder_path,
            original_folder_name=original_folder_name,
            status="discovering",
            total_files_discovered=0,
            files_processed=0,
            files_failed=0,
        )
        
        logger.info(
            "FolderBatch created",
            tenant_id=tenant_id,
            user_id=user_id,
            folder_path=folder_path,
        )
        
        return batch
    
    def reset_visited_inodes(self) -> None:
        """Reset the visited inodes set for circular symlink detection.
        
        Call this between different folder traversals to avoid false positives.
        """
        self._visited_inodes.clear()
