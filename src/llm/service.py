"""
LLM service layer.

Orchestrates LLM providers and integrates with the matching system.
AI advises, never decides.
"""

from functools import lru_cache

from sqlalchemy.orm import Session

from src.companies.models import CompanyProfile
from src.core.config import settings
from src.journalists.models import JournalistProfile
from src.llm.mock import MockLLMProvider
from src.llm.provider import (
    LLMProvider,
    MatchExplanation,
    PitchAngle,
    RiskAssessment,
)


@lru_cache()
def get_llm_provider() -> LLMProvider:
    """
    Get the configured LLM provider.

    Currently returns mock provider. In production, this would
    check configuration and return the appropriate provider.
    """
    # For Phase 5, we use mock provider only
    # Future: check settings.llm_provider and return appropriate provider
    return MockLLMProvider()


def explain_journalist_match(
    db: Session,
    company: CompanyProfile,
    journalist: JournalistProfile,
    matched_topics: list[str],
) -> MatchExplanation:
    """
    Generate a rich explanation for a company-journalist match.

    Combines deterministic match data with LLM-generated insights.
    """
    provider = get_llm_provider()

    company_topics = [t.name for t in company.topics]
    journalist_topics = [t.name for t in journalist.topics]

    return provider.explain_match(
        company_name=company.company_name,
        company_description=company.description or "",
        company_topics=company_topics,
        journalist_name=journalist.full_name,
        journalist_beat=journalist.beat_description,
        journalist_topics=journalist_topics,
        matched_topics=matched_topics,
    )


def explain_company_match(
    db: Session,
    journalist: JournalistProfile,
    company: CompanyProfile,
    matched_topics: list[str],
) -> MatchExplanation:
    """
    Generate a rich explanation for a journalist-company match.

    Same as explain_journalist_match but from journalist's perspective.
    """
    provider = get_llm_provider()

    company_topics = [t.name for t in company.topics]
    journalist_topics = [t.name for t in journalist.topics]

    return provider.explain_match(
        company_name=company.company_name,
        company_description=company.description or "",
        company_topics=company_topics,
        journalist_name=journalist.full_name,
        journalist_beat=journalist.beat_description,
        journalist_topics=journalist_topics,
        matched_topics=matched_topics,
    )


def suggest_angles_for_match(
    company: CompanyProfile,
    journalist: JournalistProfile,
    matched_topics: list[str],
    num_angles: int = 3,
) -> list[PitchAngle]:
    """
    Suggest pitch angles for a company-journalist match.

    These are advisory suggestions, not requirements.
    """
    provider = get_llm_provider()

    return provider.suggest_pitch_angles(
        company_name=company.company_name,
        company_description=company.description or "",
        journalist_name=journalist.full_name,
        journalist_beat=journalist.beat_description,
        matched_topics=matched_topics,
        num_angles=num_angles,
    )


def assess_match_risk(
    company: CompanyProfile,
    journalist: JournalistProfile,
) -> RiskAssessment:
    """
    Assess potential risks in pitching this journalist.

    Returns advisory flags, not blocking decisions.
    """
    provider = get_llm_provider()

    return provider.assess_risk(
        company_name=company.company_name,
        company_description=company.description or "",
        journalist_name=journalist.full_name,
        journalist_outlet=journalist.outlet_name,
        journalist_beat=journalist.beat_description,
    )
