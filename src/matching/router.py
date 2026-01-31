"""
Matching API endpoints.

Companies find journalists. Journalists find companies.
All matches include explanations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.auth.service import get_current_user
from src.core.database import get_db
from src.matching.schemas import (
    MatchResults,
    SimilarCompanyMatch,
    SimilarJournalistMatch,
    SimilarMatchResults,
)
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


# Similarity-based matching (Phase 4)


@router.get("/similar/journalists", response_model=SimilarMatchResults)
def get_similar_journalists(
    min_similarity: float = Query(0.3, ge=0.0, le=1.0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Find journalists with semantically similar profiles (embedding-based).

    Unlike topic matching, this finds journalists whose beat descriptions
    are semantically related to the company's description, even without
    exact topic overlap.

    Requires the company to have a profile with an embedding.
    """
    if current_user.user_type != UserType.company:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only companies can search for similar journalists",
        )

    from src.companies.service import get_profile_by_user_id
    from src.embeddings.service import find_similar_journalists

    profile = get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Create a company profile first",
        )

    results = find_similar_journalists(
        db, profile.id, min_similarity=min_similarity, limit=limit
    )

    matches = [
        SimilarJournalistMatch(
            journalist_id=journalist.id,
            full_name=journalist.full_name,
            outlet_name=journalist.outlet_name,
            outlet_type=journalist.outlet_type,
            beat_description=journalist.beat_description,
            similarity_score=round(score, 3),
            match_reason=f"Profile similarity: {round(score * 100)}% match based on semantic analysis of {journalist.full_name}'s beat and {profile.company_name}'s description.",
        )
        for journalist, score in results
    ]

    return SimilarMatchResults(matches=matches, total=len(matches))


@router.get("/similar/companies", response_model=SimilarMatchResults)
def get_similar_companies(
    min_similarity: float = Query(0.3, ge=0.0, le=1.0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Find companies with semantically similar profiles (embedding-based).

    Unlike topic matching, this finds companies whose descriptions
    are semantically related to the journalist's beat, even without
    exact topic overlap.

    Requires the journalist to have a profile with an embedding.
    """
    if current_user.user_type != UserType.journalist:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only journalists can search for similar companies",
        )

    from src.embeddings.service import find_similar_companies
    from src.journalists.service import get_profile_by_user_id

    profile = get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Create a journalist profile first",
        )

    results = find_similar_companies(
        db, profile.id, min_similarity=min_similarity, limit=limit
    )

    matches = [
        SimilarCompanyMatch(
            company_id=company.id,
            company_name=company.company_name,
            industry=company.industry,
            company_size=company.company_size,
            description=company.description,
            similarity_score=round(score, 3),
            match_reason=f"Profile similarity: {round(score * 100)}% match based on semantic analysis of {company.company_name}'s profile and {profile.full_name}'s beat.",
        )
        for company, score in results
    ]

    return SimilarMatchResults(matches=matches, total=len(matches))
