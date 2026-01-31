"""
Journalist profile service for CRUD operations.
"""

from sqlalchemy.orm import Session

from src.journalists.models import JournalistProfile
from src.journalists.schemas import JournalistProfileCreate, JournalistProfileUpdate
from src.topics.service import get_topics_by_ids


def get_profile_by_user_id(db: Session, user_id: str) -> JournalistProfile | None:
    """Get a journalist profile by user ID."""
    return db.query(JournalistProfile).filter(JournalistProfile.user_id == user_id).first()


def get_profile_by_id(db: Session, profile_id: str) -> JournalistProfile | None:
    """Get a journalist profile by profile ID."""
    return db.query(JournalistProfile).filter(JournalistProfile.id == profile_id).first()


def create_profile(
    db: Session, user_id: str, profile_data: JournalistProfileCreate
) -> JournalistProfile:
    """Create a new journalist profile."""
    # Get topics
    topics = get_topics_by_ids(db, profile_data.topic_ids)

    profile = JournalistProfile(
        user_id=user_id,
        full_name=profile_data.full_name,
        bio=profile_data.bio,
        outlet_name=profile_data.outlet_name,
        outlet_type=profile_data.outlet_type,
        beat_description=profile_data.beat_description,
        min_pitch_notice_days=profile_data.min_pitch_notice_days,
        preferred_contact_method=profile_data.preferred_contact_method,
        is_accepting_pitches=profile_data.is_accepting_pitches,
        topics=topics,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_profile(
    db: Session, profile: JournalistProfile, update_data: JournalistProfileUpdate
) -> JournalistProfile:
    """Update an existing journalist profile."""
    update_dict = update_data.model_dump(exclude_unset=True)

    # Handle topics separately
    if "topic_ids" in update_dict:
        topic_ids = update_dict.pop("topic_ids")
        profile.topics = get_topics_by_ids(db, topic_ids)

    # Update other fields
    for field, value in update_dict.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile


def list_profiles(
    db: Session, accepting_only: bool = False, skip: int = 0, limit: int = 100
) -> list[JournalistProfile]:
    """List journalist profiles."""
    query = db.query(JournalistProfile)
    if accepting_only:
        query = query.filter(JournalistProfile.is_accepting_pitches.is_(True))
    return query.offset(skip).limit(limit).all()
