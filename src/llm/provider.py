"""
Abstract LLM provider interface.

Defines the contract for LLM providers. Implementations can be mock,
OpenAI, Anthropic, or any other provider.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class MatchExplanation:
    """Rich explanation of why a match exists."""

    summary: str  # 1-2 sentence overview
    relevance_points: list[str]  # Specific reasons this is a good match
    potential_angles: list[str]  # Story angles the journalist might pursue
    suggested_approach: str  # How the company might reach out
    confidence: str  # "high", "medium", "low"


@dataclass
class PitchAngle:
    """A suggested pitch angle for a match."""

    headline: str  # Attention-grabbing headline
    hook: str  # Opening hook
    why_now: str  # Timeliness/urgency
    key_points: list[str]  # Main talking points


@dataclass
class RiskAssessment:
    """Risk flags for a potential pitch."""

    risk_level: str  # "low", "medium", "high"
    flags: list[str]  # Specific concerns
    recommendations: list[str]  # How to mitigate


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def explain_match(
        self,
        company_name: str,
        company_description: str,
        company_topics: list[str],
        journalist_name: str,
        journalist_beat: str,
        journalist_topics: list[str],
        matched_topics: list[str],
    ) -> MatchExplanation:
        """
        Generate a rich explanation of why this match exists.

        The explanation should help the company understand why this
        journalist is relevant and how to approach them.
        """
        pass

    @abstractmethod
    def suggest_pitch_angles(
        self,
        company_name: str,
        company_description: str,
        journalist_name: str,
        journalist_beat: str,
        matched_topics: list[str],
        num_angles: int = 3,
    ) -> list[PitchAngle]:
        """
        Suggest pitch angles tailored to this journalist.

        Each angle should be specific to the journalist's beat
        and the company's story.
        """
        pass

    @abstractmethod
    def assess_risk(
        self,
        company_name: str,
        company_description: str,
        journalist_name: str,
        journalist_outlet: str,
        journalist_beat: str,
    ) -> RiskAssessment:
        """
        Assess potential risks in pitching this journalist.

        Flags things like beat mismatch, outlet type concerns,
        or timing issues.
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this provider."""
        pass
