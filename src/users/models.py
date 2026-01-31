"""
User database model.

Defines the User table with identity and authentication fields.
Profile data belongs in Phase 2 (structured data capture).
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class UserType(str, enum.Enum):
    """User types in the platform. Each has different permissions and flows."""

    journalist = "journalist"
    company = "company"
    admin = "admin"


class User(Base):
    """
    Core user entity for authentication and identity.

    This table only handles WHO the user is.
    WHAT they do (profiles, preferences) is handled in separate tables.
    """

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    user_type: Mapped[UserType] = mapped_column(Enum(UserType))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
