"""
Feedback service for match quality tracking.

Manages feedback CRUD and statistics.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func

from src.feedback.models import MatchFeedback, FeedbackType
from src.feedback.schemas import FeedbackCreate, FeedbackStats


def create_feedback(
    db: Session,
    user_id: str,
    feedback_data: FeedbackCreate,
) -> MatchFeedback:
    """
    Create feedback for a match.

    Updates existing feedback if user already rated this match.
    """
    # Check for existing feedback from this user on this match
    existing = (
        db.query(MatchFeedback)
        .filter(
            MatchFeedback.user_id == user_id,
            MatchFeedback.journalist_profile_id == feedback_data.journalist_profile_id,
            MatchFeedback.company_profile_id == feedback_data.company_profile_id,
        )
        .first()
    )

    if existing:
        # Update existing feedback
        existing.feedback_type = feedback_data.feedback_type
        existing.notes = feedback_data.notes
        db.commit()
        db.refresh(existing)
        return existing

    # Create new feedback
    feedback = MatchFeedback(
        user_id=user_id,
        journalist_profile_id=feedback_data.journalist_profile_id,
        company_profile_id=feedback_data.company_profile_id,
        feedback_type=feedback_data.feedback_type,
        notes=feedback_data.notes,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


def get_user_feedback(
    db: Session,
    user_id: str,
    limit: int = 20,
) -> list[MatchFeedback]:
    """Get recent feedback from a user."""
    return (
        db.query(MatchFeedback)
        .filter(MatchFeedback.user_id == user_id)
        .order_by(MatchFeedback.created_at.desc())
        .limit(limit)
        .all()
    )


def get_feedback_stats(
    db: Session,
    user_id: str | None = None,
    journalist_profile_id: str | None = None,
    company_profile_id: str | None = None,
) -> FeedbackStats:
    """
    Get feedback statistics.

    Can filter by user, journalist, or company.
    """
    query = db.query(MatchFeedback)

    if user_id:
        query = query.filter(MatchFeedback.user_id == user_id)
    if journalist_profile_id:
        query = query.filter(MatchFeedback.journalist_profile_id == journalist_profile_id)
    if company_profile_id:
        query = query.filter(MatchFeedback.company_profile_id == company_profile_id)

    # Count by feedback type
    type_counts = (
        query.with_entities(MatchFeedback.feedback_type, func.count(MatchFeedback.id))
        .group_by(MatchFeedback.feedback_type)
        .all()
    )

    counts = {ft: 0 for ft in FeedbackType}
    for feedback_type, count in type_counts:
        counts[feedback_type] = count

    total = sum(counts.values())
    helpful = counts[FeedbackType.helpful]
    not_helpful = counts[FeedbackType.not_helpful]

    # Calculate helpfulness rate
    rated_count = helpful + not_helpful
    helpfulness_rate = helpful / rated_count if rated_count > 0 else 0.0

    return FeedbackStats(
        total_feedback=total,
        helpful_count=helpful,
        not_helpful_count=not_helpful,
        contacted_count=counts[FeedbackType.contacted],
        successful_count=counts[FeedbackType.successful],
        helpfulness_rate=round(helpfulness_rate, 3),
    )


def get_match_feedback(
    db: Session,
    journalist_profile_id: str,
    company_profile_id: str,
) -> list[MatchFeedback]:
    """Get all feedback for a specific match."""
    return (
        db.query(MatchFeedback)
        .filter(
            MatchFeedback.journalist_profile_id == journalist_profile_id,
            MatchFeedback.company_profile_id == company_profile_id,
        )
        .order_by(MatchFeedback.created_at.desc())
        .all()
    )
