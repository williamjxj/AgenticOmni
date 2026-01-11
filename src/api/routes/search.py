"""Search API router.

Feature: 004-ocr-embedding-pipeline
Task: T029
"""

from fastapi import APIRouter, Depends, status
import structlog

from src.api.dependencies import get_search_service
from src.rag_orchestration.services.search_schemas import (
    SemanticSearchRequest,
    SemanticSearchResponse,
)
from src.rag_orchestration.services.search_service import SearchService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


@router.post(
    "/semantic",
    response_model=SemanticSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Perform semantic search",
    description="Search documents based on semantic meaning using vector embeddings.",
)
async def semantic_search(
    request: SemanticSearchRequest,
    search_service: SearchService = Depends(get_search_service),
) -> SemanticSearchResponse:
    """Execute semantic search query."""
    logger.info(
        "semantic_search_requested",
        query=request.query_text,
        tenant_id=request.tenant_id,
        top_k=request.top_k
    )
    
    return await search_service.semantic_search(request)
