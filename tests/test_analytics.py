"""
Tests for analytics module (Phase 6).

Tests cover user metrics, platform metrics, and access control.
"""

import pytest


class TestUserMetrics:
    """Tests for user engagement metrics."""

    def test_get_my_metrics_journalist(
        self, client, journalist_with_profile
    ):
        """Journalist can get their metrics."""
        response = client.get(
            "/analytics/me",
            headers={"Authorization": f"Bearer {journalist_with_profile['token']}"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["user_type"] == "journalist"
        assert data["profile_complete"] is True
        assert data["topic_count"] >= 1
        assert "matches_found" in data
        assert "feedback_given" in data

    def test_get_my_metrics_company(
        self, client, company_with_profile
    ):
        """Company can get their metrics."""
        response = client.get(
            "/analytics/me",
            headers={"Authorization": f"Bearer {company_with_profile['token']}"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["user_type"] == "company"
        assert data["profile_complete"] is True

    def test_metrics_show_incomplete_profile(
        self, client, journalist_user
    ):
        """Metrics correctly show incomplete profile."""
        response = client.get(
            "/analytics/me",
            headers={"Authorization": f"Bearer {journalist_user['token']}"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["profile_complete"] is False
        assert data["topic_count"] == 0

    def test_metrics_requires_authentication(self, client):
        """Metrics endpoint requires authentication."""
        response = client.get("/analytics/me")
        assert response.status_code in (401, 403)


class TestPlatformMetrics:
    """Tests for platform-wide metrics."""

    def test_platform_metrics_requires_admin(
        self, client, company_with_profile
    ):
        """Only admins can view platform metrics."""
        response = client.get(
            "/analytics/platform",
            headers={"Authorization": f"Bearer {company_with_profile['token']}"},
        )
        assert response.status_code == 403

    def test_platform_metrics_accessible_by_admin(
        self, client, admin_user
    ):
        """Admins can view platform metrics."""
        response = client.get(
            "/analytics/platform",
            headers={"Authorization": f"Bearer {admin_user['token']}"},
        )

        assert response.status_code == 200
        data = response.json()

        # Check all expected fields
        assert "total_users" in data
        assert "journalist_count" in data
        assert "company_count" in data
        assert "admin_count" in data
        assert "profiles_complete" in data
        assert "total_topics" in data
        assert "total_feedback" in data
        assert "helpfulness_rate" in data

    def test_platform_metrics_counts_are_accurate(
        self, client, admin_user, journalist_with_profile, company_with_profile
    ):
        """Platform metrics accurately count users and profiles."""
        response = client.get(
            "/analytics/platform",
            headers={"Authorization": f"Bearer {admin_user['token']}"},
        )

        data = response.json()

        # Should have at least the test users
        assert data["total_users"] >= 3  # admin, journalist, company
        assert data["journalist_count"] >= 1
        assert data["company_count"] >= 1
        assert data["admin_count"] >= 1
        assert data["profiles_complete"] >= 2  # journalist + company


class TestMetricsIntegration:
    """Tests for metrics integration with other features."""

    def test_feedback_updates_metrics(
        self, client, company_with_profile, journalist_with_profile
    ):
        """Submitting feedback updates user metrics."""
        headers = {"Authorization": f"Bearer {company_with_profile['token']}"}

        # Get initial metrics
        initial = client.get("/analytics/me", headers=headers).json()
        initial_feedback = initial["feedback_given"]

        # Submit feedback
        client.post(
            "/feedback/",
            json={
                "journalist_profile_id": journalist_with_profile["profile"]["id"],
                "company_profile_id": company_with_profile["profile"]["id"],
                "feedback_type": "helpful",
            },
            headers=headers,
        )

        # Get updated metrics
        updated = client.get("/analytics/me", headers=headers).json()
        assert updated["feedback_given"] == initial_feedback + 1

    def test_match_count_reflects_topic_overlap(
        self, client, journalist_with_profile, company_with_profile
    ):
        """Match count in metrics reflects actual topic-based matches."""
        # Both profiles have at least one topic, so should have matches
        response = client.get(
            "/analytics/me",
            headers={"Authorization": f"Bearer {journalist_with_profile['token']}"},
        )

        data = response.json()
        # Should find at least the company_with_profile as a match
        # (they share the same topic from the fixture)
        assert data["matches_found"] >= 1
