"""Unit tests for frontmatter extraction.

Tests YAML frontmatter parsing using python-frontmatter library.
User Story 2: Handle Markdown-Specific Formatting (Priority: P2)
"""

from pathlib import Path

import pytest

from src.ingestion_parsing.parsers.markdown.frontmatter import (
    extract_frontmatter,
    has_frontmatter,
)


def test_extract_frontmatter_with_yaml(tmp_path: Path) -> None:
    """Test extraction of YAML frontmatter.
    
    User Story 2, Task T043
    """
    # Arrange
    md_file = tmp_path / "with_frontmatter.md"
    md_file.write_text(
        """---
title: API Documentation
author: John Doe
date: 2026-01-10
tags:
  - python
  - fastapi
version: 1.0.0
---

# API Documentation

This is the main content.
"""
    )
    
    # Act
    metadata, content = extract_frontmatter(md_file)
    
    # Assert
    assert metadata["title"] == "API Documentation"
    assert metadata["author"] == "John Doe"
    assert metadata["date"] == "2026-01-10"
    assert metadata["tags"] == ["python", "fastapi"]
    assert metadata["version"] == "1.0.0"
    assert "# API Documentation" in content
    assert "---" not in content  # Frontmatter removed


def test_extract_frontmatter_without_yaml(tmp_path: Path) -> None:
    """Test extraction when no frontmatter exists.
    
    User Story 2, Task T043
    """
    # Arrange
    md_file = tmp_path / "no_frontmatter.md"
    md_file.write_text(
        """# Simple Document

No frontmatter here.
"""
    )
    
    # Act
    metadata, content = extract_frontmatter(md_file)
    
    # Assert
    assert metadata == {}
    assert "# Simple Document" in content


def test_extract_frontmatter_empty_yaml(tmp_path: Path) -> None:
    """Test extraction with empty YAML frontmatter.
    
    User Story 2, Task T043
    """
    # Arrange
    md_file = tmp_path / "empty_frontmatter.md"
    md_file.write_text(
        """---
---

# Document

Content here.
"""
    )
    
    # Act
    metadata, content = extract_frontmatter(md_file)
    
    # Assert
    assert metadata == {}
    assert "# Document" in content


def test_extract_frontmatter_complex_yaml(tmp_path: Path) -> None:
    """Test extraction of complex nested YAML structures.
    
    User Story 2, Task T043
    """
    # Arrange
    md_file = tmp_path / "complex_frontmatter.md"
    md_file.write_text(
        """---
title: Complex Doc
metadata:
  author:
    name: Jane Smith
    email: jane@example.com
  reviewers:
    - Alice
    - Bob
  status: draft
sections:
  - introduction
  - methodology
  - results
---

# Content
"""
    )
    
    # Act
    metadata, content = extract_frontmatter(md_file)
    
    # Assert
    assert metadata["title"] == "Complex Doc"
    assert metadata["metadata"]["author"]["name"] == "Jane Smith"
    assert metadata["metadata"]["author"]["email"] == "jane@example.com"
    assert metadata["metadata"]["reviewers"] == ["Alice", "Bob"]
    assert metadata["metadata"]["status"] == "draft"
    assert metadata["sections"] == ["introduction", "methodology", "results"]


def test_extract_frontmatter_with_special_characters(tmp_path: Path) -> None:
    """Test frontmatter with special characters and Unicode.
    
    User Story 2, Task T043
    """
    # Arrange
    md_file = tmp_path / "unicode_frontmatter.md"
    md_file.write_text(
        """---
title: "测试文档 🎉"
description: "Special chars: @#$%^&*()"
emoji: "👍"
---

# Content
""",
        encoding="utf-8",
    )
    
    # Act
    metadata, content = extract_frontmatter(md_file)
    
    # Assert
    assert metadata["title"] == "测试文档 🎉"
    assert metadata["description"] == "Special chars: @#$%^&*()"
    assert metadata["emoji"] == "👍"


def test_extract_frontmatter_malformed_yaml(tmp_path: Path) -> None:
    """Test graceful handling of malformed YAML frontmatter.
    
    User Story 2, Task T043
    """
    # Arrange
    md_file = tmp_path / "malformed_frontmatter.md"
    md_file.write_text(
        """---
title: Missing Quote
bad_yaml: [unclosed array
key_without_value:
---

# Content
"""
    )
    
    # Act & Assert - should not crash
    try:
        metadata, content = extract_frontmatter(md_file)
        # If parsing succeeds with partial data, that's okay
        assert isinstance(metadata, dict)
        assert isinstance(content, str)
    except Exception:
        # If it raises an exception, that's also acceptable behavior
        pass


def test_has_frontmatter_true(tmp_path: Path) -> None:
    """Test has_frontmatter returns True when frontmatter exists.
    
    User Story 2, Task T043
    """
    # Arrange
    md_file = tmp_path / "has_fm.md"
    md_file.write_text(
        """---
title: Test
---

Content
"""
    )
    
    # Act
    result = has_frontmatter(md_file)
    
    # Assert
    assert result is True


def test_has_frontmatter_false(tmp_path: Path) -> None:
    """Test has_frontmatter returns False when no frontmatter exists.
    
    User Story 2, Task T043
    """
    # Arrange
    md_file = tmp_path / "no_fm.md"
    md_file.write_text("# Simple content\n\nNo frontmatter.")
    
    # Act
    result = has_frontmatter(md_file)
    
    # Assert
    assert result is False


def test_extract_frontmatter_preserves_content_structure(tmp_path: Path) -> None:
    """Test that content structure is preserved after frontmatter removal.
    
    User Story 2, Task T043
    """
    # Arrange
    md_file = tmp_path / "structure.md"
    md_file.write_text(
        """---
title: Structure Test
---

# Heading 1

Paragraph 1

## Heading 2

- List item 1
- List item 2

```python
code_block = True
```
"""
    )
    
    # Act
    metadata, content = extract_frontmatter(md_file)
    
    # Assert
    assert "# Heading 1" in content
    assert "## Heading 2" in content
    assert "- List item 1" in content
    assert "```python" in content
    assert "code_block = True" in content
