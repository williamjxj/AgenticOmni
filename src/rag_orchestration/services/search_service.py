"""Search service for semantic retrieval.

Feature: 004-ocr-embedding-pipeline
Task: T028
"""

import time
from typing import Any

from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.rag_orchestration.services.embedding_service import EmbeddingService
from src.rag_orchestration.services.search_schemas import (
    SemanticSearchRequest,
    SemanticSearchResponse,
    SearchResultItem,
)
from src.storage_indexing.models import Document, DocumentChunk
from src.storage_indexing.repositories.search_query_repository import SearchQueryRepository
from src.storage_indexing.repositories.search_result_repository import SearchResultRepository

logger = structlog.get_logger(__name__)


class SearchService:
    """Service for semantic document search.

    Uses vector embeddings and pgvector for similarity retrieval.
    Logs search activity for analytics.

    Attributes:
        session: Database session
        embedding_service: Service for text-to-vector
        query_repo: Repository for search query logging
        result_repo: Repository for search result logging
    """

    def __init__(
        self,
        session: AsyncSession,
        embedding_service: EmbeddingService,
        query_repo: SearchQueryRepository,
        result_repo: SearchResultRepository,
    ) -> None:
        """Initialize search service."""
        self.session = session
        self.embedding_service = embedding_service
        self.query_repo = query_repo
        self.result_repo = result_repo

    async def semantic_search(self, request: SemanticSearchRequest) -> SemanticSearchResponse:
        """Perform semantic search across documents.

        Args:
            request: Search parameters (query, tenant, limit)

        Returns:
            Search results with similarity scores
        """
        start_time = time.perf_counter()

        # 1. Generate query embedding
        query_vector = await self.embedding_service.get_embedding(request.query_text)

        # 2. Perform similarity search using pgvector
        # We join with labels/docs to get document titles if needed
        # Cosine distance: 1 - cosine similarity. pgvector <=> operator is cosine distance.
        # Cosine similarity = 1 - (embedding_vector <=> query_vector)
        
        # We need to use the <=> operator for cosine distance and convert to similarity score
        similarity_score = (1 - DocumentChunk.embedding_vector.cosine_distance(query_vector)).label("similarity_score")
        
        stmt = (
            select(
                DocumentChunk.chunk_id,
                DocumentChunk.document_id,
                DocumentChunk.content_text,
                DocumentChunk.start_page,
                Document.filename.label("document_title"),
                similarity_score
            )
            .join(Document, DocumentChunk.document_id == Document.document_id)
            .where(Document.tenant_id == request.tenant_id)
            .where(DocumentChunk.embedding_vector.isnot(None))
            .order_by(text("similarity_score DESC"))
            .limit(request.top_k)
        )

        result = await self.session.execute(stmt)
        rows = result.all()
        
        duration_ms = int((time.perf_counter() - start_time) * 1000)

        # 3. Log search query
        search_query = await self.query_repo.create(
            tenant_id=request.tenant_id,
            query_text=request.query_text,
            query_type="semantic_search",
            result_count=len(rows),
            search_duration_ms=duration_ms
        )

        # 4. Format results and log search results
        search_results = []
        batch_results_to_log = []
        
        for i, row in enumerate(rows):
            rank = i + 1
            item = SearchResultItem(
                chunk_id=row.chunk_id,
                document_id=row.document_id,
                similarity_score=float(row.similarity_score),
                rank_position=rank,
                text_snippet=row.content_text[:500] + "..." if len(row.content_text) > 500 else row.content_text,
                document_title=row.document_title,
                page_number=row.start_page
            )
            search_results.append(item)
            
            batch_results_to_log.append({
                "query_id": search_query.query_id,
                "chunk_id": row.chunk_id,
                "document_id": row.document_id,
                "similarity_score": float(row.similarity_score),
                "rank_position": rank,
                "result_snippet": item.text_snippet
            })

        if batch_results_to_log:
            await self.result_repo.create_batch(batch_results_to_log)
        
        # Final commit for logging
        await self.session.commit()

        return SemanticSearchResponse(
            query_id=search_query.query_id,
            query_text=request.query_text,
            results=search_results,
            total_results=len(search_results),
            search_duration_ms=duration_ms,
            created_at=search_query.created_at
        )
