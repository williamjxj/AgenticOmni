"""Base parser abstract class for document parsing."""

from abc import ABC, abstractmethod

from src.ingestion_parsing.models.parsing_result import ParsingResult


class BaseParser(ABC):
    """Abstract base class for document parsers.
    
    All document parsers (PDF, DOCX, TXT, etc.) must implement this interface
    to ensure consistent parsing behavior across different file types.
    
    Example:
        >>> class MyParser(BaseParser):
        ...     def parse(self, file_path: str) -> ParsingResult:
        ...         # Implementation here
        ...         pass
    """

    @abstractmethod
    def parse(self, file_path: str) -> ParsingResult:
        """Parse a document and extract content.
        
        This is the main entry point for document parsing. It should:
        1. Validate the file exists and is readable
        2. Extract text content
        3. Extract metadata (page count, language, etc.)
        4. Detect structural elements (headings, tables, images)
        5. Return a ParsingResult with all extracted information
        
        Args:
            file_path: Path to the document file
            
        Returns:
            ParsingResult: Structured parsing result with text and metadata
            
        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file format is invalid or cannot be parsed
        """
        pass

    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """Extract raw text content from document.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted text content as a string
            
        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If text extraction fails
        """
        pass

    @abstractmethod
    def extract_metadata(self, file_path: str) -> dict:
        """Extract document metadata.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing metadata (page_count, author, title, etc.)
            
        Raises:
            FileNotFoundError: If file does not exist
        """
        pass

    def supports_format(self, mime_type: str) -> bool:
        """Check if this parser supports the given MIME type.
        
        Args:
            mime_type: MIME type to check
            
        Returns:
            True if this parser can handle the format
        """
        return False
