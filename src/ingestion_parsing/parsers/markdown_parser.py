"""Markdown parser for extracting text and metadata from markdown files.

Uses marko for markdown parsing and python-frontmatter for frontmatter extraction.
"""

import logging
from pathlib import Path
from typing import Any

import marko
from marko.ext.gfm import gfm

from src.ingestion_parsing.models.parsing_result import ParsingResult
from src.ingestion_parsing.parsers.base import BaseParser
from src.ingestion_parsing.parsers.markdown.frontmatter import extract_frontmatter
from src.ingestion_parsing.parsers.markdown.image_extractor import (
    extract_image_references,
)
from src.ingestion_parsing.parsers.markdown.mermaid import extract_mermaid_diagrams
from src.ingestion_parsing.parsers.markdown.structure import (
    count_structural_elements,
    extract_structural_elements,
)

logger = logging.getLogger(__name__)


class MarkdownParser(BaseParser):
    """Parses markdown files to extract text content and metadata.
    
    Uses marko with GFM (GitHub Flavored Markdown) extensions for parsing.
    Extracts:
    - Plain text content with structure preserved
    - YAML frontmatter metadata
    - Structural elements (headings, code blocks, lists, tables)
    - Image references
    - Mermaid diagrams
    - Link URLs
    """

    def __init__(self) -> None:
        """Initialize the MarkdownParser with GFM support."""
        self.md = marko.Markdown(extensions=[gfm])

    async def parse(self, file_path: Path) -> ParsingResult:
        """Parse a markdown file and return its content and metadata.

        Args:
            file_path: The path to the markdown file.

        Returns:
            A ParsingResult object containing the extracted text, metadata,
            and structural elements.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            UnicodeDecodeError: If the file is not UTF-8 encoded.
            ValueError: If parsing fails.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Markdown file not found: {file_path}")
        
        try:
            # Extract frontmatter first
            frontmatter_metadata, content_without_frontmatter = extract_frontmatter(
                file_path
            )
            
            # Extract text content
            text_content = await self.extract_text(file_path)
            
            # Extract metadata
            metadata = await self.extract_metadata(file_path)
            
            # Add frontmatter to metadata
            if frontmatter_metadata:
                metadata["frontmatter"] = frontmatter_metadata
                metadata["has_yaml_frontmatter"] = True
            else:
                metadata["has_yaml_frontmatter"] = False
            
            # Extract structural elements
            structural_elements = extract_structural_elements(
                content_without_frontmatter
            )
            
            # Extract sections (heading text)
            sections = [
                elem["content_preview"]
                for elem in structural_elements
                if elem["type"] == "heading"
            ]
            
            # Determine has_tables and has_images
            has_tables = metadata.get("table_count", 0) > 0
            has_images = metadata.get("image_count", 0) > 0
            
            logger.info(
                f"Parsed markdown file: {file_path.name}, "
                f"headings={metadata.get('heading_count', 0)}, "
                f"code_blocks={metadata.get('code_block_count', 0)}, "
                f"links={metadata.get('link_count', 0)}, "
                f"images={metadata.get('image_count', 0)}"
            )
            
            return ParsingResult(
                document_id=0,  # Will be set by the service layer
                text_content=text_content,
                metadata=metadata,
                structural_elements=structural_elements,
                has_tables=has_tables,
                has_images=has_images,
                sections=sections,
            )
        
        except UnicodeDecodeError as e:
            logger.error(f"Failed to decode markdown file {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to parse markdown file {file_path}: {e}")
            # Graceful degradation: return minimal result
            return ParsingResult(
                document_id=0,
                text_content="",
                metadata={"error": str(e)},
                structural_elements=[],
            )

    async def extract_text(self, file_path: Path) -> str:
        """Extract plain text content from the markdown file.
        
        Walks the marko AST and extracts text content while preserving structure.
        
        Args:
            file_path: The path to the markdown file.
            
        Returns:
            Extracted text content as a string.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            UnicodeDecodeError: If the file is not UTF-8 encoded.
        """
        # Extract frontmatter first to get content without frontmatter
        _, content_without_frontmatter = extract_frontmatter(file_path)
        
        # Parse markdown
        doc = self.md.parse(content_without_frontmatter)
        
        # Extract text by rendering to plain text
        text_content = self._extract_text_from_ast(doc)
        
        return text_content.strip()

    async def extract_metadata(self, file_path: Path) -> dict[str, Any]:
        """Extract metadata from the markdown file.
        
        Extracts:
        - Structural element counts (headings, code blocks, lists, tables)
        - Link URLs
        - Image references
        - Mermaid diagram count
        
        Args:
            file_path: The path to the markdown file.
            
        Returns:
            Dictionary containing markdown metadata.
            
        Raises:
            FileNotFoundError: If the file does not exist.
        """
        # Read content without frontmatter
        _, content = extract_frontmatter(file_path)
        
        # Count structural elements
        counts = count_structural_elements(content)
        
        # Extract link URLs
        link_urls = self._extract_link_urls(content)
        
        # Extract image references
        image_refs = extract_image_references(content, file_path)
        
        # Extract Mermaid diagrams
        mermaid_diagrams = extract_mermaid_diagrams(content)
        
        metadata = {
            "heading_count": counts["heading_count"],
            "code_block_count": counts["code_block_count"],
            "list_count": counts["list_count"],
            "table_count": counts["table_count"],
            "blockquote_count": counts["blockquote_count"],
            "link_count": len(link_urls),
            "image_count": len(image_refs),
            "link_urls": link_urls,
            "image_references": image_refs,
            "mermaid_diagram_count": len(mermaid_diagrams),
            "mermaid_diagrams": mermaid_diagrams,
        }
        
        return metadata

    def _extract_text_from_ast(self, node: Any) -> str:
        """Extract text content from a marko AST node.
        
        Recursively traverses the AST and collects text content.
        
        Args:
            node: A marko AST node.
            
        Returns:
            Extracted text as a string.
        """
        text_parts = []
        self._collect_text_recursive(node, text_parts)
        return "".join(text_parts)

    def _collect_text_recursive(self, node: Any, text_parts: list[str]) -> None:
        """Recursively collect text from an AST node.
        
        Args:
            node: A marko AST node.
            text_parts: A list to append text parts to.
        """
        if isinstance(node, str):
            text_parts.append(node)
            return
        
        if hasattr(node, "children"):
            if isinstance(node.children, str):
                text_parts.append(node.children)
                # Add newline after block elements
                if hasattr(node, "__class__") and "Block" in node.__class__.__name__:
                    text_parts.append("\n")
            elif isinstance(node.children, list):
                for child in node.children:
                    self._collect_text_recursive(child, text_parts)
                # Add newline after block elements
                if hasattr(node, "__class__") and "Block" in node.__class__.__name__:
                    text_parts.append("\n")
            else:
                self._collect_text_recursive(node.children, text_parts)

    def _extract_link_urls(self, markdown_content: str) -> list[str]:
        """Extract link URLs from markdown content.
        
        Args:
            markdown_content: The raw markdown content.
            
        Returns:
            A list of link URLs.
        """
        from marko.inline import Link
        
        doc = self.md.parse(markdown_content)
        urls = []
        
        def traverse(node: Any) -> None:
            """Recursively traverse AST to find Link nodes."""
            if isinstance(node, Link):
                urls.append(node.dest)
            
            if hasattr(node, "children") and node.children:
                for child in node.children:
                    if hasattr(child, "children") or isinstance(child, Link):
                        traverse(child)
        
        traverse(doc)
        return urls

    def supports_format(self, mime_type: str) -> bool:
        """Check if this parser supports the given MIME type.
        
        Args:
            mime_type: MIME type to check.
            
        Returns:
            True if markdown MIME type, False otherwise.
        """
        return mime_type in ["text/markdown", "text/x-markdown", "text/plain"]
