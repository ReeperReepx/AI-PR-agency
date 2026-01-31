"""
Journalist profile API endpoints.

Journalists manage their own profiles. Companies and admins can view public info.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth.service import get_current_user
from src.core.database import get_db
from src.journalists.schemas import (
    JournalistProfileCreate,
    JournalistProfilePublic,
    JournalistProfileResponse,
    JournalistProfileUpdate,
)
from src.journalists.service import (
    create_profile,
    get_profile_by_id,
    get_profile_by_user_id,
    update_profile,
)
from src.users.models import User, UserType
from src.users.service import is_admin

router = APIRouter(prefix="/journalists", tags=["journalists"])


def require_journalist(user: User) -> None:
    """Raise 403 if user is not a journalist."""
    if user.user_type != UserType.journalist:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only journalists can access this endpoint",
        )


@router.get("/me", response_model=JournalistProfileResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the current journalist's profile."""
    require_journalist(current_user)

    profile = get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Create one first.",
        )
    return profile


@router.post("/me", response_model=JournalistProfileResponse, status_code=status.HTTP_201_CREATED)
def create_my_profile(
    profile_data: JournalistProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a profile for the current journalist."""
    require_journalist(current_user)

    existing = get_profile_by_user_id(db, current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already exists. Use PUT to update.",
        )

    return create_profile(db, current_user.id, profile_data)


@router.put("/me", response_model=JournalistProfileResponse)
def update_my_profile(
    update_data: JournalistProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update the current journalist's profile."""
    require_journalist(current_user)

    profile = get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Create one first.",
        )

    return update_profile(db, profile, update_data)


@router.get("/{profile_id}", response_model=JournalistProfilePublic)
def get_journalist_profile(
    profile_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    View a journalist's public profile.

    - Companies see limited public info
    - Admins see limited public info (full access via admin endpoints if needed)
    - Journalists can view other journalists' public profiles
    """
    profile = get_profile_by_id(db, profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journalist profile not found",
        )

    return profile
