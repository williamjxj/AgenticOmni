"""Permission model for document-level access control."""

from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.storage_indexing.models.base import Base


class ResourceType(str, Enum):
    """Resource type enumeration for permissions."""

    DOCUMENT = "document"
    FOLDER = "folder"
    COLLECTION = "collection"


class PermissionLevel(str, Enum):
    """Permission level enumeration."""

    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class Permission(Base):
    """Permission entity for document-level access control.

    This model enables granular access control at the document, folder,
    or collection level. Each permission grants a user specific access
    to a resource.

    Attributes:
        permission_id: Primary key, unique permission identifier
        user_id: Foreign key to users table
        resource_type: Type of resource (document, folder, collection)
        resource_id: ID of the resource
        permission_level: Access level (read, write, admin)
        granted_at: Timestamp when permission was granted
        granted_by: User ID who granted the permission
    """

    __tablename__ = "permissions"

    permission_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Primary key, unique permission identifier",
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to users",
    )

    resource_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type of resource (document, folder, collection)",
    )

    resource_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="ID of the resource",
    )

    permission_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Access level (read, write, admin)",
    )

    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        comment="Timestamp when permission was granted",
    )

    granted_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
        comment="User ID who granted the permission",
    )

    def __repr__(self) -> str:
        """String representation of Permission."""
        return f"<Permission(permission_id={self.permission_id}, user_id={self.user_id}, level='{self.permission_level}')>"
