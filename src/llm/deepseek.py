"""
DeepSeek LLM provider implementation.

Uses the OpenAI-compatible API with DeepSeek's endpoint.
"""

import json
import logging

from openai import OpenAI

from src.core.config import settings
from src.llm.provider import (
    LLMProvider,
    MatchExplanation,
    PitchAngle,
    RiskAssessment,
)

logger = logging.getLogger(__name__)


class DeepSeekProvider(LLMProvider):
    """DeepSeek LLM provider using OpenAI-compatible API."""

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )
        self.model = settings.deepseek_model

    @property
    def provider_name(self) -> str:
        return "deepseek"

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Make a call to the DeepSeek API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"DeepSeek API error: {e}")
            raise

    def _parse_json_response(self, response: str, default: dict) -> dict:
        """Parse JSON from LLM response, handling markdown code blocks."""
        # Strip markdown code blocks if present
        text = response.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM JSON response: {e}")
            return default

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
        """Generate a rich explanation of why this match exists."""
        default = {
            "summary": f"{company_name} aligns with {journalist_name}'s coverage of {journalist_beat}.",
            "relevance_points": [
                f"Shared interest in {', '.join(matched_topics) if matched_topics else 'related topics'}",
                f"{journalist_name} covers {journalist_beat}",
                f"{company_name}'s story fits this beat",
            ],
            "potential_angles": [
                "Industry trend story",
                "Company innovation angle",
            ],
            "suggested_approach": "Personalize your pitch based on their recent coverage.",
            "confidence": "medium",
        }

        system_prompt = """You are an expert PR matchmaking assistant. Your job is to explain
why a company and journalist are a good match for each other. Be specific, actionable, and
focus on editorial relevance. Always respond in valid JSON format."""

        user_prompt = f"""Analyze this match and explain why it's relevant:

COMPANY:
- Name: {company_name}
- Description: {company_description}
- Topics: {', '.join(company_topics)}

JOURNALIST:
- Name: {journalist_name}
- Beat: {journalist_beat}
- Topics: {', '.join(journalist_topics)}

MATCHED TOPICS: {', '.join(matched_topics) if matched_topics else 'None (similarity-based match)'}

Respond with JSON in this exact format:
{{
    "summary": "1-2 sentence overview of why this is a good match",
    "relevance_points": ["point 1", "point 2", "point 3"],
    "potential_angles": ["angle 1", "angle 2"],
    "suggested_approach": "How the company should approach this journalist",
    "confidence": "high/medium/low"
}}"""

        try:
            response = self._call_llm(system_prompt, user_prompt)
            data = self._parse_json_response(response, default)
        except Exception as e:
            logger.warning(f"DeepSeek API unavailable, using fallback: {e}")
            data = default

        return MatchExplanation(
            summary=data.get("summary", ""),
            relevance_points=data.get("relevance_points", []),
            potential_angles=data.get("potential_angles", []),
            suggested_approach=data.get("suggested_approach", ""),
            confidence=data.get("confidence", "medium"),
        )

    def suggest_pitch_angles(
        self,
        company_name: str,
        company_description: str,
        journalist_name: str,
        journalist_beat: str,
        matched_topics: list[str],
        num_angles: int = 3,
    ) -> list[PitchAngle]:
        """Suggest pitch angles tailored to this journalist."""
        system_prompt = """You are an expert PR strategist. Generate compelling pitch angles
that would resonate with a specific journalist based on their beat. Each angle should be
newsworthy and timely. Always respond in valid JSON format."""

        user_prompt = f"""Generate {num_angles} pitch angles for this match:

COMPANY:
- Name: {company_name}
- Description: {company_description}

JOURNALIST:
- Name: {journalist_name}
- Beat: {journalist_beat}

MATCHED TOPICS: {', '.join(matched_topics) if matched_topics else 'General relevance'}

Respond with JSON array in this exact format:
[
    {{
        "headline": "Attention-grabbing headline",
        "hook": "Opening sentence that captures interest",
        "why_now": "Why this story is timely",
        "key_points": ["point 1", "point 2", "point 3"]
    }}
]

Generate exactly {num_angles} angles."""

        try:
            response = self._call_llm(system_prompt, user_prompt)
            data = self._parse_json_response(response, [])
        except Exception as e:
            logger.warning(f"DeepSeek API unavailable, using fallback: {e}")
            data = []

        angles = []
        for i, item in enumerate(data[:num_angles]):
            angles.append(PitchAngle(
                headline=item.get("headline", f"Story Angle {i+1}"),
                hook=item.get("hook", ""),
                why_now=item.get("why_now", "Timely industry development"),
                key_points=item.get("key_points", []),
            ))

        # Ensure we return the requested number with intelligent fallbacks
        fallback_angles = [
            PitchAngle(
                headline=f"{company_name}: Industry Innovation Story",
                hook=f"How {company_name} is reshaping {journalist_beat}.",
                why_now="Market dynamics are shifting rapidly.",
                key_points=["Unique approach", "Market impact", "Future outlook"],
            ),
            PitchAngle(
                headline=f"The Future of {journalist_beat}",
                hook=f"{company_name}'s perspective on where the industry is heading.",
                why_now="Industry evolution accelerating.",
                key_points=["Trend analysis", "Expert insights", "Actionable takeaways"],
            ),
            PitchAngle(
                headline=f"Behind the Scenes at {company_name}",
                hook=f"An inside look at how {company_name} operates.",
                why_now="Growing interest in company culture and operations.",
                key_points=["Company culture", "Innovation process", "Leadership vision"],
            ),
        ]

        while len(angles) < num_angles:
            idx = len(angles)
            if idx < len(fallback_angles):
                angles.append(fallback_angles[idx])
            else:
                angles.append(PitchAngle(
                    headline=f"Alternative Angle {len(angles)+1}",
                    hook="Consider this perspective...",
                    why_now="Industry timing",
                    key_points=["Key insight"],
                ))

        return angles

    def assess_risk(
        self,
        company_name: str,
        company_description: str,
        journalist_name: str,
        journalist_outlet: str,
        journalist_beat: str,
    ) -> RiskAssessment:
        """Assess potential risks in pitching this journalist."""
        default = {
            "risk_level": "low",
            "flags": [
                "Ensure pitch aligns with journalist's current coverage focus",
                "Research their recent articles before reaching out",
            ],
            "recommendations": [
                "Personalize your pitch based on their recent work",
                f"Reference specific {journalist_outlet} articles",
                "Keep initial outreach concise and newsworthy",
            ],
        }

        system_prompt = """You are a PR risk assessment expert. Analyze potential risks
in pitching a journalist and provide actionable recommendations. Be balanced - not
every pitch is high risk. Always respond in valid JSON format."""

        user_prompt = f"""Assess the risk of pitching this journalist:

COMPANY:
- Name: {company_name}
- Description: {company_description}

JOURNALIST:
- Name: {journalist_name}
- Outlet: {journalist_outlet}
- Beat: {journalist_beat}

Consider:
- Beat alignment
- Outlet type and reach
- Potential negative angles
- Timing considerations

Respond with JSON in this exact format:
{{
    "risk_level": "low/medium/high",
    "flags": ["flag 1", "flag 2"],
    "recommendations": ["recommendation 1", "recommendation 2"]
}}"""

        try:
            response = self._call_llm(system_prompt, user_prompt)
            data = self._parse_json_response(response, default)
        except Exception as e:
            logger.warning(f"DeepSeek API unavailable, using fallback: {e}")
            data = default

        return RiskAssessment(
            risk_level=data.get("risk_level", "low"),
            flags=data.get("flags", []),
            recommendations=data.get("recommendations", []),
        )
