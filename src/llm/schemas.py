"""
Pydantic schemas for LLM-assisted features.

These schemas define the API response formats for LLM-generated content.
"""

from pydantic import BaseModel, ConfigDict


class MatchExplanationResponse(BaseModel):
    """API response for match explanation."""

    model_config = ConfigDict(from_attributes=True)

    summary: str
    relevance_points: list[str]
    potential_angles: list[str]
    suggested_approach: str
    confidence: str
    provider: str  # Which LLM provider generated this


class PitchAngleResponse(BaseModel):
    """API response for a single pitch angle."""

    model_config = ConfigDict(from_attributes=True)

    headline: str
    hook: str
    why_now: str
    key_points: list[str]


class PitchAnglesResponse(BaseModel):
    """API response for pitch angle suggestions."""

    model_config = ConfigDict(from_attributes=True)

    angles: list[PitchAngleResponse]
    provider: str
    disclaimer: str = "These are AI-generated suggestions. Review and customize before use."


class RiskAssessmentResponse(BaseModel):
    """API response for risk assessment."""

    model_config = ConfigDict(from_attributes=True)

    risk_level: str
    flags: list[str]
    recommendations: list[str]
    provider: str
    disclaimer: str = "This is an AI advisory assessment. Use human judgment for final decisions."


class LLMInsightsResponse(BaseModel):
    """Combined LLM insights for a match."""

    model_config = ConfigDict(from_attributes=True)

    explanation: MatchExplanationResponse
    pitch_angles: PitchAnglesResponse
    risk_assessment: RiskAssessmentResponse
