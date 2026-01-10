"""Unit tests for QuotaManager."""

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from src.ingestion_parsing.storage.quota_manager import QuotaManager
from src.shared.exceptions import QuotaExceededError
from src.storage_indexing.models import Tenant


@pytest.mark.asyncio
async def test_check_quota_sufficient(db_session: "AsyncSession") -> None:
    """Test quota check passes when sufficient quota available."""
    # Create tenant with quota
    tenant = Tenant(
        name="Test Tenant",
        storage_quota_bytes=100_000_000,  # 100MB
        storage_used_bytes=10_000_000,  # 10MB used
    )
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)
    
    quota_manager = QuotaManager(db_session)
    
    # Try to upload 5MB file (should pass)
    result = await quota_manager.check_quota(
        tenant_id=tenant.tenant_id,
        file_size=5_000_000,
    )
    
    assert result is True


@pytest.mark.asyncio
async def test_check_quota_exceeded(db_session: "AsyncSession") -> None:
    """Test quota check raises exception when quota would be exceeded."""
    # Create tenant near quota limit
    tenant = Tenant(
        name="Test Tenant",
        storage_quota_bytes=100_000_000,  # 100MB
        storage_used_bytes=95_000_000,  # 95MB used
    )
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)
    
    quota_manager = QuotaManager(db_session)
    
    # Try to upload 10MB file (should fail - would exceed quota)
    with pytest.raises(QuotaExceededError) as exc_info:
        await quota_manager.check_quota(
            tenant_id=tenant.tenant_id,
            file_size=10_000_000,
        )
    
    assert exc_info.value.used_bytes == 95_000_000
    assert exc_info.value.quota_bytes == 100_000_000


@pytest.mark.asyncio
async def test_check_quota_exactly_at_limit(db_session: "AsyncSession") -> None:
    """Test quota check passes when upload reaches exactly the limit."""
    tenant = Tenant(
        name="Test Tenant",
        storage_quota_bytes=100_000_000,  # 100MB
        storage_used_bytes=90_000_000,  # 90MB used
    )
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)
    
    quota_manager = QuotaManager(db_session)
    
    # Upload exactly remaining quota
    result = await quota_manager.check_quota(
        tenant_id=tenant.tenant_id,
        file_size=10_000_000,  # Exactly 10MB remaining
    )
    
    assert result is True


@pytest.mark.asyncio
async def test_update_usage_after_upload(db_session: "AsyncSession") -> None:
    """Test storage usage is updated after upload."""
    tenant = Tenant(
        name="Test Tenant",
        storage_quota_bytes=100_000_000,
        storage_used_bytes=10_000_000,
    )
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)
    
    quota_manager = QuotaManager(db_session)
    
    # Upload 5MB file
    new_usage = await quota_manager.update_usage(
        tenant_id=tenant.tenant_id,
        size_delta=5_000_000,
    )
    
    assert new_usage == 15_000_000
    
    # Verify database updated
    await db_session.refresh(tenant)
    assert tenant.storage_used_bytes == 15_000_000


@pytest.mark.asyncio
async def test_update_usage_after_deletion(db_session: "AsyncSession") -> None:
    """Test storage usage decreases after document deletion."""
    tenant = Tenant(
        name="Test Tenant",
        storage_quota_bytes=100_000_000,
        storage_used_bytes=20_000_000,
    )
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)
    
    quota_manager = QuotaManager(db_session)
    
    # Delete 5MB file (negative delta)
    new_usage = await quota_manager.update_usage(
        tenant_id=tenant.tenant_id,
        size_delta=-5_000_000,
    )
    
    assert new_usage == 15_000_000


@pytest.mark.asyncio
async def test_get_usage(db_session: "AsyncSession") -> None:
    """Test getting current storage usage statistics."""
    tenant = Tenant(
        name="Test Tenant",
        storage_quota_bytes=100_000_000,  # 100MB
        storage_used_bytes=30_000_000,  # 30MB
    )
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)
    
    quota_manager = QuotaManager(db_session)
    
    used, quota, percent = await quota_manager.get_usage(tenant_id=tenant.tenant_id)
    
    assert used == 30_000_000
    assert quota == 100_000_000
    assert percent == 30.0


@pytest.mark.asyncio
async def test_set_quota(db_session: "AsyncSession") -> None:
    """Test setting tenant storage quota."""
    tenant = Tenant(
        name="Test Tenant",
        storage_quota_bytes=100_000_000,
        storage_used_bytes=20_000_000,
    )
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)
    
    quota_manager = QuotaManager(db_session)
    
    # Increase quota to 200MB
    await quota_manager.set_quota(
        tenant_id=tenant.tenant_id,
        new_quota_bytes=200_000_000,
    )
    
    await db_session.refresh(tenant)
    assert tenant.storage_quota_bytes == 200_000_000


@pytest.mark.asyncio
async def test_set_quota_below_usage_fails(db_session: "AsyncSession") -> None:
    """Test setting quota below current usage is rejected."""
    tenant = Tenant(
        name="Test Tenant",
        storage_quota_bytes=100_000_000,
        storage_used_bytes=50_000_000,  # 50MB used
    )
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)
    
    quota_manager = QuotaManager(db_session)
    
    # Try to set quota to 30MB (less than current usage)
    with pytest.raises(ValueError, match="below current usage"):
        await quota_manager.set_quota(
            tenant_id=tenant.tenant_id,
            new_quota_bytes=30_000_000,
        )
