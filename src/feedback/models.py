"""
Feedback models for match quality tracking.

Stores user feedback on matches for continuous improvement.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from src.core.database import Base


class FeedbackType(str, enum.Enum):
    """Types of match feedback."""

    helpful = "helpful"  # Match was relevant
    not_helpful = "not_helpful"  # Match was irrelevant
    contacted = "contacted"  # User reached out based on match
    successful = "successful"  # Match led to coverage/story


class MatchFeedback(Base):
    """
    Feedback on a match between a company and journalist.

    Tracks whether matches are helpful and if they led to outcomes.
    """

    __tablename__ = "match_feedback"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Who gave the feedback
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    user = relationship("User")

    # The match that was rated
    journalist_profile_id = Column(String, ForeignKey("journalist_profiles.id"), nullable=False)
    company_profile_id = Column(String, ForeignKey("company_profiles.id"), nullable=False)

    journalist_profile = relationship("JournalistProfile")
    company_profile = relationship("CompanyProfile")

    # Feedback details
    feedback_type = Column(Enum(FeedbackType), nullable=False)
    notes = Column(Text, nullable=True)  # Optional user notes

    def __repr__(self):
        return f"<MatchFeedback {self.user_id} -> {self.feedback_type.value}>"
