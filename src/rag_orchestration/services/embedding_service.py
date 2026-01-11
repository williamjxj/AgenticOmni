"""Embedding service for generating vector embeddings from text.

Feature: 004-ocr-embedding-pipeline
Task: T027
"""

import time
from typing import Any

from openai import AsyncOpenAI
import httpx
import structlog

from config.settings import Settings
from src.rag_orchestration.services.embedding_exceptions import EmbeddingProviderError

logger = structlog.get_logger(__name__)


class EmbeddingService:
    """Service for generating vector embeddings.

    Handles interfacing with embedding providers (OpenAI, HuggingFace)
    to convert text into vector representations.

    Attributes:
        settings: Application settings
        client: Async OpenAI client
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize embedding service.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.client = None
        if settings.openai_api_key:
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def get_embedding(self, text: str) -> list[float]:
        """Generate embedding for a single text string.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector

        Raises:
            EmbeddingProviderError: If the provider fails
        """
        if not text or not text.strip():
            raise ValueError("Text for embedding cannot be empty")

        if self.settings.embedding_provider == "openai":
            return await self._get_openai_embedding(text)
        elif self.settings.embedding_provider == "ollama":
            return await self._get_ollama_embedding(text)
        elif self.settings.embedding_provider == "huggingface":
            # Placeholder for local embedding implementation
            raise NotImplementedError("HuggingFace local embeddings not yet implemented")
        else:
            raise ValueError(f"Unsupported embedding provider: {self.settings.embedding_provider}")

    async def _get_openai_embedding(self, text: str) -> list[float]:
        """Get embedding from OpenAI API.

        Args:
            text: Text to embed

        Returns:
            Embedding vector

        Raises:
            EmbeddingProviderError: If OpenAI call fails
        """
        if not self.client:
            raise EmbeddingProviderError(
                "OpenAI client not initialized. Check OPENAI_API_KEY.",
                provider="openai"
            )

        try:
            start_time = time.perf_counter()
            response = await self.client.embeddings.create(
                model=self.settings.embedding_model,
                input=text.replace("\n", " ")  # Recommended by OpenAI
            )
            duration_ms = int((time.perf_counter() - start_time) * 1000)

            logger.debug(
                "OpenAI embedding generated",
                model=self.settings.embedding_model,
                duration_ms=duration_ms,
                token_count=response.usage.total_tokens
            )

            return response.data[0].embedding

        except Exception as e:
            logger.error(
                "OpenAI embedding failed",
                error=str(e),
                model=self.settings.embedding_model
            )
            raise EmbeddingProviderError(
                f"Failed to generate OpenAI embedding: {str(e)}",
                provider="openai"
            ) from e

    async def _get_ollama_embedding(self, text: str) -> list[float]:
        """Get embedding from local Ollama API.

        Args:
            text: Text to embed

        Returns:
            Embedding vector

        Raises:
            EmbeddingProviderError: If Ollama call fails
        """
        try:
            start_time = time.perf_counter()
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.settings.ollama_base_url}/api/embeddings",
                    json={
                        "model": self.settings.embedding_model,
                        "prompt": text,
                    },
                )
                response.raise_for_status()
                data = response.json()
            
            duration_ms = int((time.perf_counter() - start_time) * 1000)

            logger.debug(
                "Ollama embedding generated",
                model=self.settings.embedding_model,
                duration_ms=duration_ms
            )

            return data["embedding"]

        except Exception as e:
            logger.error(
                "Ollama embedding failed",
                error=str(e),
                model=self.settings.embedding_model,
                url=self.settings.ollama_base_url
            )
            raise EmbeddingProviderError(
                f"Failed to generate Ollama embedding: {str(e)}",
                provider="ollama"
            ) from e
