"""Parser factory for selecting appropriate parser based on file type."""

import structlog

from src.ingestion_parsing.parsers.base import BaseParser
from src.ingestion_parsing.parsers.docx_parser import DOCXParser
from src.ingestion_parsing.parsers.pdf_parser import PDFParser
from src.ingestion_parsing.parsers.txt_parser import TXTParser

logger = structlog.get_logger(__name__)


class ParserFactory:
    """Factory class for creating document parsers based on MIME type.
    
    Example:
        >>> parser = ParserFactory.get_parser("application/pdf")
        >>> result = parser.parse("/path/to/document.pdf")
    """

    # Registry of parsers by MIME type
    _parsers: dict[str, type[BaseParser]] = {
        "application/pdf": PDFParser,
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": DOCXParser,
        "text/plain": TXTParser,
    }

    @classmethod
    def get_parser(cls, mime_type: str) -> BaseParser:
        """Get appropriate parser for the given MIME type.
        
        Args:
            mime_type: MIME type of the document
            
        Returns:
            Parser instance for the given MIME type
            
        Raises:
            ValueError: If no parser is available for the MIME type
            
        Example:
            >>> parser = ParserFactory.get_parser("application/pdf")
            >>> isinstance(parser, PDFParser)
            True
        """
        parser_class = cls._parsers.get(mime_type)
        
        if parser_class is None:
            supported_types = ", ".join(cls._parsers.keys())
            logger.error(
                "No parser available for MIME type",
                mime_type=mime_type,
                supported_types=supported_types,
            )
            raise ValueError(
                f"No parser available for MIME type '{mime_type}'. "
                f"Supported types: {supported_types}"
            )
        
        logger.info("Creating parser", mime_type=mime_type, parser_class=parser_class.__name__)
        return parser_class()

    @classmethod
    def register_parser(cls, mime_type: str, parser_class: type[BaseParser]) -> None:
        """Register a new parser for a MIME type.
        
        Allows runtime registration of custom parsers.
        
        Args:
            mime_type: MIME type to register
            parser_class: Parser class to use for this MIME type
            
        Example:
            >>> class CustomParser(BaseParser):
            ...     pass
            >>> ParserFactory.register_parser("application/custom", CustomParser)
        """
        cls._parsers[mime_type] = parser_class
        logger.info("Parser registered", mime_type=mime_type, parser_class=parser_class.__name__)

    @classmethod
    def get_supported_types(cls) -> list[str]:
        """Get list of supported MIME types.
        
        Returns:
            List of supported MIME type strings
        """
        return list(cls._parsers.keys())
