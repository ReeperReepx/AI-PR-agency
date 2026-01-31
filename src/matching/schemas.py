"""
Pydantic schemas for match results.

Every match includes an explanation — explainability is required.
"""

from pydantic import BaseModel, ConfigDict

from src.companies.models import CompanySize
from src.journalists.models import OutletType
from src.topics.schemas import TopicBrief


class JournalistMatch(BaseModel):
    """A journalist that matches a company's topics."""

    model_config = ConfigDict(from_attributes=True)

    journalist_id: str
    full_name: str
    outlet_name: str
    outlet_type: OutletType
    beat_description: str
    matched_topics: list[TopicBrief]
    match_reason: str


class CompanyMatch(BaseModel):
    """A company that matches a journalist's topics."""

    model_config = ConfigDict(from_attributes=True)

    company_id: str
    company_name: str
    industry: str
    company_size: CompanySize
    description: str | None
    matched_topics: list[TopicBrief]
    match_reason: str


class MatchResults(BaseModel):
    """Paginated match results with metadata."""

    matches: list[JournalistMatch] | list[CompanyMatch]
    total: int
    page: int
    page_size: int
    has_more: bool
