"""Repository for SearchQuery data access.

Feature: 004-ocr-embedding-pipeline
Task: T023
"""

from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.storage_indexing.models.search_query import QueryType, SearchQuery


class SearchQueryRepository:
    """Repository for SearchQuery data access operations.

    Handles database operations for search query logging and analytics,
    including creating queries and retrieving search history.

    Attributes:
        session: Async SQLAlchemy database session
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize SearchQueryRepository with database session.

        Args:
            session: Async SQLAlchemy database session
        """
        self.session = session

    async def create(
        self,
        tenant_id: int,
        query_text: str,
        query_type: str,
        user_id: int | None = None,
        source_document_id: int | None = None,
        filters_applied: dict[str, Any] | None = None,
        result_count: int | None = None,
        search_duration_ms: int | None = None,
    ) -> SearchQuery:
        """Create a new search query record.

        Args:
            tenant_id: Foreign key to tenants table
            query_text: Original search query text
            query_type: Type of query (semantic_search, similar_documents)
            user_id: Optional user who performed search
            source_document_id: Optional document for "find similar" queries
            filters_applied: Optional metadata filters (JSONB)
            result_count: Optional number of results returned
            search_duration_ms: Optional query execution time

        Returns:
            Created SearchQuery instance

        Raises:
            ValueError: If query_text is empty or query_type is invalid
            SQLAlchemyError: For database errors
        """
        if not query_text or not query_text.strip():
            raise ValueError("query_text cannot be empty")

        if query_type not in [QueryType.SEMANTIC_SEARCH.value, QueryType.SIMILAR_DOCUMENTS.value]:
            raise ValueError(f"Invalid query_type: {query_type}")

        search_query = SearchQuery(
            tenant_id=tenant_id,
            user_id=user_id,
            query_text=query_text,
            query_type=query_type,
            source_document_id=source_document_id,
            filters_applied=filters_applied,
            result_count=result_count,
            search_duration_ms=search_duration_ms,
        )

        self.session.add(search_query)
        await self.session.flush()
        await self.session.refresh(search_query)

        return search_query

    async def get_by_id(self, query_id: int) -> SearchQuery | None:
        """Retrieve search query by ID.

        Args:
            query_id: Unique identifier

        Returns:
            SearchQuery instance if found, None otherwise
        """
        stmt = select(SearchQuery).where(SearchQuery.query_id == query_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_tenant(
        self, tenant_id: int, limit: int = 100
    ) -> list[SearchQuery]:
        """Retrieve recent search queries for a tenant.

        Args:
            tenant_id: Foreign key to tenants table
            limit: Maximum number of queries to return (default: 100)

        Returns:
            List of SearchQuery instances ordered by created_at DESC
        """
        stmt = (
            select(SearchQuery)
            .where(SearchQuery.tenant_id == tenant_id)
            .order_by(desc(SearchQuery.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user(
        self, user_id: int, limit: int = 50
    ) -> list[SearchQuery]:
        """Retrieve recent search queries for a user.

        Args:
            user_id: Foreign key to users table
            limit: Maximum number of queries to return (default: 50)

        Returns:
            List of SearchQuery instances ordered by created_at DESC
        """
        stmt = (
            select(SearchQuery)
            .where(SearchQuery.user_id == user_id)
            .order_by(desc(SearchQuery.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_type(
        self, tenant_id: int, query_type: str, limit: int = 100
    ) -> list[SearchQuery]:
        """Retrieve search queries by type.

        Args:
            tenant_id: Foreign key to tenants table
            query_type: Type of query (semantic_search, similar_documents)
            limit: Maximum number of queries to return (default: 100)

        Returns:
            List of SearchQuery instances ordered by created_at DESC
        """
        stmt = (
            select(SearchQuery)
            .where(
                SearchQuery.tenant_id == tenant_id,
                SearchQuery.query_type == query_type,
            )
            .order_by(desc(SearchQuery.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_avg_search_duration(self, tenant_id: int) -> float | None:
        """Calculate average search duration for a tenant.

        Args:
            tenant_id: Foreign key to tenants table

        Returns:
            Average search duration in milliseconds, None if no data
        """
        queries = await self.get_by_tenant(tenant_id, limit=1000)

        # Filter out None durations
        durations = [
            q.search_duration_ms for q in queries if q.search_duration_ms is not None
        ]

        if not durations:
            return None

        return sum(durations) / len(durations)

    async def get_total_searches(self, tenant_id: int) -> int:
        """Count total searches for a tenant.

        Args:
            tenant_id: Foreign key to tenants table

        Returns:
            Total number of search queries
        """
        queries = await self.get_by_tenant(tenant_id, limit=999999)
        return len(queries)
