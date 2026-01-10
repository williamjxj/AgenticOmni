"""PDF parser using Docling for RAG-optimized text extraction."""

from pathlib import Path
from typing import Any

import structlog
from docling.document_converter import DocumentConverter

from src.ingestion_parsing.models.parsing_result import ParsingResult
from src.ingestion_parsing.parsers.base import BaseParser

logger = structlog.get_logger(__name__)


class PDFParser(BaseParser):
    """PDF document parser using Docling library.
    
    Docling is IBM's RAG-optimized document parser that provides:
    - High-quality text extraction
    - Structure preservation (headings, tables, lists)
    - Table extraction and formatting
    - Metadata extraction
    
    Example:
        >>> parser = PDFParser()
        >>> result = parser.parse("/path/to/document.pdf")
        >>> print(result.text_content)
        >>> print(f"Pages: {result.page_count}")
    """

    def __init__(self) -> None:
        """Initialize PDF parser with Docling converter."""
        self.converter = DocumentConverter()
        logger.info("PDFParser initialized with Docling")

    def parse(self, file_path: str) -> ParsingResult:
        """Parse PDF document and extract all content and metadata.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            ParsingResult with text, metadata, and structural information
            
        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If PDF parsing fails
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info("Starting PDF parsing", file_path=file_path)
        
        try:
            # Extract text content
            text_content = self.extract_text(file_path)
            
            # Extract metadata
            metadata = self.extract_metadata(file_path)
            
            # Build parsing result
            result = ParsingResult(
                document_id=0,  # Will be set by calling service
                text_content=text_content,
                page_count=metadata.get("page_count"),
                language=metadata.get("language"),
                metadata=metadata,
                has_tables=metadata.get("has_tables", False),
                has_images=metadata.get("has_images", False),
                sections=metadata.get("sections", []),
            )
            
            logger.info(
                "PDF parsing completed",
                file_path=file_path,
                page_count=result.page_count,
                text_length=len(text_content),
                has_tables=result.has_tables,
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "PDF parsing failed",
                file_path=file_path,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise ValueError(f"Failed to parse PDF: {e}") from e

    def extract_text(self, file_path: str) -> str:
        """Extract text content from PDF using Docling.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
            
        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If text extraction fails
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # Convert PDF using Docling
            result = self.converter.convert(file_path)
            
            # Extract text from conversion result
            # Docling provides structured output with markdown
            text_content = result.document.export_to_markdown()
            
            logger.debug(
                "Text extraction completed",
                file_path=file_path,
                text_length=len(text_content),
            )
            
            return text_content
            
        except Exception as e:
            logger.error(
                "Text extraction failed",
                file_path=file_path,
                error=str(e),
            )
            raise ValueError(f"Failed to extract text: {e}") from e

    def extract_metadata(self, file_path: str) -> dict[str, Any]:
        """Extract metadata from PDF.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary containing metadata (page_count, language, etc.)
            
        Raises:
            FileNotFoundError: If file does not exist
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # Convert PDF to get document structure
            result = self.converter.convert(file_path)
            document = result.document
            
            # Extract metadata from Docling document
            metadata: dict[str, Any] = {
                "page_count": len(document.pages) if hasattr(document, 'pages') else None,
                "language": None,  # Docling may provide this in future versions
                "has_tables": self._detect_tables(document),
                "has_images": self._detect_images(document),
                "sections": self._extract_sections(document),
            }
            
            # Add any additional metadata from Docling
            if hasattr(document, 'metadata'):
                metadata.update(document.metadata)
            
            logger.debug("Metadata extraction completed", file_path=file_path, metadata=metadata)
            
            return metadata
            
        except Exception as e:
            logger.error("Metadata extraction failed", file_path=file_path, error=str(e))
            # Return minimal metadata on error
            return {
                "page_count": None,
                "language": None,
                "has_tables": False,
                "has_images": False,
                "sections": [],
            }

    def supports_format(self, mime_type: str) -> bool:
        """Check if this parser supports PDF format.
        
        Args:
            mime_type: MIME type to check
            
        Returns:
            True if MIME type is application/pdf
        """
        return mime_type == "application/pdf"

    def _detect_tables(self, document: Any) -> bool:
        """Detect if document contains tables.
        
        Args:
            document: Docling document object
            
        Returns:
            True if tables are present
        """
        try:
            # Check if document has table elements
            if hasattr(document, 'tables') and document.tables:
                return len(document.tables) > 0
            return False
        except Exception:
            return False

    def _detect_images(self, document: Any) -> bool:
        """Detect if document contains images.
        
        Args:
            document: Docling document object
            
        Returns:
            True if images are present
        """
        try:
            # Check if document has image elements
            if hasattr(document, 'pictures') and document.pictures:
                return len(document.pictures) > 0
            return False
        except Exception:
            return False

    def _extract_sections(self, document: Any) -> list[str]:
        """Extract section headings from document.
        
        Args:
            document: Docling document object
            
        Returns:
            List of section heading texts
        """
        sections = []
        try:
            # Extract headings from document structure
            # This is a simplified version - Docling provides rich structure
            if hasattr(document, 'texts'):
                for text in document.texts:
                    if hasattr(text, 'label') and 'heading' in str(text.label).lower():
                        sections.append(text.text)
        except Exception as e:
            logger.warning("Section extraction failed", error=str(e))
        
        return sections
