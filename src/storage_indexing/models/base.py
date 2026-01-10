"""SQLAlchemy base classes and mixins.

This module defines the declarative base and common mixins used across all models.
"""

from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy declarative base class for all models."""


class TenantScopedMixin:
    """Mixin for models that enforce row-level tenant isolation.

    All models that include this mixin will have a tenant_id column with
    a foreign key constraint to the tenants table. This enables row-level
    isolation where queries are automatically filtered by tenant.
    """

    @declared_attr
    def tenant_id(cls) -> Mapped[int]:
        """Tenant ID for row-level isolation."""
        return mapped_column(
            Integer,
            nullable=False,
            index=True,
            comment="Tenant ID for row-level isolation",
        )


class TimestampMixin:
    """Mixin for models with created_at and updated_at timestamps."""

    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        """Timestamp when the record was created."""
        return mapped_column(
            DateTime(timezone=True),
            nullable=False,
            default=lambda: datetime.now(UTC),
            comment="Record creation timestamp",
        )

    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:
        """Timestamp when the record was last updated."""
        return mapped_column(
            DateTime(timezone=True),
            nullable=False,
            default=lambda: datetime.now(UTC),
            onupdate=lambda: datetime.now(UTC),
            comment="Record last update timestamp",
        )
