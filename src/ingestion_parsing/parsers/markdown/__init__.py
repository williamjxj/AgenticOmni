"""Markdown parsing utilities.

This package contains specialized utilities for parsing markdown files:
- frontmatter: YAML frontmatter extraction
- mermaid: Mermaid diagram detection
- image_extractor: Image reference extraction
- structure: Structural element identification
"""

from src.ingestion_parsing.parsers.markdown.frontmatter import extract_frontmatter
from src.ingestion_parsing.parsers.markdown.image_extractor import (
    extract_image_references,
)
from src.ingestion_parsing.parsers.markdown.mermaid import extract_mermaid_diagrams
from src.ingestion_parsing.parsers.markdown.structure import (
    extract_structural_elements,
)

__all__ = [
    "extract_frontmatter",
    "extract_image_references",
    "extract_mermaid_diagrams",
    "extract_structural_elements",
]
