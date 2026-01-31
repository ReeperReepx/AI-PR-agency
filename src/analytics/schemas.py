"""
Pydantic schemas for analytics.
"""

from datetime import datetime

from pydantic import BaseModel


class UserMetrics(BaseModel):
    """Metrics for a single user."""

    user_id: str
    user_type: str
    profile_complete: bool
    topic_count: int
    matches_found: int  # How many matches available
    feedback_given: int
    last_active: datetime | None


class PlatformMetrics(BaseModel):
    """Platform-wide metrics for admins."""

    total_users: int
    journalist_count: int
    company_count: int
    admin_count: int

    profiles_complete: int
    total_topics: int
    topics_in_use: int

    total_feedback: int
    helpful_feedback: int
    helpfulness_rate: float

    total_matches_possible: int  # Based on topic overlap
    avg_matches_per_profile: float


class MatchQualityMetrics(BaseModel):
    """Match quality metrics."""

    total_matches_searched: int  # Number of match queries
    unique_matches_found: int
    feedback_coverage: float  # % of matches with feedback
    helpfulness_rate: float
    success_rate: float  # % of matches marked successful
