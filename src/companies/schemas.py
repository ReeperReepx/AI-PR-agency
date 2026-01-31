"""
Pydantic schemas for company profile validation.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from src.companies.models import CompanySize
from src.topics.schemas import TopicBrief


class CompanyProfileCreate(BaseModel):
    """Schema for creating a company profile."""

    company_name: str = Field(..., min_length=2, max_length=200)
    description: str | None = Field(None, max_length=2000)
    website: str | None = Field(None, max_length=500)
    industry: str = Field(..., min_length=2, max_length=100)
    company_size: CompanySize
    founded_year: int | None = Field(None, ge=1800, le=2100)
    headquarters: str | None = Field(None, max_length=200)
    topic_ids: list[str] = Field(default_factory=list, max_length=10)


class CompanyProfileUpdate(BaseModel):
    """Schema for updating a company profile. All fields optional."""

    company_name: str | None = Field(None, min_length=2, max_length=200)
    description: str | None = Field(None, max_length=2000)
    website: str | None = Field(None, max_length=500)
    industry: str | None = Field(None, min_length=2, max_length=100)
    company_size: CompanySize | None = None
    founded_year: int | None = Field(None, ge=1800, le=2100)
    headquarters: str | None = Field(None, max_length=200)
    is_active: bool | None = None
    topic_ids: list[str] | None = Field(None, max_length=10)


class CompanyProfileResponse(BaseModel):
    """Full profile returned to the company themselves."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    company_name: str
    description: str | None
    website: str | None
    industry: str
    company_size: CompanySize
    founded_year: int | None
    headquarters: str | None
    is_active: bool
    topics: list[TopicBrief]
    created_at: datetime
    updated_at: datetime


class CompanyProfilePublic(BaseModel):
    """
    Profile visible to journalists.

    Journalists see this when a company wants to pitch them.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    company_name: str
    description: str | None
    website: str | None
    industry: str
    company_size: CompanySize
    founded_year: int | None
    headquarters: str | None
    topics: list[TopicBrief]
