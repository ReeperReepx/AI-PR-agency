"""
Pydantic schemas for journalist profile validation.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.journalists.models import ContactMethod, OutletType
from src.topics.schemas import TopicBrief


class JournalistProfileCreate(BaseModel):
    """Schema for creating a journalist profile."""

    full_name: str = Field(..., min_length=2, max_length=200)
    bio: str | None = Field(None, max_length=2000)
    outlet_name: str = Field(..., min_length=2, max_length=200)
    outlet_type: OutletType
    beat_description: str = Field(..., min_length=10, max_length=2000)
    min_pitch_notice_days: int = Field(default=3, ge=0, le=90)
    preferred_contact_method: ContactMethod = ContactMethod.email
    is_accepting_pitches: bool = True
    topic_ids: list[str] = Field(default_factory=list, max_length=10)


class JournalistProfileUpdate(BaseModel):
    """Schema for updating a journalist profile. All fields optional."""

    full_name: str | None = Field(None, min_length=2, max_length=200)
    bio: str | None = Field(None, max_length=2000)
    outlet_name: str | None = Field(None, min_length=2, max_length=200)
    outlet_type: OutletType | None = None
    beat_description: str | None = Field(None, min_length=10, max_length=2000)
    min_pitch_notice_days: int | None = Field(None, ge=0, le=90)
    preferred_contact_method: ContactMethod | None = None
    is_accepting_pitches: bool | None = None
    topic_ids: list[str] | None = Field(None, max_length=10)


class JournalistProfileResponse(BaseModel):
    """Full profile returned to the journalist themselves."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    full_name: str
    bio: str | None
    outlet_name: str
    outlet_type: OutletType
    beat_description: str
    min_pitch_notice_days: int
    preferred_contact_method: ContactMethod
    is_accepting_pitches: bool
    topics: list[TopicBrief]
    created_at: datetime
    updated_at: datetime


class JournalistProfilePublic(BaseModel):
    """
    Limited profile visible to companies.

    Does not expose contact preferences or accepting status.
    Companies see this when browsing — actual pitching requires matching.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    full_name: str
    bio: str | None
    outlet_name: str
    outlet_type: OutletType
    beat_description: str
    topics: list[TopicBrief]
