"""FolderBatch repository for database operations.

This module provides repository pattern implementation for FolderBatch entities.
"""

from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.storage_indexing.models.folder_batch import FolderBatch


class FolderBatchRepository:
    """Repository for FolderBatch database operations.
    
    Provides CRUD operations and queries for folder batch processing.
    
    Example:
        >>> async with async_session() as session:
        ...     repo = FolderBatchRepository(session)
        ...     batch = await repo.create(
        ...         tenant_id=1,
        ...         user_id=42,
        ...         folder_path="/uploads/batch_123",
        ...         original_folder_name="docs"
        ...     )
        ...     await session.commit()
    """
    
    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.
        
        Args:
            session: SQLAlchemy async session
        """
        self.session = session
    
    async def create(
        self,
        tenant_id: int,
        user_id: int,
        folder_path: str,
        original_folder_name: str,
        status: str = "discovering"
    ) -> FolderBatch:
        """Create a new folder batch record.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            folder_path: Absolute path to uploaded folder
            original_folder_name: Original folder name
            status: Initial status (default: "discovering")
        
        Returns:
            Created FolderBatch instance
        
        Example:
            >>> batch = await repo.create(
            ...     tenant_id=1,
            ...     user_id=42,
            ...     folder_path="/uploads/batch_123",
            ...     original_folder_name="docs"
            ... )
        """
        batch = FolderBatch(
            tenant_id=tenant_id,
            user_id=user_id,
            folder_path=folder_path,
            original_folder_name=original_folder_name,
            status=status
        )
        self.session.add(batch)
        await self.session.flush()  # Get ID without committing
        return batch
    
    async def get_by_id(self, batch_id: int, tenant_id: int) -> FolderBatch | None:
        """Get folder batch by ID with tenant isolation.
        
        Args:
            batch_id: Batch identifier
            tenant_id: Tenant identifier for isolation
        
        Returns:
            FolderBatch if found, None otherwise
        
        Example:
            >>> batch = await repo.get_by_id(batch_id=123, tenant_id=1)
            >>> if batch:
            ...     print(f"Progress: {batch.progress_percentage}%")
        """
        result = await self.session.execute(
            select(FolderBatch)
            .where(FolderBatch.id == batch_id)
            .where(FolderBatch.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()
    
    async def update_status(
        self,
        batch_id: int,
        status: str,
        error_message: str | None = None
    ) -> None:
        """Update folder batch status.
        
        Args:
            batch_id: Batch identifier
            status: New status value
            error_message: Optional error message
        
        Example:
            >>> await repo.update_status(
            ...     batch_id=123,
            ...     status="processing"
            ... )
        """
        await self.session.execute(
            update(FolderBatch)
            .where(FolderBatch.id == batch_id)
            .values(
                status=status,
                error_message=error_message,
                updated_at=datetime.now(timezone.utc)
            )
        )
    
    async def update_discovery(
        self,
        batch_id: int,
        total_files_discovered: int
    ) -> None:
        """Update folder batch after file discovery.
        
        Args:
            batch_id: Batch identifier
            total_files_discovered: Total markdown files found
        
        Example:
            >>> await repo.update_discovery(
            ...     batch_id=123,
            ...     total_files_discovered=47
            ... )
        """
        await self.session.execute(
            update(FolderBatch)
            .where(FolderBatch.id == batch_id)
            .values(
                total_files_discovered=total_files_discovered,
                status="processing",
                updated_at=datetime.now(timezone.utc)
            )
        )
    
    async def increment_files_processed(self, batch_id: int) -> None:
        """Increment files_processed counter.
        
        Args:
            batch_id: Batch identifier
        
        Example:
            >>> await repo.increment_files_processed(batch_id=123)
        """
        await self.session.execute(
            update(FolderBatch)
            .where(FolderBatch.id == batch_id)
            .values(
                files_processed=FolderBatch.files_processed + 1,
                updated_at=datetime.now(timezone.utc)
            )
        )
    
    async def increment_files_failed(self, batch_id: int) -> None:
        """Increment files_failed counter.
        
        Args:
            batch_id: Batch identifier
        
        Example:
            >>> await repo.increment_files_failed(batch_id=123)
        """
        await self.session.execute(
            update(FolderBatch)
            .where(FolderBatch.id == batch_id)
            .values(
                files_failed=FolderBatch.files_failed + 1,
                updated_at=datetime.now(timezone.utc)
            )
        )
    
    async def finalize_batch(self, batch_id: int) -> None:
        """Mark batch as completed and check for failures.
        
        Automatically sets status to 'completed' or 'partial_failure'
        based on files_failed count.
        
        Args:
            batch_id: Batch identifier
        
        Example:
            >>> await repo.finalize_batch(batch_id=123)
        """
        # Get current batch state
        batch = await self.session.get(FolderBatch, batch_id)
        if not batch:
            return
        
        # Determine final status
        if batch.files_failed > 0:
            final_status = "partial_failure"
        else:
            final_status = "completed"
        
        await self.session.execute(
            update(FolderBatch)
            .where(FolderBatch.id == batch_id)
            .values(
                status=final_status,
                completed_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
        )
    
    async def list_by_tenant(
        self,
        tenant_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> Sequence[FolderBatch]:
        """List folder batches for a tenant.
        
        Args:
            tenant_id: Tenant identifier
            limit: Maximum results to return
            offset: Results offset for pagination
        
        Returns:
            List of FolderBatch instances
        
        Example:
            >>> batches = await repo.list_by_tenant(
            ...     tenant_id=1,
            ...     limit=10
            ... )
            >>> for batch in batches:
            ...     print(f"{batch.original_folder_name}: {batch.status}")
        """
        result = await self.session.execute(
            select(FolderBatch)
            .where(FolderBatch.tenant_id == tenant_id)
            .order_by(FolderBatch.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
