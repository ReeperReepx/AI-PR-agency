"""
Deterministic matching rules.

Pure functions that implement hard matching logic.
Rules before embeddings. If a rule can solve it, don't use AI.
"""

from src.companies.models import CompanyProfile
from src.journalists.models import JournalistProfile
from src.topics.models import Topic


def get_topic_overlap(topics_a: list[Topic], topics_b: list[Topic]) -> list[Topic]:
    """
    Find overlapping topics between two lists.

    Returns the intersection as a list of Topic objects.
    """
    ids_a = {t.id for t in topics_a}
    return [t for t in topics_b if t.id in ids_a]


def journalist_is_eligible(journalist: JournalistProfile) -> bool:
    """
    Check if a journalist is eligible for matching.

    Rules:
    - Must be accepting pitches
    - Must have at least one topic
    """
    return journalist.is_accepting_pitches and len(journalist.topics) > 0


def company_is_eligible(company: CompanyProfile) -> bool:
    """
    Check if a company is eligible for matching.

    Rules:
    - Must be active
    - Must have at least one topic
    """
    return company.is_active and len(company.topics) > 0


def is_match(
    company: CompanyProfile, journalist: JournalistProfile
) -> tuple[bool, list[Topic]]:
    """
    Determine if a company and journalist match.

    Returns (is_match, overlapping_topics).

    Match requires:
    1. Company is eligible
    2. Journalist is eligible
    3. At least one topic overlap
    """
    if not company_is_eligible(company):
        return False, []

    if not journalist_is_eligible(journalist):
        return False, []

    overlap = get_topic_overlap(company.topics, journalist.topics)

    if not overlap:
        return False, []

    return True, overlap


def generate_match_reason(
    company: CompanyProfile,
    journalist: JournalistProfile,
    matched_topics: list[Topic],
) -> str:
    """
    Generate a human-readable explanation for why this match exists.

    Explainability is a core requirement.
    """
    topic_names = [t.display_name for t in matched_topics]

    if len(topic_names) == 1:
        topics_str = topic_names[0]
    elif len(topic_names) == 2:
        topics_str = f"{topic_names[0]} and {topic_names[1]}"
    else:
        topics_str = f"{', '.join(topic_names[:-1])}, and {topic_names[-1]}"

    return (
        f"{journalist.full_name} at {journalist.outlet_name} covers {topics_str}, "
        f"which aligns with {company.company_name}'s expertise."
    )
