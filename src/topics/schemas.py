"""
Pydantic schemas for topic validation.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TopicCreate(BaseModel):
    """Schema for creating a new topic. Admin only."""

    name: str = Field(..., min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    display_name: str = Field(..., min_length=2, max_length=100)
    category: str = Field(..., min_length=2, max_length=50)


class TopicResponse(BaseModel):
    """Schema for topic data returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    display_name: str
    category: str
    created_at: datetime


class TopicBrief(BaseModel):
    """Minimal topic info for embedding in profiles."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    display_name: str
