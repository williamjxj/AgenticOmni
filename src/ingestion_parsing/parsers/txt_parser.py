"""TXT parser for plain text files."""

from pathlib import Path
from typing import Any

import structlog

from src.ingestion_parsing.models.parsing_result import ParsingResult
from src.ingestion_parsing.parsers.base import BaseParser

logger = structlog.get_logger(__name__)


class TXTParser(BaseParser):
    """Plain text file parser.
    
    Handles:
    - UTF-8 encoding
    - Line ending normalization (CRLF, LF)
    - Character encoding detection
    
    Example:
        >>> parser = TXTParser()
        >>> result = parser.parse("/path/to/document.txt")
        >>> print(result.text_content)
    """

    def parse(self, file_path: str) -> ParsingResult:
        """Parse plain text file and extract content.
        
        Args:
            file_path: Path to TXT file
            
        Returns:
            ParsingResult with text content
            
        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If text parsing fails
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info("Starting TXT parsing", file_path=file_path)
        
        try:
            # Extract text content
            text_content = self.extract_text(file_path)
            
            # Extract metadata
            metadata = self.extract_metadata(file_path)
            
            # Build parsing result
            result = ParsingResult(
                document_id=0,  # Will be set by calling service
                text_content=text_content,
                page_count=None,  # Plain text has no pages
                language=None,  # Could be detected with langdetect
                metadata=metadata,
                has_tables=False,
                has_images=False,
                sections=[],
            )
            
            logger.info(
                "TXT parsing completed",
                file_path=file_path,
                text_length=len(text_content),
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "TXT parsing failed",
                file_path=file_path,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise ValueError(f"Failed to parse TXT: {e}") from e

    def extract_text(self, file_path: str) -> str:
        """Extract text content from plain text file.
        
        Tries multiple encodings in order:
        1. UTF-8 (most common)
        2. UTF-8 with BOM
        3. Latin-1 (fallback)
        
        Args:
            file_path: Path to TXT file
            
        Returns:
            Extracted text content with normalized line endings
            
        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If text extraction fails
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    text_content = f.read()
                
                # Normalize line endings (CRLF → LF)
                text_content = text_content.replace('\r\n', '\n').replace('\r', '\n')
                
                logger.debug(
                    "Text extraction completed",
                    file_path=file_path,
                    encoding=encoding,
                    text_length=len(text_content),
                )
                
                return text_content
                
            except UnicodeDecodeError:
                logger.debug(f"Failed to decode with {encoding}, trying next encoding")
                continue
            except Exception as e:
                logger.error(
                    "Text extraction failed",
                    file_path=file_path,
                    encoding=encoding,
                    error=str(e),
                )
                continue
        
        # If all encodings fail
        raise ValueError(f"Failed to extract text with any encoding: {encodings}")

    def extract_metadata(self, file_path: str) -> dict[str, Any]:
        """Extract metadata from plain text file.
        
        Args:
            file_path: Path to TXT file
            
        Returns:
            Dictionary containing basic metadata
            
        Raises:
            FileNotFoundError: If file does not exist
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            file_stat = Path(file_path).stat()
            
            metadata: dict[str, Any] = {
                "file_size": file_stat.st_size,
                "created": None,  # Not reliably available on all systems
                "modified": file_stat.st_mtime,
                "line_count": self._count_lines(file_path),
                "has_tables": False,
                "has_images": False,
                "sections": [],
            }
            
            logger.debug("Metadata extraction completed", file_path=file_path, metadata=metadata)
            
            return metadata
            
        except Exception as e:
            logger.error("Metadata extraction failed", file_path=file_path, error=str(e))
            return {
                "has_tables": False,
                "has_images": False,
                "sections": [],
            }

    def supports_format(self, mime_type: str) -> bool:
        """Check if this parser supports plain text format.
        
        Args:
            mime_type: MIME type to check
            
        Returns:
            True if MIME type is text/plain
        """
        return mime_type in ["text/plain", "text/x-python", "text/x-script", "text/x-log"]

    def _count_lines(self, file_path: str) -> int:
        """Count number of lines in text file.
        
        Args:
            file_path: Path to text file
            
        Returns:
            Number of lines
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f)
        except Exception:
            return 0
