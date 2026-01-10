"""Tenant model for multi-tenancy support."""

from typing import Any

from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.storage_indexing.models.base import Base, TimestampMixin


class Tenant(Base, TimestampMixin):
    """Tenant entity for multi-tenant application.

    Each tenant represents an organization or customer using the platform.
    Tenant isolation is enforced at the row level using tenant_id in other tables.

    Attributes:
        tenant_id: Primary key, unique tenant identifier
        name: Tenant name (organization name)
        domain: Tenant domain (e.g., acmecorp for acmecorp.example.com)
        settings: JSON field for tenant-specific configuration
        status: Tenant status (active, suspended, inactive)
        created_at: Record creation timestamp
        updated_at: Record last update timestamp
    """

    __tablename__ = "tenants"

    tenant_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Primary key, unique tenant identifier",
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Tenant name (organization name)",
    )

    domain: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="Tenant domain slug (unique identifier)",
    )

    settings: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
        comment="Tenant-specific configuration (JSONB)",
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
        comment="Tenant status (active, suspended, inactive)",
    )

    def __repr__(self) -> str:
        """String representation of Tenant."""
        return (
            f"<Tenant(tenant_id={self.tenant_id}, domain='{self.domain}', status='{self.status}')>"
        )
