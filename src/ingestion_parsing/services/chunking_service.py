"""Document chunking service for RAG-optimized text splitting."""

import re
from typing import Any

import structlog
import tiktoken

from src.ingestion_parsing.models.parsing_result import ChunkData
from src.shared.config import settings

logger = structlog.get_logger(__name__)


class ChunkingService:
    """Service for chunking documents into RAG-optimized segments.
    
    Uses a hybrid approach:
    1. Semantic boundaries (headings, paragraphs, lists)
    2. Fixed token size limits (512 tokens default)
    3. Overlapping chunks for context preservation (50 tokens)
    
    Example:
        >>> service = ChunkingService()
        >>> chunks = service.chunk_document("Long document text here...")
        >>> print(f"Created {len(chunks)} chunks")
    """

    def __init__(
        self,
        chunk_size_tokens: int | None = None,
        chunk_overlap_tokens: int | None = None,
        min_chunk_size_tokens: int | None = None,
    ) -> None:
        """Initialize chunking service.
        
        Args:
            chunk_size_tokens: Target chunk size in tokens (default from settings)
            chunk_overlap_tokens: Overlap between chunks (default from settings)
            min_chunk_size_tokens: Minimum chunk size (default from settings)
        """
        self.chunk_size_tokens = chunk_size_tokens or settings.chunk_size_tokens
        self.chunk_overlap_tokens = chunk_overlap_tokens or settings.chunk_overlap_tokens
        self.min_chunk_size_tokens = min_chunk_size_tokens or settings.min_chunk_size_tokens
        
        # Initialize tiktoken encoder for token counting
        self.encoder = tiktoken.get_encoding("cl100k_base")  # GPT-3.5/4 encoding
        
        logger.info(
            "ChunkingService initialized",
            chunk_size=self.chunk_size_tokens,
            overlap=self.chunk_overlap_tokens,
            min_size=self.min_chunk_size_tokens,
        )

    def chunk_document(self, text: str, document_id: int | None = None) -> list[ChunkData]:
        """Chunk document text into RAG-optimized segments.
        
        Main entry point for document chunking. Uses hybrid approach:
        1. Split by semantic boundaries
        2. Enforce token limits
        3. Add overlap between chunks
        
        Args:
            text: Full document text to chunk
            document_id: Optional document ID for logging
            
        Returns:
            List of ChunkData objects with content and metadata
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for chunking", document_id=document_id)
            return []
        
        logger.info(
            "Starting document chunking",
            document_id=document_id,
            text_length=len(text),
        )
        
        # Step 1: Split by semantic boundaries
        semantic_chunks = self.split_by_semantic_boundaries(text)
        
        # Step 2: Enforce token limits (may split further)
        sized_chunks = self.enforce_token_limits(semantic_chunks)
        
        # Step 3: Add overlap between chunks
        final_chunks = self.add_overlap(sized_chunks)
        
        # Step 4: Create ChunkData objects
        chunk_data_list = []
        for i, chunk_text in enumerate(final_chunks):
            token_count = self.count_tokens(chunk_text)
            
            chunk_data = ChunkData(
                chunk_index=i,
                content=chunk_text,
                chunk_type="paragraph",  # Could be enhanced with type detection
                token_count=token_count,
            )
            chunk_data_list.append(chunk_data)
        
        logger.info(
            "Document chunking completed",
            document_id=document_id,
            chunk_count=len(chunk_data_list),
            total_tokens=sum(c.token_count or 0 for c in chunk_data_list),
        )
        
        return chunk_data_list

    def split_by_semantic_boundaries(self, text: str) -> list[str]:
        """Split text by semantic boundaries (paragraphs, headings, lists).
        
        Detects:
        - Headings (lines starting with #)
        - Paragraph breaks (double newlines)
        - List items
        - Table structures
        
        Args:
            text: Text to split
            
        Returns:
            List of text segments at semantic boundaries
        """
        # Split by double newlines (paragraph boundaries)
        paragraphs = re.split(r'\n\s*\n', text)
        
        # Filter out empty paragraphs
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        logger.debug("Semantic boundary splitting", segment_count=len(paragraphs))
        
        return paragraphs

    def enforce_token_limits(self, chunks: list[str]) -> list[str]:
        """Enforce token size limits on chunks.
        
        Splits chunks that exceed max size and merges chunks that are too small.
        
        Args:
            chunks: List of text chunks to process
            
        Returns:
            List of chunks within token limits
        """
        result = []
        
        for chunk in chunks:
            token_count = self.count_tokens(chunk)
            
            if token_count > self.chunk_size_tokens:
                # Split large chunk
                sub_chunks = self._split_large_chunk(chunk)
                result.extend(sub_chunks)
            elif token_count < self.min_chunk_size_tokens and result:
                # Merge with previous chunk if too small
                last_chunk = result[-1]
                combined = f"{last_chunk}\n\n{chunk}"
                combined_tokens = self.count_tokens(combined)
                
                if combined_tokens <= self.chunk_size_tokens:
                    result[-1] = combined
                else:
                    result.append(chunk)
            else:
                result.append(chunk)
        
        logger.debug(
            "Token limits enforced",
            input_count=len(chunks),
            output_count=len(result),
        )
        
        return result

    def add_overlap(self, chunks: list[str]) -> list[str]:
        """Add overlap between consecutive chunks for context preservation.
        
        Takes the last N tokens from chunk i and prepends to chunk i+1.
        
        Args:
            chunks: List of chunks to process
            
        Returns:
            List of chunks with overlap added
        """
        if len(chunks) <= 1:
            return chunks
        
        result = [chunks[0]]  # First chunk has no prefix
        
        for i in range(1, len(chunks)):
            # Get last N tokens from previous chunk
            previous_chunk = chunks[i-1]
            overlap_text = self._get_last_n_tokens(previous_chunk, self.chunk_overlap_tokens)
            
            # Prepend to current chunk
            current_chunk = chunks[i]
            overlapped_chunk = f"{overlap_text}\n\n{current_chunk}"
            
            result.append(overlapped_chunk)
        
        logger.debug("Overlap added", chunk_count=len(result))
        
        return result

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        try:
            tokens = self.encoder.encode(text)
            return len(tokens)
        except Exception as e:
            logger.warning("Token counting failed, using word count estimate", error=str(e))
            # Fallback: rough estimate (1 token ≈ 0.75 words)
            return int(len(text.split()) * 1.33)

    def _split_large_chunk(self, text: str) -> list[str]:
        """Split a large chunk into smaller chunks.
        
        Args:
            text: Large chunk to split
            
        Returns:
            List of smaller chunks
        """
        # Split by sentences
        sentences = re.split(r'([.!?]+\s+)', text)
        
        # Rejoin sentence with its punctuation
        clean_sentences = []
        for i in range(0, len(sentences), 2):
            if i + 1 < len(sentences):
                clean_sentences.append(sentences[i] + sentences[i+1])
            else:
                clean_sentences.append(sentences[i])
        
        # Group sentences into chunks of appropriate size
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for sentence in clean_sentences:
            sentence_tokens = self.count_tokens(sentence)
            
            if current_tokens + sentence_tokens > self.chunk_size_tokens and current_chunk:
                # Start new chunk
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_tokens = sentence_tokens
            else:
                current_chunk.append(sentence)
                current_tokens += sentence_tokens
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks

    def _get_last_n_tokens(self, text: str, n_tokens: int) -> str:
        """Get the last N tokens from text.
        
        Args:
            text: Text to extract from
            n_tokens: Number of tokens to extract
            
        Returns:
            Last N tokens as text
        """
        try:
            tokens = self.encoder.encode(text)
            
            if len(tokens) <= n_tokens:
                return text
            
            overlap_tokens = tokens[-n_tokens:]
            overlap_text = self.encoder.decode(overlap_tokens)
            
            return overlap_text
        except Exception as e:
            logger.warning("Token extraction failed", error=str(e))
            # Fallback: use last ~N words
            words = text.split()
            n_words = int(n_tokens * 0.75)  # Rough conversion
            return " ".join(words[-n_words:])
