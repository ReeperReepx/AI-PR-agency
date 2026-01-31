"""
Tests for feedback module (Phase 6).

Tests cover feedback submission, statistics, and access control.
"""

import pytest


class TestFeedbackSubmission:
    """Tests for submitting match feedback."""

    def test_submit_feedback_creates_record(
        self, client, company_with_profile, journalist_with_profile, db_session
    ):
        """User can submit feedback on a match."""
        from src.feedback.models import MatchFeedback

        response = client.post(
            "/feedback/",
            json={
                "journalist_profile_id": journalist_with_profile["profile"]["id"],
                "company_profile_id": company_with_profile["profile"]["id"],
                "feedback_type": "helpful",
                "notes": "Great match, very relevant to our industry",
            },
            headers={"Authorization": f"Bearer {company_with_profile['token']}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["feedback_type"] == "helpful"
        assert data["notes"] == "Great match, very relevant to our industry"

        # Verify in database
        feedback = db_session.query(MatchFeedback).filter_by(id=data["id"]).first()
        assert feedback is not None

    def test_submit_feedback_updates_existing(
        self, client, company_with_profile, journalist_with_profile
    ):
        """Submitting feedback again updates the existing record."""
        profile_ids = {
            "journalist_profile_id": journalist_with_profile["profile"]["id"],
            "company_profile_id": company_with_profile["profile"]["id"],
        }
        headers = {"Authorization": f"Bearer {company_with_profile['token']}"}

        # First feedback
        response1 = client.post(
            "/feedback/",
            json={**profile_ids, "feedback_type": "helpful"},
            headers=headers,
        )
        assert response1.status_code == 201
        first_id = response1.json()["id"]

        # Update feedback
        response2 = client.post(
            "/feedback/",
            json={**profile_ids, "feedback_type": "not_helpful"},
            headers=headers,
        )
        assert response2.status_code == 201
        assert response2.json()["id"] == first_id  # Same record updated
        assert response2.json()["feedback_type"] == "not_helpful"

    def test_feedback_requires_authentication(
        self, client, company_with_profile, journalist_with_profile
    ):
        """Feedback submission requires authentication."""
        response = client.post(
            "/feedback/",
            json={
                "journalist_profile_id": journalist_with_profile["profile"]["id"],
                "company_profile_id": company_with_profile["profile"]["id"],
                "feedback_type": "helpful",
            },
        )
        assert response.status_code in (401, 403)

    def test_feedback_validates_journalist_exists(
        self, client, company_with_profile
    ):
        """Feedback fails if journalist doesn't exist."""
        response = client.post(
            "/feedback/",
            json={
                "journalist_profile_id": "nonexistent-id",
                "company_profile_id": company_with_profile["profile"]["id"],
                "feedback_type": "helpful",
            },
            headers={"Authorization": f"Bearer {company_with_profile['token']}"},
        )
        assert response.status_code == 404
        assert "journalist" in response.json()["detail"].lower()

    def test_feedback_validates_company_exists(
        self, client, journalist_with_profile
    ):
        """Feedback fails if company doesn't exist."""
        response = client.post(
            "/feedback/",
            json={
                "journalist_profile_id": journalist_with_profile["profile"]["id"],
                "company_profile_id": "nonexistent-id",
                "feedback_type": "helpful",
            },
            headers={"Authorization": f"Bearer {journalist_with_profile['token']}"},
        )
        assert response.status_code == 404
        assert "company" in response.json()["detail"].lower()


class TestFeedbackTypes:
    """Tests for different feedback types."""

    def test_all_feedback_types_accepted(
        self, client, company_with_profile, journalist_with_profile
    ):
        """All valid feedback types are accepted."""
        headers = {"Authorization": f"Bearer {company_with_profile['token']}"}
        profile_ids = {
            "journalist_profile_id": journalist_with_profile["profile"]["id"],
            "company_profile_id": company_with_profile["profile"]["id"],
        }

        for feedback_type in ["helpful", "not_helpful", "contacted", "successful"]:
            response = client.post(
                "/feedback/",
                json={**profile_ids, "feedback_type": feedback_type},
                headers=headers,
            )
            assert response.status_code == 201
            assert response.json()["feedback_type"] == feedback_type


class TestFeedbackRetrieval:
    """Tests for retrieving feedback."""

    def test_get_my_feedback(
        self, client, company_with_profile, journalist_with_profile
    ):
        """User can see their feedback history."""
        headers = {"Authorization": f"Bearer {company_with_profile['token']}"}

        # Submit some feedback
        client.post(
            "/feedback/",
            json={
                "journalist_profile_id": journalist_with_profile["profile"]["id"],
                "company_profile_id": company_with_profile["profile"]["id"],
                "feedback_type": "helpful",
            },
            headers=headers,
        )

        # Get feedback summary
        response = client.get("/feedback/me", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert "stats" in data
        assert "recent_feedback" in data
        assert data["stats"]["total_feedback"] >= 1

    def test_feedback_stats_calculated_correctly(
        self, client, company_with_profile, journalist_with_profile
    ):
        """Feedback stats are calculated correctly."""
        headers = {"Authorization": f"Bearer {company_with_profile['token']}"}
        profile_ids = {
            "journalist_profile_id": journalist_with_profile["profile"]["id"],
            "company_profile_id": company_with_profile["profile"]["id"],
        }

        # Submit helpful feedback
        client.post(
            "/feedback/",
            json={**profile_ids, "feedback_type": "helpful"},
            headers=headers,
        )

        response = client.get("/feedback/me", headers=headers)
        stats = response.json()["stats"]

        assert stats["helpful_count"] >= 1
        assert stats["helpfulness_rate"] > 0


class TestPlatformStats:
    """Tests for platform-wide feedback statistics."""

    def test_platform_stats_requires_admin(
        self, client, company_with_profile
    ):
        """Only admins can view platform stats."""
        response = client.get(
            "/feedback/stats",
            headers={"Authorization": f"Bearer {company_with_profile['token']}"},
        )
        assert response.status_code == 403

    def test_platform_stats_accessible_by_admin(
        self, client, admin_user
    ):
        """Admins can view platform stats."""
        response = client.get(
            "/feedback/stats",
            headers={"Authorization": f"Bearer {admin_user['token']}"},
        )
        assert response.status_code == 200

        data = response.json()
        assert "total_feedback" in data
        assert "helpfulness_rate" in data
