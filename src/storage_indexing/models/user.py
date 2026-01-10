"""User model for authentication and authorization."""

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.storage_indexing.models.base import Base, TenantScopedMixin, TimestampMixin


class UserRole(str, Enum):
    """User role enumeration for RBAC."""

    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class User(Base, TenantScopedMixin, TimestampMixin):
    """User entity for authentication and authorization.

    Each user belongs to a tenant and has a specific role for RBAC.

    Attributes:
        user_id: Primary key, unique user identifier
        tenant_id: Foreign key to tenants table (row-level isolation)
        email: User email address (unique per tenant)
        hashed_password: Bcrypt hashed password
        role: User role (admin, editor, viewer)
        full_name: User's full name
        last_login: Last login timestamp
        is_active: Account active status
        created_at: Record creation timestamp
        updated_at: Record last update timestamp
    """

    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Primary key, unique user identifier",
    )

    tenant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tenants.tenant_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to tenants (row-level isolation)",
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="User email address (unique per tenant)",
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Bcrypt hashed password",
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=UserRole.VIEWER.value,
        comment="User role for RBAC (admin, editor, viewer)",
    )

    full_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="User's full name",
    )

    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last login timestamp",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Account active status",
    )

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(user_id={self.user_id}, email='{self.email}', role='{self.role}')>"
