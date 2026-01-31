"""
Analytics service for platform metrics.

Calculates and returns platform-wide statistics.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func

from src.analytics.schemas import PlatformMetrics, UserMetrics
from src.companies.models import CompanyProfile
from src.feedback.models import FeedbackType, MatchFeedback
from src.journalists.models import JournalistProfile
from src.topics.models import Topic
from src.users.models import User, UserType


def get_platform_metrics(db: Session) -> PlatformMetrics:
    """
    Calculate platform-wide metrics.

    For admin dashboard and monitoring.
    """
    # User counts by type
    user_counts = (
        db.query(User.user_type, func.count(User.id))
        .group_by(User.user_type)
        .all()
    )
    counts_by_type = {ut: 0 for ut in UserType}
    for user_type, count in user_counts:
        counts_by_type[user_type] = count

    total_users = sum(counts_by_type.values())

    # Profile counts
    journalist_profiles = db.query(func.count(JournalistProfile.id)).scalar() or 0
    company_profiles = db.query(func.count(CompanyProfile.id)).scalar() or 0
    profiles_complete = journalist_profiles + company_profiles

    # Topic stats
    total_topics = db.query(func.count(Topic.id)).scalar() or 0

    # Count topics actually in use (assigned to profiles)
    from src.journalists.models import journalist_topics
    from src.companies.models import company_topics

    journalist_topic_count = db.query(func.count(func.distinct(journalist_topics.c.topic_id))).scalar() or 0
    company_topic_count = db.query(func.count(func.distinct(company_topics.c.topic_id))).scalar() or 0
    topics_in_use = max(journalist_topic_count, company_topic_count)  # Approximate

    # Feedback stats
    total_feedback = db.query(func.count(MatchFeedback.id)).scalar() or 0
    helpful_feedback = (
        db.query(func.count(MatchFeedback.id))
        .filter(MatchFeedback.feedback_type == FeedbackType.helpful)
        .scalar() or 0
    )

    # Calculate helpfulness rate
    not_helpful_count = (
        db.query(func.count(MatchFeedback.id))
        .filter(MatchFeedback.feedback_type == FeedbackType.not_helpful)
        .scalar() or 0
    )
    rated_feedback = helpful_feedback + not_helpful_count
    helpfulness_rate = helpful_feedback / rated_feedback if rated_feedback > 0 else 0.0

    # Calculate potential matches (simplified - count profiles with topic overlap)
    # This is an approximation
    total_matches_possible = journalist_profiles * company_profiles  # Maximum possible

    avg_matches = total_matches_possible / profiles_complete if profiles_complete > 0 else 0.0

    return PlatformMetrics(
        total_users=total_users,
        journalist_count=counts_by_type[UserType.journalist],
        company_count=counts_by_type[UserType.company],
        admin_count=counts_by_type[UserType.admin],
        profiles_complete=profiles_complete,
        total_topics=total_topics,
        topics_in_use=topics_in_use,
        total_feedback=total_feedback,
        helpful_feedback=helpful_feedback,
        helpfulness_rate=round(helpfulness_rate, 3),
        total_matches_possible=total_matches_possible,
        avg_matches_per_profile=round(avg_matches, 2),
    )


def get_user_metrics(db: Session, user: User) -> UserMetrics:
    """
    Get metrics for a specific user.

    Shows their profile status and engagement.
    """
    profile_complete = False
    topic_count = 0
    matches_found = 0

    if user.user_type == UserType.journalist:
        from src.journalists.service import get_profile_by_user_id

        profile = get_profile_by_user_id(db, user.id)
        if profile:
            profile_complete = True
            topic_count = len(profile.topics)
            # Count matching companies
            from src.matching.service import find_companies_for_journalist

            _, matches_found = find_companies_for_journalist(db, user.id)

    elif user.user_type == UserType.company:
        from src.companies.service import get_profile_by_user_id

        profile = get_profile_by_user_id(db, user.id)
        if profile:
            profile_complete = True
            topic_count = len(profile.topics)
            # Count matching journalists
            from src.matching.service import find_journalists_for_company

            _, matches_found = find_journalists_for_company(db, user.id)

    # Count feedback given
    feedback_count = (
        db.query(func.count(MatchFeedback.id))
        .filter(MatchFeedback.user_id == user.id)
        .scalar() or 0
    )

    return UserMetrics(
        user_id=user.id,
        user_type=user.user_type.value,
        profile_complete=profile_complete,
        topic_count=topic_count,
        matches_found=matches_found,
        feedback_given=feedback_count,
        last_active=user.updated_at,
    )
