"""
Journalist profile model.

Stores structured data about what journalists cover and how they prefer to be contacted.
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


class OutletType(str, enum.Enum):
    """Type of media outlet."""

    newspaper = "newspaper"
    magazine = "magazine"
    online = "online"
    broadcast = "broadcast"
    podcast = "podcast"
    newsletter = "newsletter"
    freelance = "freelance"


class ContactMethod(str, enum.Enum):
    """Preferred contact method."""

    email = "email"
    twitter = "twitter"
    linkedin = "linkedin"


# Association table for journalist-topic many-to-many
journalist_topics = Table(
    "journalist_topics",
    Base.metadata,
    Column("journalist_id", String, ForeignKey("journalist_profiles.id"), primary_key=True),
    Column("topic_id", String, ForeignKey("topics.id"), primary_key=True),
)


class JournalistProfile(Base):
    """
    A journalist's profile with structured editorial preferences.

    Linked 1:1 with a User of type 'journalist'.
    """

    __tablename__ = "journalist_profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)

    # Identity
    full_name = Column(String(200), nullable=False)
    bio = Column(Text, nullable=True)

    # Outlet info
    outlet_name = Column(String(200), nullable=False)
    outlet_type = Column(Enum(OutletType), nullable=False)

    # Beat/coverage
    beat_description = Column(Text, nullable=False)

    # Preferences
    min_pitch_notice_days = Column(Integer, default=3, nullable=False)
    preferred_contact_method = Column(Enum(ContactMethod), default=ContactMethod.email)
    is_accepting_pitches = Column(Boolean, default=True, nullable=False)

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
    user = relationship("User", backref="journalist_profile")
    topics = relationship("Topic", secondary=journalist_topics, back_populates="journalists")

    def __repr__(self):
        return f"<JournalistProfile {self.full_name} @ {self.outlet_name}>"
