"""
Tests for LLM-assisted reasoning (Phase 5).

Tests cover the provider interface, mock provider, and insight endpoints.
AI advises, never decides.
"""

import pytest


class TestLLMProvider:
    """Tests for LLM provider interface and mock implementation."""

    def test_mock_provider_has_correct_name(self):
        """Mock provider identifies itself correctly."""
        from src.llm.mock import MockLLMProvider

        provider = MockLLMProvider()
        assert provider.provider_name == "mock"

    def test_explain_match_returns_all_fields(self):
        """Match explanation includes all required fields."""
        from src.llm.mock import MockLLMProvider

        provider = MockLLMProvider()
        explanation = provider.explain_match(
            company_name="TechCorp",
            company_description="AI-powered analytics",
            company_topics=["AI/ML", "Data Analytics"],
            journalist_name="Jane Reporter",
            journalist_beat="Technology startups and AI",
            journalist_topics=["AI/ML", "Startups"],
            matched_topics=["AI/ML"],
        )

        assert explanation.summary
        assert len(explanation.relevance_points) > 0
        assert len(explanation.potential_angles) > 0
        assert explanation.suggested_approach
        assert explanation.confidence in ("high", "medium", "low")

    def test_suggest_pitch_angles_returns_requested_count(self):
        """Pitch angle suggestions return the requested number."""
        from src.llm.mock import MockLLMProvider

        provider = MockLLMProvider()

        for num in [1, 2, 3]:
            angles = provider.suggest_pitch_angles(
                company_name="TechCorp",
                company_description="AI-powered analytics",
                journalist_name="Jane Reporter",
                journalist_beat="Technology startups",
                matched_topics=["AI/ML"],
                num_angles=num,
            )
            assert len(angles) == num

    def test_pitch_angle_has_all_fields(self):
        """Each pitch angle includes all required fields."""
        from src.llm.mock import MockLLMProvider

        provider = MockLLMProvider()
        angles = provider.suggest_pitch_angles(
            company_name="TechCorp",
            company_description="AI-powered analytics",
            journalist_name="Jane Reporter",
            journalist_beat="Technology startups",
            matched_topics=["AI/ML"],
            num_angles=1,
        )

        angle = angles[0]
        assert angle.headline
        assert angle.hook
        assert angle.why_now
        assert len(angle.key_points) > 0

    def test_risk_assessment_returns_valid_level(self):
        """Risk assessment returns a valid risk level."""
        from src.llm.mock import MockLLMProvider

        provider = MockLLMProvider()
        risk = provider.assess_risk(
            company_name="TechCorp",
            company_description="AI-powered analytics",
            journalist_name="Jane Reporter",
            journalist_outlet="Tech News Daily",
            journalist_beat="Technology startups",
        )

        assert risk.risk_level in ("low", "medium", "high")
        assert len(risk.flags) > 0
        assert len(risk.recommendations) > 0


class TestLLMService:
    """Tests for LLM service layer."""

    def test_get_llm_provider_returns_mock(self):
        """Service returns mock provider by default."""
        from src.llm.service import get_llm_provider

        provider = get_llm_provider()
        assert provider.provider_name == "mock"

    def test_provider_is_cached(self):
        """Provider is cached for efficiency."""
        from src.llm.service import get_llm_provider

        provider1 = get_llm_provider()
        provider2 = get_llm_provider()
        assert provider1 is provider2


class TestJournalistInsightsEndpoint:
    """Tests for /matches/insights/journalist/{id} endpoint."""

    def test_company_can_get_journalist_insights(
        self, client, company_with_profile, journalist_with_profile
    ):
        """Company can get LLM insights for a journalist."""
        journalist_id = journalist_with_profile["profile"]["id"]

        response = client.get(
            f"/matches/insights/journalist/{journalist_id}",
            headers={"Authorization": f"Bearer {company_with_profile['token']}"},
        )

        assert response.status_code == 200
        data = response.json()

        # Check explanation
        assert "explanation" in data
        assert data["explanation"]["summary"]
        assert data["explanation"]["provider"] == "mock"

        # Check pitch angles
        assert "pitch_angles" in data
        assert "angles" in data["pitch_angles"]
        assert data["pitch_angles"]["disclaimer"]

        # Check risk assessment
        assert "risk_assessment" in data
        assert data["risk_assessment"]["risk_level"] in ("low", "medium", "high")
        assert data["risk_assessment"]["disclaimer"]

    def test_journalist_cannot_get_journalist_insights(
        self, client, journalist_with_profile
    ):
        """Journalists cannot get journalist insights (only companies can)."""
        response = client.get(
            f"/matches/insights/journalist/{journalist_with_profile['profile']['id']}",
            headers={"Authorization": f"Bearer {journalist_with_profile['token']}"},
        )

        assert response.status_code == 403

    def test_insights_require_company_profile(self, client, company_user, journalist_with_profile):
        """Company must have a profile to get insights."""
        response = client.get(
            f"/matches/insights/journalist/{journalist_with_profile['profile']['id']}",
            headers={"Authorization": f"Bearer {company_user['token']}"},
        )

        assert response.status_code == 400
        assert "profile" in response.json()["detail"].lower()

    def test_insights_for_nonexistent_journalist(self, client, company_with_profile):
        """Returns 404 for non-existent journalist."""
        response = client.get(
            "/matches/insights/journalist/nonexistent-id",
            headers={"Authorization": f"Bearer {company_with_profile['token']}"},
        )

        assert response.status_code == 404


class TestCompanyInsightsEndpoint:
    """Tests for /matches/insights/company/{id} endpoint."""

    def test_journalist_can_get_company_insights(
        self, client, journalist_with_profile, company_with_profile
    ):
        """Journalist can get LLM insights for a company."""
        company_id = company_with_profile["profile"]["id"]

        response = client.get(
            f"/matches/insights/company/{company_id}",
            headers={"Authorization": f"Bearer {journalist_with_profile['token']}"},
        )

        assert response.status_code == 200
        data = response.json()

        # Check all sections present
        assert "explanation" in data
        assert "pitch_angles" in data
        assert "risk_assessment" in data

        # Provider should be identified
        assert data["explanation"]["provider"] == "mock"

    def test_company_cannot_get_company_insights(self, client, company_with_profile):
        """Companies cannot get company insights (only journalists can)."""
        response = client.get(
            f"/matches/insights/company/{company_with_profile['profile']['id']}",
            headers={"Authorization": f"Bearer {company_with_profile['token']}"},
        )

        assert response.status_code == 403

    def test_insights_require_journalist_profile(self, client, journalist_user, company_with_profile):
        """Journalist must have a profile to get insights."""
        response = client.get(
            f"/matches/insights/company/{company_with_profile['profile']['id']}",
            headers={"Authorization": f"Bearer {journalist_user['token']}"},
        )

        assert response.status_code == 400
        assert "profile" in response.json()["detail"].lower()

    def test_insights_for_nonexistent_company(self, client, journalist_with_profile):
        """Returns 404 for non-existent company."""
        response = client.get(
            "/matches/insights/company/nonexistent-id",
            headers={"Authorization": f"Bearer {journalist_with_profile['token']}"},
        )

        assert response.status_code == 404


class TestInsightsContent:
    """Tests for the quality and structure of LLM insights."""

    def test_explanation_includes_company_name(
        self, client, company_with_profile, journalist_with_profile
    ):
        """Explanation mentions the company name."""
        response = client.get(
            f"/matches/insights/journalist/{journalist_with_profile['profile']['id']}",
            headers={"Authorization": f"Bearer {company_with_profile['token']}"},
        )

        data = response.json()
        explanation = data["explanation"]

        # Company name should appear in the explanation
        assert "Test Company" in explanation["summary"] or any(
            "Test Company" in point for point in explanation["relevance_points"]
        )

    def test_pitch_angles_are_distinct(
        self, client, company_with_profile, journalist_with_profile
    ):
        """Each pitch angle has a unique headline."""
        response = client.get(
            f"/matches/insights/journalist/{journalist_with_profile['profile']['id']}",
            headers={"Authorization": f"Bearer {company_with_profile['token']}"},
        )

        data = response.json()
        angles = data["pitch_angles"]["angles"]

        headlines = [a["headline"] for a in angles]
        assert len(headlines) == len(set(headlines)), "Headlines should be unique"

    def test_risk_assessment_has_recommendations(
        self, client, company_with_profile, journalist_with_profile
    ):
        """Risk assessment always includes recommendations."""
        response = client.get(
            f"/matches/insights/journalist/{journalist_with_profile['profile']['id']}",
            headers={"Authorization": f"Bearer {company_with_profile['token']}"},
        )

        data = response.json()
        risk = data["risk_assessment"]

        assert len(risk["recommendations"]) > 0
        assert all(isinstance(r, str) for r in risk["recommendations"])
