"""Pydantic models for document parsing results."""

from typing import Any

from pydantic import BaseModel, Field


class ParsingResult(BaseModel):
    """Result of document parsing operation.
    
    Contains extracted text, metadata, and structural information.
    """

    document_id: int = Field(..., description="Document ID that was parsed")
    text_content: str = Field(..., description="Extracted text content")
    page_count: int | None = Field(None, description="Number of pages")
    language: str | None = Field(None, description="Detected language code (ISO 639-1)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    
    # Structural information
    has_tables: bool = Field(default=False, description="Whether document contains tables")
    has_images: bool = Field(default=False, description="Whether document contains images")
    sections: list[str] = Field(default_factory=list, description="Section headings")
    
    class Config:
        """Pydantic configuration."""
        
        json_schema_extra = {
            "example": {
                "document_id": 123,
                "text_content": "This is the extracted text from the document...",
                "page_count": 5,
                "language": "en",
                "metadata": {
                    "author": "John Doe",
                    "created_date": "2024-01-09",
                    "title": "Annual Report 2024",
                },
                "has_tables": True,
                "has_images": False,
                "sections": ["Introduction", "Results", "Conclusion"],
            }
        }


class ChunkData(BaseModel):
    """Data for a document chunk."""

    chunk_index: int = Field(..., description="Sequential index of chunk")
    content: str = Field(..., description="Chunk text content")
    chunk_type: str | None = Field(None, description="Type of chunk (paragraph, heading, table, etc.)")
    start_page: int | None = Field(None, description="Starting page number")
    end_page: int | None = Field(None, description="Ending page number")
    token_count: int | None = Field(None, description="Number of tokens")
    parent_heading: str | None = Field(None, description="Parent section heading")
    
    class Config:
        """Pydantic configuration."""
        
        json_schema_extra = {
            "example": {
                "chunk_index": 0,
                "content": "This is the first chunk of text...",
                "chunk_type": "paragraph",
                "start_page": 1,
                "end_page": 1,
                "token_count": 50,
                "parent_heading": "Introduction",
            }
        }


class ChunkingResult(BaseModel):
    """Result of document chunking operation."""

    document_id: int = Field(..., description="Document ID that was chunked")
    chunks: list[ChunkData] = Field(..., description="List of document chunks")
    total_chunks: int = Field(..., description="Total number of chunks created")
    total_tokens: int = Field(..., description="Total tokens across all chunks")
    
    class Config:
        """Pydantic configuration."""
        
        json_schema_extra = {
            "example": {
                "document_id": 123,
                "chunks": [
                    {
                        "chunk_index": 0,
                        "content": "First chunk...",
                        "token_count": 50,
                    },
                    {
                        "chunk_index": 1,
                        "content": "Second chunk...",
                        "token_count": 48,
                    },
                ],
                "total_chunks": 2,
                "total_tokens": 98,
            }
        }
