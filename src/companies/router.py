"""
Company profile API endpoints.

Companies manage their own profiles. Journalists and admins can view public info.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth.service import get_current_user
from src.companies.schemas import (
    CompanyProfileCreate,
    CompanyProfilePublic,
    CompanyProfileResponse,
    CompanyProfileUpdate,
)
from src.companies.service import (
    create_profile,
    get_profile_by_id,
    get_profile_by_user_id,
    update_profile,
)
from src.core.database import get_db
from src.users.models import User, UserType

router = APIRouter(prefix="/companies", tags=["companies"])


def require_company(user: User) -> None:
    """Raise 403 if user is not a company."""
    if user.user_type != UserType.company:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only companies can access this endpoint",
        )


@router.get("/me", response_model=CompanyProfileResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the current company's profile."""
    require_company(current_user)

    profile = get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Create one first.",
        )
    return profile


@router.post("/me", response_model=CompanyProfileResponse, status_code=status.HTTP_201_CREATED)
def create_my_profile(
    profile_data: CompanyProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a profile for the current company."""
    require_company(current_user)

    existing = get_profile_by_user_id(db, current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already exists. Use PUT to update.",
        )

    return create_profile(db, current_user.id, profile_data)


@router.put("/me", response_model=CompanyProfileResponse)
def update_my_profile(
    update_data: CompanyProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update the current company's profile."""
    require_company(current_user)

    profile = get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Create one first.",
        )

    return update_profile(db, profile, update_data)


@router.get("/{profile_id}", response_model=CompanyProfilePublic)
def get_company_profile(
    profile_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    View a company's public profile.

    - Journalists see company info when considering pitches
    - Admins and other companies can also view
    """
    profile = get_profile_by_id(db, profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found",
        )

    return profile
