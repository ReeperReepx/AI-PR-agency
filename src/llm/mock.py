"""
Mock LLM provider for testing and development.

Returns deterministic, template-based responses without
requiring any API keys or network access.
"""

from src.llm.provider import (
    LLMProvider,
    MatchExplanation,
    PitchAngle,
    RiskAssessment,
)


class MockLLMProvider(LLMProvider):
    """
    Mock provider that generates template-based responses.

    Useful for testing and development without API costs.
    """

    @property
    def provider_name(self) -> str:
        return "mock"

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
        """Generate a template-based match explanation."""
        topic_str = ", ".join(matched_topics) if matched_topics else "related areas"

        return MatchExplanation(
            summary=f"{journalist_name} covers {topic_str}, which aligns with {company_name}'s focus areas.",
            relevance_points=[
                f"Shared interest in {matched_topics[0]}" if matched_topics else "Complementary focus areas",
                f"{journalist_name}'s beat ({journalist_beat[:50]}...) relates to {company_name}'s work",
                f"Both active in the {matched_topics[0] if matched_topics else 'technology'} space",
            ],
            potential_angles=[
                f"Industry trend piece featuring {company_name}'s approach",
                f"Expert commentary on {matched_topics[0] if matched_topics else 'market'} developments",
                f"Case study highlighting {company_name}'s impact",
            ],
            suggested_approach=f"Reference {journalist_name}'s recent coverage of {matched_topics[0] if matched_topics else 'the industry'} and offer a unique perspective from {company_name}.",
            confidence="high" if len(matched_topics) >= 2 else "medium" if matched_topics else "low",
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
        """Generate template-based pitch angles."""
        topic = matched_topics[0] if matched_topics else "the industry"

        angles = [
            PitchAngle(
                headline=f"How {company_name} is Redefining {topic.title()}",
                hook=f"While the {topic} landscape shifts, {company_name} has taken a contrarian approach that's yielding results.",
                why_now=f"Recent developments in {topic} make this story timely.",
                key_points=[
                    f"{company_name}'s unique approach to {topic}",
                    "Measurable outcomes and data points",
                    "Expert insights on industry direction",
                ],
            ),
            PitchAngle(
                headline=f"The {topic.title()} Trend That's Flying Under the Radar",
                hook=f"Industry insiders are watching a quiet transformation in {topic}, and {company_name} is at the center.",
                why_now="Market indicators suggest this trend is about to accelerate.",
                key_points=[
                    f"Emerging patterns in {topic}",
                    f"{company_name}'s early-mover advantage",
                    "Implications for the broader market",
                ],
            ),
            PitchAngle(
                headline=f"Inside {company_name}'s {topic.title()} Strategy",
                hook=f"In a crowded market, {company_name}'s approach to {topic} stands out for its clarity and results.",
                why_now=f"As companies navigate {topic} challenges, this strategy is gaining attention.",
                key_points=[
                    "Strategic framework and decision-making",
                    "Results and metrics",
                    "Lessons for other organizations",
                ],
            ),
        ]

        return angles[:num_angles]

    def assess_risk(
        self,
        company_name: str,
        company_description: str,
        journalist_name: str,
        journalist_outlet: str,
        journalist_beat: str,
    ) -> RiskAssessment:
        """Generate a template-based risk assessment."""
        # Simple heuristics for mock risk assessment
        flags = []
        recommendations = []
        risk_level = "low"

        # Check for potential mismatches (simple heuristics)
        beat_lower = journalist_beat.lower()
        desc_lower = company_description.lower() if company_description else ""

        # Flag if beat seems very specific
        if len(journalist_beat) > 100:
            flags.append(f"{journalist_name} has a very specific beat - ensure your pitch is directly relevant")
            recommendations.append("Tailor your pitch narrowly to their stated interests")
            risk_level = "medium"

        # Generic recommendations
        if not flags:
            flags.append("No significant risk factors identified")

        recommendations.extend([
            f"Research {journalist_name}'s recent articles before reaching out",
            f"Ensure your pitch aligns with {journalist_outlet}'s editorial style",
            "Prepare supporting data and expert availability",
        ])

        return RiskAssessment(
            risk_level=risk_level,
            flags=flags,
            recommendations=recommendations[:3],
        )
