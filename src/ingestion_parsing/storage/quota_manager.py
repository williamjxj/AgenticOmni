"""Storage quota management for multi-tenant document uploads."""

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

import structlog

from src.shared.exceptions import QuotaExceededError
from src.storage_indexing.models import Tenant

logger = structlog.get_logger(__name__)


class QuotaManager:
    """Manages storage quotas for tenants.
    
    Tracks storage usage and enforces quota limits before allowing uploads.
    
    Example:
        >>> quota_manager = QuotaManager(db_session)
        >>> await quota_manager.check_quota(tenant_id=1, file_size=5_000_000)
        True
    """

    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize quota manager.
        
        Args:
            db_session: Async database session
        """
        self.db = db_session

    async def check_quota(self, tenant_id: int, file_size: int) -> bool:
        """Check if tenant has sufficient quota for upload.
        
        Args:
            tenant_id: Tenant ID
            file_size: Size of file to upload in bytes
            
        Returns:
            True if quota is sufficient
            
        Raises:
            QuotaExceededError: If upload would exceed quota
        """
        # Get tenant's current usage and quota
        result = await self.db.execute(
            select(Tenant.storage_used_bytes, Tenant.storage_quota_bytes).where(
                Tenant.tenant_id == tenant_id
            )
        )
        row = result.first()
        
        if not row:
            raise ValueError(f"Tenant {tenant_id} not found")
        
        used_bytes, quota_bytes = row
        
        # Check if upload would exceed quota
        if used_bytes + file_size > quota_bytes:
            used_mb = used_bytes / (1024 * 1024)
            quota_mb = quota_bytes / (1024 * 1024)
            file_mb = file_size / (1024 * 1024)
            
            logger.warning(
                "Storage quota exceeded",
                tenant_id=tenant_id,
                used_mb=f"{used_mb:.2f}",
                quota_mb=f"{quota_mb:.2f}",
                file_mb=f"{file_mb:.2f}",
            )
            
            raise QuotaExceededError(
                f"Storage quota exceeded. Current usage: {used_mb:.2f}MB / {quota_mb:.2f}MB. "
                f"Cannot upload {file_mb:.2f}MB file.",
                used_bytes=used_bytes,
                quota_bytes=quota_bytes,
            )
        
        logger.info(
            "Quota check passed",
            tenant_id=tenant_id,
            used_bytes=used_bytes,
            quota_bytes=quota_bytes,
            file_size=file_size,
        )
        return True

    async def update_usage(self, tenant_id: int, size_delta: int) -> int:
        """Update tenant's storage usage.
        
        Args:
            tenant_id: Tenant ID
            size_delta: Change in storage usage (positive for upload, negative for delete)
            
        Returns:
            New storage usage in bytes
            
        Example:
            >>> # After uploading 5MB file
            >>> new_usage = await quota_manager.update_usage(tenant_id=1, size_delta=5_000_000)
            >>> print(f"New usage: {new_usage / 1024 / 1024:.2f}MB")
        """
        # Update storage usage atomically
        result = await self.db.execute(
            update(Tenant)
            .where(Tenant.tenant_id == tenant_id)
            .values(storage_used_bytes=Tenant.storage_used_bytes + size_delta)
            .returning(Tenant.storage_used_bytes)
        )
        
        new_usage = result.scalar_one()
        await self.db.commit()
        
        logger.info(
            "Storage usage updated",
            tenant_id=tenant_id,
            size_delta=size_delta,
            new_usage=new_usage,
        )
        
        return new_usage

    async def get_usage(self, tenant_id: int) -> tuple[int, int, float]:
        """Get tenant's current storage usage and quota.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Tuple of (used_bytes, quota_bytes, usage_percent)
            
        Example:
            >>> used, quota, percent = await quota_manager.get_usage(tenant_id=1)
            >>> print(f"Usage: {used / 1024 / 1024:.2f}MB / {quota / 1024 / 1024:.2f}MB ({percent:.1f}%)")
        """
        result = await self.db.execute(
            select(Tenant.storage_used_bytes, Tenant.storage_quota_bytes).where(
                Tenant.tenant_id == tenant_id
            )
        )
        row = result.first()
        
        if not row:
            raise ValueError(f"Tenant {tenant_id} not found")
        
        used_bytes, quota_bytes = row
        usage_percent = (used_bytes / quota_bytes * 100) if quota_bytes > 0 else 0
        
        return used_bytes, quota_bytes, usage_percent

    async def set_quota(self, tenant_id: int, new_quota_bytes: int) -> None:
        """Set tenant's storage quota.
        
        Args:
            tenant_id: Tenant ID
            new_quota_bytes: New quota in bytes
            
        Raises:
            ValueError: If new quota is less than current usage
        """
        # Check current usage
        used_bytes, _, _ = await self.get_usage(tenant_id)
        
        if new_quota_bytes < used_bytes:
            raise ValueError(
                f"Cannot set quota ({new_quota_bytes} bytes) below current usage ({used_bytes} bytes)"
            )
        
        # Update quota
        await self.db.execute(
            update(Tenant)
            .where(Tenant.tenant_id == tenant_id)
            .values(storage_quota_bytes=new_quota_bytes)
        )
        await self.db.commit()
        
        logger.info("Storage quota updated", tenant_id=tenant_id, new_quota_bytes=new_quota_bytes)
