"""
Company profile model.

Stores structured data about companies and their story angles.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship

from src.core.database import Base


class CompanySize(str, enum.Enum):
    """Company size classification."""

    startup = "startup"  # 1-10
    small = "small"  # 11-50
    medium = "medium"  # 51-200
    large = "large"  # 201-1000
    enterprise = "enterprise"  # 1000+


# Association table for company-topic many-to-many
company_topics = Table(
    "company_topics",
    Base.metadata,
    Column("company_id", String, ForeignKey("company_profiles.id"), primary_key=True),
    Column("topic_id", String, ForeignKey("topics.id"), primary_key=True),
)


class CompanyProfile(Base):
    """
    A company's profile with structured business information.

    Linked 1:1 with a User of type 'company'.
    """

    __tablename__ = "company_profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)

    # Identity
    company_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    website = Column(String(500), nullable=True)

    # Business info
    industry = Column(String(100), nullable=False)
    company_size = Column(Enum(CompanySize), nullable=False)
    founded_year = Column(Integer, nullable=True)
    headquarters = Column(String(200), nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user = relationship("User", backref="company_profile")
    topics = relationship("Topic", secondary=company_topics, back_populates="companies")

    def __repr__(self):
        return f"<CompanyProfile {self.company_name}>"
