"""
Company profile service for CRUD operations.
"""

from sqlalchemy.orm import Session

from src.companies.models import CompanyProfile
from src.companies.schemas import CompanyProfileCreate, CompanyProfileUpdate
from src.topics.service import get_topics_by_ids


def get_profile_by_user_id(db: Session, user_id: str) -> CompanyProfile | None:
    """Get a company profile by user ID."""
    return db.query(CompanyProfile).filter(CompanyProfile.user_id == user_id).first()


def get_profile_by_id(db: Session, profile_id: str) -> CompanyProfile | None:
    """Get a company profile by profile ID."""
    return db.query(CompanyProfile).filter(CompanyProfile.id == profile_id).first()


def create_profile(
    db: Session, user_id: str, profile_data: CompanyProfileCreate
) -> CompanyProfile:
    """Create a new company profile."""
    # Get topics
    topics = get_topics_by_ids(db, profile_data.topic_ids)

    profile = CompanyProfile(
        user_id=user_id,
        company_name=profile_data.company_name,
        description=profile_data.description,
        website=profile_data.website,
        industry=profile_data.industry,
        company_size=profile_data.company_size,
        founded_year=profile_data.founded_year,
        headquarters=profile_data.headquarters,
        topics=topics,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_profile(
    db: Session, profile: CompanyProfile, update_data: CompanyProfileUpdate
) -> CompanyProfile:
    """Update an existing company profile."""
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
    db: Session, active_only: bool = False, skip: int = 0, limit: int = 100
) -> list[CompanyProfile]:
    """List company profiles."""
    query = db.query(CompanyProfile)
    if active_only:
        query = query.filter(CompanyProfile.is_active.is_(True))
    return query.offset(skip).limit(limit).all()
