"""
Pydantic schemas for match feedback.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.feedback.models import FeedbackType


class FeedbackCreate(BaseModel):
    """Create feedback on a match."""

    journalist_profile_id: str
    company_profile_id: str
    feedback_type: FeedbackType
    notes: str | None = None


class FeedbackResponse(BaseModel):
    """Feedback response after creation."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    journalist_profile_id: str
    company_profile_id: str
    feedback_type: FeedbackType
    notes: str | None
    created_at: datetime


class FeedbackStats(BaseModel):
    """Statistics about feedback for a user or match."""

    total_feedback: int
    helpful_count: int
    not_helpful_count: int
    contacted_count: int
    successful_count: int
    helpfulness_rate: float  # helpful / (helpful + not_helpful)


class FeedbackSummary(BaseModel):
    """Summary of feedback given by a user."""

    user_id: str
    stats: FeedbackStats
    recent_feedback: list[FeedbackResponse]
