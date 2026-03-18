"""HuggingFace dataset loader service for importing external datasets.

This module provides functionality to load datasets from HuggingFace Hub
and convert them into documents for ingestion into the RAG pipeline.
"""

import hashlib
from typing import Any

import structlog
from datasets import load_dataset

from src.shared.config import settings

logger = structlog.get_logger(__name__)


class HFDatasetLoader:
    """Service for loading and processing HuggingFace datasets.
    
    Converts HuggingFace datasets into a format compatible with the
    existing document ingestion pipeline.
    
    Example:
        >>> loader = HFDatasetLoader()
        >>> records = loader.load_squad_dataset(limit=100)
        >>> print(f"Loaded {len(records)} records")
    """

    def __init__(self) -> None:
        """Initialize HuggingFace dataset loader."""
        self.token = settings.huggingface_token
        logger.info(
            "HFDatasetLoader initialized",
            has_token=bool(self.token),
        )

    def load_squad_dataset(
        self,
        split: str = "train",
        limit: int | None = None,
        streaming: bool = False,
    ) -> list[dict[str, Any]]:
        """Load SQuAD dataset from HuggingFace.
        
        SQuAD (Stanford Question Answering Dataset) contains contexts,
        questions, and answers. We extract the context passages as
        documents for indexing.
        
        Args:
            split: Dataset split to load (train, validation)
            limit: Maximum number of records to load (None = all)
            streaming: Use streaming mode for large datasets
            
        Returns:
            List of document records with text, metadata, and source info
            
        Example:
            >>> loader = HFDatasetLoader()
            >>> records = loader.load_squad_dataset(split="train", limit=500)
        """
        logger.info(
            "Loading SQuAD dataset",
            split=split,
            limit=limit,
            streaming=streaming,
        )
        
        try:
            # Load SQuAD dataset
            dataset = load_dataset(
                "rajpurkar/squad",
                split=split,
                streaming=streaming,
                token=self.token,
            )
            
            # Process records
            records = []
            seen_contexts = set()  # Deduplicate contexts
            
            for idx, row in enumerate(dataset):
                # Apply limit if specified
                if limit and idx >= limit:
                    break
                
                # Extract context (the document text)
                # HuggingFace dataset rows support dictionary access
                try:
                    context = row["context"].strip() if "context" in row else ""
                except (KeyError, AttributeError):
                    continue
                    
                if not context or context in seen_contexts:
                    continue
                
                seen_contexts.add(context)
                
                # Create content hash for deduplication
                content_hash = hashlib.sha256(context.encode()).hexdigest()
                
                # Extract metadata
                try:
                    title = row["title"] if "title" in row else "Unknown"
                    question = row["question"] if "question" in row else ""
                except (KeyError, AttributeError):
                    title = "Unknown"
                    question = ""
                
                # Create document record
                record = {
                    "text": context,
                    "content_hash": content_hash,
                    "source": "huggingface:rajpurkar/squad",
                    "split": split,
                    "original_index": idx,
                    "metadata": {
                        "title": title,
                        "dataset": "squad",
                        "split": split,
                        "has_questions": bool(question),
                        "source_url": "https://huggingface.co/datasets/rajpurkar/squad",
                    },
                }
                
                records.append(record)
            
            logger.info(
                "SQuAD dataset loaded successfully",
                split=split,
                total_records=len(records),
                unique_contexts=len(seen_contexts),
            )
            
            return records
            
        except Exception as e:
            logger.error(
                "Failed to load SQuAD dataset",
                split=split,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise

    def load_generic_dataset(
        self,
        dataset_name: str,
        split: str = "train",
        text_column: str = "text",
        limit: int | None = None,
        streaming: bool = False,
    ) -> list[dict[str, Any]]:
        """Load a generic HuggingFace dataset.
        
        Flexible loader for any HuggingFace dataset with a text column.
        
        Args:
            dataset_name: HuggingFace dataset identifier (e.g., "wikitext")
            split: Dataset split to load
            text_column: Name of the column containing text content
            limit: Maximum number of records to load
            streaming: Use streaming mode for large datasets
            
        Returns:
            List of document records
            
        Example:
            >>> loader = HFDatasetLoader()
            >>> records = loader.load_generic_dataset(
            ...     "wikitext",
            ...     text_column="text",
            ...     limit=1000
            ... )
        """
        logger.info(
            "Loading generic HuggingFace dataset",
            dataset_name=dataset_name,
            split=split,
            text_column=text_column,
            limit=limit,
        )
        
        try:
            # Load dataset
            dataset = load_dataset(
                dataset_name,
                split=split,
                streaming=streaming,
                token=self.token,
            )
            
            # Process records
            records = []
            
            for idx, row in enumerate(dataset):
                # Apply limit if specified
                if limit and idx >= limit:
                    break
                
                # Extract text content
                try:
                    text = row[text_column].strip() if text_column in row else ""
                except (KeyError, AttributeError, TypeError):
                    continue
                    
                if not text:
                    continue
                
                # Create content hash for deduplication
                content_hash = hashlib.sha256(text.encode()).hexdigest()
                
                # Create document record
                record = {
                    "text": text,
                    "content_hash": content_hash,
                    "source": f"huggingface:{dataset_name}",
                    "split": split,
                    "original_index": idx,
                    "metadata": {
                        "dataset": dataset_name,
                        "split": split,
                        "text_column": text_column,
                    },
                }
                
                records.append(record)
            
            logger.info(
                "Generic dataset loaded successfully",
                dataset_name=dataset_name,
                split=split,
                total_records=len(records),
            )
            
            return records
            
        except Exception as e:
            logger.error(
                "Failed to load generic dataset",
                dataset_name=dataset_name,
                split=split,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise

    def validate_dataset_access(self, dataset_name: str) -> bool:
        """Validate access to a HuggingFace dataset.
        
        Checks if the dataset exists and is accessible with current token.
        
        Args:
            dataset_name: HuggingFace dataset identifier
            
        Returns:
            True if dataset is accessible, False otherwise
        """
        try:
            # Try to load just the first row
            dataset = load_dataset(
                dataset_name,
                split="train",
                streaming=True,
                token=self.token,
            )
            next(iter(dataset))
            return True
        except Exception as e:
            logger.warning(
                "Dataset validation failed",
                dataset_name=dataset_name,
                error=str(e),
            )
            return False
