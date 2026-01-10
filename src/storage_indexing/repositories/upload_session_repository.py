"""Repository for upload session database operations.

Handles CRUD operations for resumable upload sessions.
"""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.storage_indexing.models.upload_session import UploadSession

logger = structlog.get_logger(__name__)


class UploadSessionRepository:
    """Repository for managing upload sessions."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository.
        
        Args:
            db: Database session
        """
        self.db = db

    async def create(
        self,
        filename: str,
        total_size_bytes: int,
        tenant_id: int,
        user_id: int,
        chunk_size_bytes: int = 5_000_000,
        mime_type: str = "application/octet-stream",
        storage_path: str = "",
        expires_in_hours: int = 24,
    ) -> UploadSession:
        """Create a new upload session.
        
        Args:
            filename: Original filename
            total_size_bytes: Total file size in bytes
            tenant_id: Tenant ID
            user_id: User ID
            chunk_size_bytes: Chunk size in bytes
            mime_type: MIME type
            storage_path: Temporary storage path
            expires_in_hours: Hours until session expires
            
        Returns:
            Created upload session
            
        Example:
            >>> session = await repo.create(
            ...     filename="large.pdf",
            ...     total_size_bytes=50_000_000,
            ...     tenant_id=1,
            ...     user_id=1,
            ... )
            >>> print(session.session_id)
        """
        from uuid import uuid4 as uuid_gen
        
        session_uuid = uuid_gen()
        expires_at = datetime.now(UTC) + timedelta(hours=expires_in_hours)
        
        # Use upload directory for storage path if not provided
        if not storage_path:
            storage_path = f"/tmp/uploads/{session_uuid}"
        
        upload_session = UploadSession(
            session_id=session_uuid,
            tenant_id=tenant_id,
            user_id=user_id,
            filename=filename,
            mime_type=mime_type,
            total_size_bytes=total_size_bytes,
            uploaded_size_bytes=0,
            chunk_size_bytes=chunk_size_bytes,
            storage_path=storage_path,
            status="pending",
            expires_at=expires_at,
        )
        
        self.db.add(upload_session)
        await self.db.commit()
        await self.db.refresh(upload_session)
        
        logger.info(
            "Created upload session",
            session_id=session_id,
            filename=filename,
            file_size=total_size_bytes,
            tenant_id=tenant_id,
            expires_at=expires_at.isoformat(),
        )
        
        return upload_session

    async def get_by_id(self, session_id: str) -> UploadSession | None:
        """Get upload session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Upload session or None if not found
        """
        result = await self.db.execute(
            select(UploadSession).where(UploadSession.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def update_progress(
        self,
        session_id: str,
        uploaded_bytes: int,
        status: str | None = None,
    ) -> UploadSession | None:
        """Update upload progress.
        
        Args:
            session_id: Session identifier
            uploaded_bytes: Total bytes uploaded so far
            status: New status (optional)
            
        Returns:
            Updated session or None if not found
        """
        values: dict[str, Any] = {"uploaded_size_bytes": uploaded_bytes}
        
        if status:
            values["status"] = status
        
        await self.db.execute(
            update(UploadSession)
            .where(UploadSession.session_id == session_id)
            .values(**values)
        )
        await self.db.commit()
        
        # Fetch updated session
        return await self.get_by_id(session_id)

    async def mark_complete(
        self,
        session_id: str,
        document_id: int,
    ) -> UploadSession | None:
        """Mark upload session as complete.
        
        Args:
            session_id: Session identifier
            document_id: Created document ID
            
        Returns:
            Updated session or None if not found
        """
        await self.db.execute(
            update(UploadSession)
            .where(UploadSession.session_id == session_id)
            .values(status="complete")
        )
        await self.db.commit()
        
        logger.info(
            "Upload session completed",
            session_id=session_id,
            document_id=document_id,
        )
        
        return await self.get_by_id(session_id)

    async def mark_cancelled(self, session_id: str) -> UploadSession | None:
        """Mark upload session as cancelled.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Updated session or None if not found
        """
        await self.db.execute(
            update(UploadSession)
            .where(UploadSession.session_id == session_id)
            .values(status="cancelled")
        )
        await self.db.commit()
        
        logger.info("Upload session cancelled", session_id=session_id)
        
        return await self.get_by_id(session_id)

    async def get_expired_sessions(self) -> list[UploadSession]:
        """Get all expired upload sessions.
        
        Returns:
            List of expired sessions
        """
        now = datetime.now(UTC)
        result = await self.db.execute(
            select(UploadSession).where(
                UploadSession.expires_at < now,
                UploadSession.status.in_(["pending", "uploading"]),
            )
        )
        return list(result.scalars().all())

    async def mark_expired(self, session_id: str) -> UploadSession | None:
        """Mark upload session as expired.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Updated session or None if not found
        """
        await self.db.execute(
            update(UploadSession)
            .where(UploadSession.session_id == session_id)
            .values(status="expired")
        )
        await self.db.commit()
        
        logger.info("Upload session expired", session_id=session_id)
        
        return await self.get_by_id(session_id)
