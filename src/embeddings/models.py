"""
Embedding storage model.

Stores pre-computed embeddings for profiles to enable fast similarity search.
"""

import enum
import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, String, Text

from src.core.database import Base


class ProfileType(str, enum.Enum):
    """Type of profile the embedding belongs to."""

    journalist = "journalist"
    company = "company"


class ProfileEmbedding(Base):
    """
    Stored embedding for a profile.

    Embeddings are stored as JSON arrays for SQLite compatibility.
    For production with PostgreSQL, consider using pgvector.
    """

    __tablename__ = "profile_embeddings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_type = Column(Enum(ProfileType), nullable=False, index=True)
    profile_id = Column(String, nullable=False, index=True)

    # Embedding stored as JSON string (list of floats)
    embedding_json = Column(Text, nullable=False)

    # The source text that was embedded (for debugging/regeneration)
    source_text = Column(Text, nullable=False)

    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    @property
    def embedding(self) -> list[float]:
        """Get embedding as a list of floats."""
        return json.loads(self.embedding_json)

    @embedding.setter
    def embedding(self, value: list[float]) -> None:
        """Set embedding from a list of floats."""
        self.embedding_json = json.dumps(value)

    def __repr__(self):
        return f"<ProfileEmbedding {self.profile_type}:{self.profile_id}>"
