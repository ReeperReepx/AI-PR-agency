"""
Journalist profile service for CRUD operations.

Uses BaseProfileService for common operations.
"""

from sqlalchemy.orm import Session

from src.core.base_service import BaseProfileService
from src.journalists.models import JournalistProfile
from src.journalists.schemas import JournalistProfileCreate, JournalistProfileUpdate


class JournalistProfileService(BaseProfileService[JournalistProfile, JournalistProfileCreate, JournalistProfileUpdate]):
    """Service for journalist profile operations."""

    model_class = JournalistProfile
    profile_type = "journalist"
    filter_field = "is_accepting_pitches"


# Singleton instance
_service = JournalistProfileService()


# Backwards-compatible function API
def get_profile_by_user_id(db: Session, user_id: str) -> JournalistProfile | None:
    """Get a journalist profile by user ID."""
    return _service.get_by_user_id(db, user_id)


def get_profile_by_id(db: Session, profile_id: str) -> JournalistProfile | None:
    """Get a journalist profile by profile ID."""
    return _service.get_by_id(db, profile_id)


def create_profile(
    db: Session, user_id: str, profile_data: JournalistProfileCreate
) -> JournalistProfile:
    """Create a new journalist profile."""
    return _service.create(db, user_id, profile_data)


def update_profile(
    db: Session, profile: JournalistProfile, update_data: JournalistProfileUpdate
) -> JournalistProfile:
    """Update an existing journalist profile."""
    return _service.update(db, profile, update_data)


def list_profiles(
    db: Session, accepting_only: bool = False, skip: int = 0, limit: int = 100
) -> list[JournalistProfile]:
    """List journalist profiles."""
    return _service.list_all(db, filter_active=accepting_only, skip=skip, limit=limit)
