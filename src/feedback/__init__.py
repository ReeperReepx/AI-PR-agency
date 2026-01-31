"""
Feedback module (Phase 6).

Enables users to provide feedback on matches for continuous improvement.
"""

from src.feedback.models import MatchFeedback, FeedbackType
from src.feedback.service import create_feedback, get_feedback_stats

__all__ = ["MatchFeedback", "FeedbackType", "create_feedback", "get_feedback_stats"]
