#!/usr/bin/env python3
"""Generate embeddings for all document chunks.

This script processes all chunks that don't have embeddings yet
and generates vector embeddings using the configured embedding provider.

Usage:
    python scripts/generate_embeddings.py [--batch-size 32] [--tenant-id 1]
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.config import settings
from src.rag_orchestration.services.embedding_service import EmbeddingService
from src.storage_indexing.database import get_db, init_db
from src.storage_indexing.models.document_chunk import DocumentChunk

logger = structlog.get_logger(__name__)


async def generate_embeddings_for_chunks(
    batch_size: int = 32,
    tenant_id: int | None = None,
) -> dict[str, Any]:
    """Generate embeddings for chunks without embeddings.

    Args:
        batch_size: Number of chunks to process in each batch
        tenant_id: Optional tenant ID filter

    Returns:
        Statistics about the embedding generation process
    """
    init_db()
    embedding_service = EmbeddingService(settings)

    total_processed = 0
    total_failed = 0
    total_skipped = 0

    logger.info(
        "Starting embedding generation",
        batch_size=batch_size,
        tenant_id=tenant_id,
        provider=settings.embedding_provider,
        model=settings.embedding_model,
    )

    async for db in get_db():
        # Query chunks without embeddings
        query = select(DocumentChunk).where(DocumentChunk.embedding_vector.is_(None))

        if tenant_id is not None:
            # Join with documents to filter by tenant
            from src.storage_indexing.models.document import Document

            query = (
                query.join(Document, DocumentChunk.document_id == Document.document_id)
                .where(Document.tenant_id == tenant_id)
            )

        result = await db.execute(query.limit(1000))  # Process max 1000 at a time
        chunks = result.scalars().all()

        if not chunks:
            logger.info("No chunks found without embeddings")
            return {
                "processed": total_processed,
                "failed": total_failed,
                "skipped": total_skipped,
            }

        logger.info(f"Found {len(chunks)} chunks to process")

        # Process in batches
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]

            for chunk in batch:
                try:
                    # Skip empty chunks
                    if not chunk.content_text or not chunk.content_text.strip():
                        logger.warning(
                            "Skipping empty chunk",
                            chunk_id=chunk.chunk_id,
                            document_id=chunk.document_id,
                        )
                        total_skipped += 1
                        continue

                    logger.info(
                        "Generating embedding",
                        chunk_id=chunk.chunk_id,
                        document_id=chunk.document_id,
                        content_length=len(chunk.content_text),
                    )

                    # Generate embedding
                    embedding = await embedding_service.get_embedding(chunk.content_text)

                    # Update chunk with embedding
                    chunk.embedding_vector = embedding

                    total_processed += 1

                    logger.info(
                        "Embedding generated successfully",
                        chunk_id=chunk.chunk_id,
                        document_id=chunk.document_id,
                        embedding_dim=len(embedding),
                    )

                except Exception as e:
                    logger.error(
                        "Failed to generate embedding",
                        chunk_id=chunk.chunk_id,
                        document_id=chunk.document_id,
                        error=str(e),
                        error_type=type(e).__name__,
                    )
                    total_failed += 1
                    continue

            # Commit after each batch
            try:
                await db.commit()
                logger.info(
                    "Batch committed",
                    batch_start=i,
                    batch_end=min(i + batch_size, len(chunks)),
                    processed=total_processed,
                    failed=total_failed,
                )
            except Exception as e:
                logger.error(
                    "Failed to commit batch",
                    batch_start=i,
                    error=str(e),
                )
                await db.rollback()
                raise

    stats = {
        "processed": total_processed,
        "failed": total_failed,
        "skipped": total_skipped,
    }

    logger.info(
        "Embedding generation complete",
        total_processed=total_processed,
        total_failed=total_failed,
        total_skipped=total_skipped,
    )

    return stats


async def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate embeddings for document chunks"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Number of chunks to process in each batch (default: 32)",
    )
    parser.add_argument(
        "--tenant-id",
        type=int,
        default=None,
        help="Filter by tenant ID (optional)",
    )

    args = parser.parse_args()

    # Verify embedding provider is configured
    if not settings.embedding_provider:
        logger.error("EMBEDDING_PROVIDER not configured in .env")
        return

    if settings.embedding_provider == "ollama":
        if not settings.ollama_base_url:
            logger.error("OLLAMA_BASE_URL not configured in .env")
            return
        logger.info(
            "Using Ollama for embeddings",
            base_url=settings.ollama_base_url,
            model=settings.embedding_model,
        )
    elif settings.embedding_provider == "openai":
        if not settings.openai_api_key:
            logger.error("OPENAI_API_KEY not configured in .env")
            return
        logger.info("Using OpenAI for embeddings", model=settings.embedding_model)

    # Generate embeddings
    stats = await generate_embeddings_for_chunks(
        batch_size=args.batch_size,
        tenant_id=args.tenant_id,
    )

    # Print summary
    print("\n" + "=" * 70)
    print("EMBEDDING GENERATION SUMMARY")
    print("=" * 70)
    print(f"✅ Successfully processed: {stats['processed']}")
    print(f"❌ Failed: {stats['failed']}")
    print(f"⏭️  Skipped (empty): {stats['skipped']}")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Verify embeddings: ./scripts/check_db_status.sh")
    print("  2. Test search: http://localhost:3000/search")
    print("  3. Or via API: POST /api/v1/search/semantic")
    print()


if __name__ == "__main__":
    asyncio.run(main())
