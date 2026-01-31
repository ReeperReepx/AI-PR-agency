"""
Matching API endpoints.

Companies find journalists. Journalists find companies.
All matches include explanations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.auth.service import get_current_user
from src.core.database import get_db
from src.matching.schemas import CompanyMatch, JournalistMatch, MatchResults
from src.matching.service import find_companies_for_journalist, find_journalists_for_company
from src.users.models import User, UserType

router = APIRouter(prefix="/matches", tags=["matching"])


@router.get("/journalists", response_model=MatchResults)
def get_journalist_matches(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Find journalists that match the company's topics.

    Returns journalists who:
    - Share at least one topic with the company
    - Are currently accepting pitches

    Each match includes an explanation of why it exists.
    """
    if current_user.user_type != UserType.company:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only companies can search for journalist matches",
        )

    matches, total = find_journalists_for_company(
        db, current_user.id, page=page, page_size=page_size
    )

    if total == 0 and page == 1:
        # Check if company has a profile
        from src.companies.service import get_profile_by_user_id
        profile = get_profile_by_user_id(db, current_user.id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Create a company profile first to find matches",
            )
        if not profile.topics:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Add topics to your profile to find matches",
            )

    return MatchResults(
        matches=matches,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(page * page_size) < total,
    )


@router.get("/companies", response_model=MatchResults)
def get_company_matches(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Find companies that match the journalist's topics.

    Returns companies who:
    - Share at least one topic with the journalist
    - Are currently active

    Each match includes an explanation of why it exists.
    """
    if current_user.user_type != UserType.journalist:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only journalists can search for company matches",
        )

    matches, total = find_companies_for_journalist(
        db, current_user.id, page=page, page_size=page_size
    )

    if total == 0 and page == 1:
        # Check if journalist has a profile
        from src.journalists.service import get_profile_by_user_id
        profile = get_profile_by_user_id(db, current_user.id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Create a journalist profile first to find matches",
            )
        if not profile.topics:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Add topics to your profile to find matches",
            )

    return MatchResults(
        matches=matches,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(page * page_size) < total,
    )
