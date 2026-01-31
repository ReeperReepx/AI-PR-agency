"""
Matching service for finding journalist-company matches.

Orchestrates the matching rules and returns explainable results.
"""

from sqlalchemy.orm import Session

from src.companies.models import CompanyProfile
from src.companies.service import get_profile_by_user_id as get_company_profile
from src.journalists.models import JournalistProfile
from src.journalists.service import get_profile_by_user_id as get_journalist_profile
from src.matching.rules import (
    generate_match_reason,
    is_match,
)
from src.matching.schemas import CompanyMatch, JournalistMatch
from src.topics.schemas import TopicBrief


def find_journalists_for_company(
    db: Session, company_user_id: str, page: int = 1, page_size: int = 20
) -> tuple[list[JournalistMatch], int]:
    """
    Find journalists that match a company's topics.

    Returns (matches, total_count).
    """
    company = get_company_profile(db, company_user_id)
    if not company:
        return [], 0

    # Get all journalists who are accepting pitches
    journalists = (
        db.query(JournalistProfile)
        .filter(JournalistProfile.is_accepting_pitches.is_(True))
        .all()
    )

    matches = []
    for journalist in journalists:
        matched, overlap = is_match(company, journalist)
        if matched:
            reason = generate_match_reason(company, journalist, overlap)
            matches.append(
                JournalistMatch(
                    journalist_id=journalist.id,
                    full_name=journalist.full_name,
                    outlet_name=journalist.outlet_name,
                    outlet_type=journalist.outlet_type,
                    beat_description=journalist.beat_description,
                    matched_topics=[TopicBrief.model_validate(t) for t in overlap],
                    match_reason=reason,
                )
            )

    total = len(matches)

    # Paginate
    start = (page - 1) * page_size
    end = start + page_size
    paginated = matches[start:end]

    return paginated, total


def find_companies_for_journalist(
    db: Session, journalist_user_id: str, page: int = 1, page_size: int = 20
) -> tuple[list[CompanyMatch], int]:
    """
    Find companies that match a journalist's topics.

    Returns (matches, total_count).
    """
    journalist = get_journalist_profile(db, journalist_user_id)
    if not journalist:
        return [], 0

    # Get all active companies
    companies = (
        db.query(CompanyProfile)
        .filter(CompanyProfile.is_active.is_(True))
        .all()
    )

    matches = []
    for company in companies:
        matched, overlap = is_match(company, journalist)
        if matched:
            reason = generate_match_reason(company, journalist, overlap)
            matches.append(
                CompanyMatch(
                    company_id=company.id,
                    company_name=company.company_name,
                    industry=company.industry,
                    company_size=company.company_size,
                    description=company.description,
                    matched_topics=[TopicBrief.model_validate(t) for t in overlap],
                    match_reason=reason,
                )
            )

    total = len(matches)

    # Paginate
    start = (page - 1) * page_size
    end = start + page_size
    paginated = matches[start:end]

    return paginated, total
