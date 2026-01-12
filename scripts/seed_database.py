#!/usr/bin/env python3
"""Seed database with initial tenant and user data.

This script creates a default tenant and user for development/testing.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import structlog
from sqlalchemy import select

from src.shared.config import settings
from src.storage_indexing.database import get_db, init_db
from src.storage_indexing.models.tenant import Tenant
from src.storage_indexing.models.user import User

logger = structlog.get_logger(__name__)


async def seed_database() -> None:
    """Seed database with initial data."""
    init_db()
    
    logger.info("Starting database seeding...")
    
    async for db in get_db():
        # Check if tenant already exists
        result = await db.execute(select(Tenant).where(Tenant.tenant_id == 1))
        existing_tenant = result.scalar_one_or_none()
        
        if existing_tenant:
            logger.info("Tenant 1 already exists, skipping creation")
        else:
            # Create default tenant
            tenant = Tenant(
                tenant_id=1,
                name="Default Tenant",
                domain="default",
                status="active",
                storage_quota_bytes=10 * 1024 * 1024 * 1024,  # 10 GB
                storage_used_bytes=0,
            )
            db.add(tenant)
            await db.flush()
            logger.info(
                "Created default tenant",
                tenant_id=tenant.tenant_id,
                name=tenant.name,
                domain=tenant.domain,
                storage_quota_gb=10,
            )
        
        # Check if user already exists
        result = await db.execute(select(User).where(User.user_id == 1))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            logger.info("User 1 already exists, skipping creation")
        else:
            # Create default user
            user = User(
                user_id=1,
                tenant_id=1,
                email="admin@example.com",
                hashed_password="dummy_hash_for_dev",  # Not used in dev mode
                role="admin",
                full_name="Administrator",
                is_active=True,
            )
            db.add(user)
            await db.flush()
            logger.info(
                "Created default user",
                user_id=user.user_id,
                email=user.email,
                role=user.role,
                tenant_id=user.tenant_id,
            )
        
        # Commit all changes
        await db.commit()
        
        logger.info("Database seeding complete!")
        
        print("\n" + "=" * 70)
        print("DATABASE SEEDING COMPLETE")
        print("=" * 70)
        print("\n✅ Default Tenant Created:")
        print(f"   ID: 1")
        print(f"   Name: Default Tenant")
        print(f"   Storage Quota: 10 GB")
        print("\n✅ Default User Created:")
        print(f"   ID: 1")
        print(f"   Email: admin@example.com")
        print(f"   Role: admin")
        print(f"   Tenant ID: 1")
        print("\n" + "=" * 70)
        print("\nYou can now upload documents:")
        print("  - Web UI: http://localhost:3000/upload")
        print("  - Or test: ./scripts/test_upload.sh")
        print()


if __name__ == "__main__":
    asyncio.run(seed_database())
