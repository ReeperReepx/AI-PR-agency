"""
Company profile service for CRUD operations.

Uses BaseProfileService for common operations.
"""

from sqlalchemy.orm import Session

from src.companies.models import CompanyProfile
from src.companies.schemas import CompanyProfileCreate, CompanyProfileUpdate
from src.core.base_service import BaseProfileService


class CompanyProfileService(BaseProfileService[CompanyProfile, CompanyProfileCreate, CompanyProfileUpdate]):
    """Service for company profile operations."""

    model_class = CompanyProfile
    profile_type = "company"
    filter_field = "is_active"


# Singleton instance
_service = CompanyProfileService()


# Backwards-compatible function API
def get_profile_by_user_id(db: Session, user_id: str) -> CompanyProfile | None:
    """Get a company profile by user ID."""
    return _service.get_by_user_id(db, user_id)


def get_profile_by_id(db: Session, profile_id: str) -> CompanyProfile | None:
    """Get a company profile by profile ID."""
    return _service.get_by_id(db, profile_id)


def create_profile(
    db: Session, user_id: str, profile_data: CompanyProfileCreate
) -> CompanyProfile:
    """Create a new company profile."""
    return _service.create(db, user_id, profile_data)


def update_profile(
    db: Session, profile: CompanyProfile, update_data: CompanyProfileUpdate
) -> CompanyProfile:
    """Update an existing company profile."""
    return _service.update(db, profile, update_data)


def list_profiles(
    db: Session, active_only: bool = False, skip: int = 0, limit: int = 100
) -> list[CompanyProfile]:
    """List company profiles."""
    return _service.list_all(db, filter_active=active_only, skip=skip, limit=limit)
