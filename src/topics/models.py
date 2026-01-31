"""
Topic model for shared taxonomy.

Topics are the primary way journalists and companies are matched.
Both sides select from the same taxonomy for consistency.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import relationship

from src.core.database import Base


class Topic(Base):
    """
    A topic in the shared taxonomy.

    Examples: "artificial-intelligence", "climate-policy", "fintech"
    """

    __tablename__ = "topics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships defined via association tables in profile models
    journalists = relationship(
        "JournalistProfile", secondary="journalist_topics", back_populates="topics"
    )
    companies = relationship(
        "CompanyProfile", secondary="company_topics", back_populates="topics"
    )

    def __repr__(self):
        return f"<Topic {self.name}>"
