"""Repository layer for data access.

The repository pattern provides an abstraction layer between the data access
logic and the business logic of the application. This enables:
- Testability: Easy to mock repositories in unit tests
- Flexibility: Can switch database implementations without changing business logic
- Separation of concerns: Business logic doesn't know about database specifics

Feature: 004-ocr-embedding-pipeline
Task: T025
"""

from src.storage_indexing.repositories.extracted_text_repository import (
    ExtractedTextRepository,
)
from src.storage_indexing.repositories.search_query_repository import (
    SearchQueryRepository,
)
from src.storage_indexing.repositories.search_result_repository import (
    SearchResultRepository,
)

__all__ = [
    "ExtractedTextRepository",
    "SearchQueryRepository",
    "SearchResultRepository",
]
