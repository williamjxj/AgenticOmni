"""Repository for SearchResult data access.

Feature: 004-ocr-embedding-pipeline
Task: T024
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.storage_indexing.models.search_result import SearchResult


class SearchResultRepository:
    """Repository for SearchResult data access operations.

    Handles database operations for search results, including creating
    and retrieving results for queries.

    Attributes:
        session: Async SQLAlchemy database session
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize SearchResultRepository with database session.

        Args:
            session: Async SQLAlchemy database session
        """
        self.session = session

    async def create(
        self,
        query_id: int,
        chunk_id: int,
        document_id: int,
        similarity_score: float,
        rank_position: int,
        result_snippet: str | None = None,
    ) -> SearchResult:
        """Create a new search result record.

        Args:
            query_id: Foreign key to search_queries table
            chunk_id: Foreign key to document_chunks table
            document_id: Foreign key to documents table
            similarity_score: Cosine similarity score (0.0-1.0)
            rank_position: Result position (1-based)
            result_snippet: Optional text snippet for preview

        Returns:
            Created SearchResult instance

        Raises:
            ValueError: If similarity_score or rank_position are invalid
            SQLAlchemyError: For database errors
        """
        if not (0.0 <= similarity_score <= 1.0):
            raise ValueError(
                f"similarity_score must be between 0.0 and 1.0, got {similarity_score}"
            )

        if rank_position < 1:
            raise ValueError(f"rank_position must be >= 1, got {rank_position}")

        search_result = SearchResult(
            query_id=query_id,
            chunk_id=chunk_id,
            document_id=document_id,
            similarity_score=similarity_score,
            rank_position=rank_position,
            result_snippet=result_snippet,
        )

        self.session.add(search_result)
        await self.session.flush()
        await self.session.refresh(search_result)

        return search_result

    async def create_batch(
        self, results: list[dict]
    ) -> list[SearchResult]:
        """Create multiple search results in batch.

        Args:
            results: List of result dictionaries with required fields

        Returns:
            List of created SearchResult instances

        Example:
            results = [
                {
                    "query_id": 1,
                    "chunk_id": 100,
                    "document_id": 10,
                    "similarity_score": 0.95,
                    "rank_position": 1,
                    "result_snippet": "...",
                },
                ...
            ]
        """
        search_results = []

        for result_data in results:
            search_result = SearchResult(**result_data)
            self.session.add(search_result)
            search_results.append(search_result)

        await self.session.flush()

        # Refresh all instances
        for result in search_results:
            await self.session.refresh(result)

        return search_results

    async def get_by_id(self, result_id: int) -> SearchResult | None:
        """Retrieve search result by ID.

        Args:
            result_id: Unique identifier

        Returns:
            SearchResult instance if found, None otherwise
        """
        stmt = select(SearchResult).where(SearchResult.result_id == result_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_query(self, query_id: int) -> list[SearchResult]:
        """Retrieve all results for a search query.

        Args:
            query_id: Foreign key to search_queries table

        Returns:
            List of SearchResult instances ordered by rank_position
        """
        stmt = (
            select(SearchResult)
            .where(SearchResult.query_id == query_id)
            .order_by(SearchResult.rank_position)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_chunk(self, chunk_id: int) -> list[SearchResult]:
        """Retrieve all search results that matched a specific chunk.

        Args:
            chunk_id: Foreign key to document_chunks table

        Returns:
            List of SearchResult instances
        """
        stmt = select(SearchResult).where(SearchResult.chunk_id == chunk_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_document(self, document_id: int) -> list[SearchResult]:
        """Retrieve all search results that matched a specific document.

        Args:
            document_id: Foreign key to documents table

        Returns:
            List of SearchResult instances
        """
        stmt = select(SearchResult).where(SearchResult.document_id == document_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_by_query(self, query_id: int) -> int:
        """Delete all results for a search query.

        Args:
            query_id: Foreign key to search_queries table

        Returns:
            Number of records deleted
        """
        results = await self.get_by_query(query_id)
        count = len(results)

        for search_result in results:
            await self.session.delete(search_result)

        await self.session.flush()
        return count

    async def count_by_query(self, query_id: int) -> int:
        """Count search results for a query.

        Args:
            query_id: Foreign key to search_queries table

        Returns:
            Number of search results
        """
        results = await self.get_by_query(query_id)
        return len(results)
