"""Frontmatter extraction utilities for markdown files.

Extracts YAML/TOML frontmatter from markdown documents using python-frontmatter.
"""

from pathlib import Path
from typing import Any

import frontmatter


def extract_frontmatter(file_path: Path) -> tuple[dict[str, Any], str]:
    """Extract YAML frontmatter from a markdown file.
    
    Args:
        file_path: Path to the markdown file.
        
    Returns:
        A tuple of (metadata_dict, content_without_frontmatter).
        If no frontmatter exists, returns (empty dict, original content).
        
    Raises:
        FileNotFoundError: If the file does not exist.
        UnicodeDecodeError: If the file is not UTF-8 encoded.
        
    Examples:
        >>> file_path = Path("document.md")
        >>> metadata, content = extract_frontmatter(file_path)
        >>> print(metadata.get("title"))
        "My Document"
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Read and parse frontmatter
    with open(file_path, "r", encoding="utf-8") as f:
        post = frontmatter.load(f)
    
    # Extract metadata and content
    metadata = dict(post.metadata) if post.metadata else {}
    content = post.content
    
    return metadata, content


def has_frontmatter(file_path: Path) -> bool:
    """Check if a markdown file has YAML frontmatter.
    
    Args:
        file_path: Path to the markdown file.
        
    Returns:
        True if frontmatter exists, False otherwise.
        
    Examples:
        >>> if has_frontmatter(Path("doc.md")):
        ...     print("Has frontmatter")
    """
    try:
        metadata, _ = extract_frontmatter(file_path)
        return len(metadata) > 0
    except (FileNotFoundError, UnicodeDecodeError):
        return False
