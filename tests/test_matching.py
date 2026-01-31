"""
Tests for deterministic matchmaking.

Covers topic-based matching rules and explainability.
"""

import pytest


class TestMatchingRules:
    """Tests for the matching rule functions."""

    def test_topic_overlap_found(self, client, journalist_with_profile, company_with_profile):
        """When journalist and company share topics, they match."""
        # Both fixtures use the same topic (first one from seeded data)
        # so they should match

        response = client.get(
            "/matches/journalists",
            headers={"Authorization": f"Bearer {company_with_profile['token']}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

        # Find our test journalist in matches
        journalist_id = journalist_with_profile["profile"]["id"]
        match = next(
            (m for m in data["matches"] if m["journalist_id"] == journalist_id), None
        )
        assert match is not None
        assert len(match["matched_topics"]) >= 1
        assert match["match_reason"]  # Explainability required

    def test_no_overlap_no_match(self, client, db_session):
        """When no topic overlap, no match is returned."""
        # Create a journalist with unique topics
        reg_response = client.post(
            "/auth/register",
            json={
                "email": "unique_journalist@example.com",
                "password": "securepass123",
                "user_type": "journalist",
            },
        )
        login_response = client.post(
            "/auth/login",
            json={"email": "unique_journalist@example.com", "password": "securepass123"},
        )
        journalist_token = login_response.json()["access_token"]

        # Get a topic that's different from what we'll use for the company
        topics = client.get("/topics/?category=healthcare").json()
        healthcare_topic_id = topics[0]["id"]

        client.post(
            "/journalists/me",
            json={
                "full_name": "Healthcare Reporter",
                "outlet_name": "Health News",
                "outlet_type": "online",
                "beat_description": "I cover healthcare and pharmaceuticals",
                "topic_ids": [healthcare_topic_id],
            },
            headers={"Authorization": f"Bearer {journalist_token}"},
        )

        # Create a company with different topics (technology)
        reg_response = client.post(
            "/auth/register",
            json={
                "email": "tech_company@example.com",
                "password": "securepass123",
                "user_type": "company",
            },
        )
        login_response = client.post(
            "/auth/login",
            json={"email": "tech_company@example.com", "password": "securepass123"},
        )
        company_token = login_response.json()["access_token"]

        # Get a technology topic (different category)
        tech_topics = client.get("/topics/?category=media").json()
        media_topic_id = tech_topics[0]["id"]

        client.post(
            "/companies/me",
            json={
                "company_name": "Media Streaming Inc",
                "industry": "Media",
                "company_size": "startup",
                "topic_ids": [media_topic_id],
            },
            headers={"Authorization": f"Bearer {company_token}"},
        )

        # Search for matches - healthcare journalist shouldn't match media company
        response = client.get(
            "/matches/journalists",
            headers={"Authorization": f"Bearer {company_token}"},
        )
        assert response.status_code == 200
        data = response.json()

        # The healthcare journalist should NOT be in matches
        healthcare_match = next(
            (m for m in data["matches"] if m["full_name"] == "Healthcare Reporter"), None
        )
        assert healthcare_match is None


class TestJournalistNotAcceptingPitches:
    """Tests for filtering out journalists not accepting pitches."""

    def test_journalist_not_accepting_excluded(self, client, company_with_profile):
        """Journalists not accepting pitches are excluded from matches."""
        # Create a journalist who is NOT accepting pitches
        reg_response = client.post(
            "/auth/register",
            json={
                "email": "busy_journalist@example.com",
                "password": "securepass123",
                "user_type": "journalist",
            },
        )
        login_response = client.post(
            "/auth/login",
            json={"email": "busy_journalist@example.com", "password": "securepass123"},
        )
        journalist_token = login_response.json()["access_token"]

        # Get same topic as company (they use first seeded topic)
        topics = client.get("/topics/").json()
        topic_id = topics[0]["id"]

        profile_response = client.post(
            "/journalists/me",
            json={
                "full_name": "Busy Journalist",
                "outlet_name": "Busy News",
                "outlet_type": "online",
                "beat_description": "I cover tech but I'm too busy right now",
                "is_accepting_pitches": False,  # NOT accepting
                "topic_ids": [topic_id],
            },
            headers={"Authorization": f"Bearer {journalist_token}"},
        )
        assert profile_response.status_code == 201

        # Search for matches
        response = client.get(
            "/matches/journalists",
            headers={"Authorization": f"Bearer {company_with_profile['token']}"},
        )
        assert response.status_code == 200
        data = response.json()

        # Busy journalist should NOT be in matches
        busy_match = next(
            (m for m in data["matches"] if m["full_name"] == "Busy Journalist"), None
        )
        assert busy_match is None


class TestCompanyMatchSearch:
    """Tests for GET /matches/companies (journalist searching)."""

    def test_journalist_finds_matching_companies(
        self, client, journalist_with_profile, company_with_profile
    ):
        """Journalist can find companies matching their topics."""
        response = client.get(
            "/matches/companies",
            headers={"Authorization": f"Bearer {journalist_with_profile['token']}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

        # Find our test company in matches
        company_id = company_with_profile["profile"]["id"]
        match = next(
            (m for m in data["matches"] if m["company_id"] == company_id), None
        )
        assert match is not None
        assert len(match["matched_topics"]) >= 1
        assert match["match_reason"]

    def test_inactive_company_excluded(self, client, journalist_with_profile):
        """Inactive companies are excluded from matches."""
        # Create and deactivate a company
        reg_response = client.post(
            "/auth/register",
            json={
                "email": "inactive_company@example.com",
                "password": "securepass123",
                "user_type": "company",
            },
        )
        login_response = client.post(
            "/auth/login",
            json={"email": "inactive_company@example.com", "password": "securepass123"},
        )
        company_token = login_response.json()["access_token"]

        topics = client.get("/topics/").json()
        topic_id = topics[0]["id"]

        client.post(
            "/companies/me",
            json={
                "company_name": "Inactive Corp",
                "industry": "Tech",
                "company_size": "startup",
                "topic_ids": [topic_id],
            },
            headers={"Authorization": f"Bearer {company_token}"},
        )

        # Deactivate the company
        client.put(
            "/companies/me",
            json={"is_active": False},
            headers={"Authorization": f"Bearer {company_token}"},
        )

        # Journalist searches
        response = client.get(
            "/matches/companies",
            headers={"Authorization": f"Bearer {journalist_with_profile['token']}"},
        )
        assert response.status_code == 200
        data = response.json()

        # Inactive company should NOT be in matches
        inactive_match = next(
            (m for m in data["matches"] if m["company_name"] == "Inactive Corp"), None
        )
        assert inactive_match is None


class TestMatchAuthorization:
    """Tests for match endpoint authorization."""

    def test_journalist_cannot_search_journalists(self, client, journalist_with_profile):
        """Journalists cannot search for other journalists."""
        response = client.get(
            "/matches/journalists",
            headers={"Authorization": f"Bearer {journalist_with_profile['token']}"},
        )
        assert response.status_code == 403

    def test_company_cannot_search_companies(self, client, company_with_profile):
        """Companies cannot search for other companies."""
        response = client.get(
            "/matches/companies",
            headers={"Authorization": f"Bearer {company_with_profile['token']}"},
        )
        assert response.status_code == 403

    def test_no_profile_returns_helpful_error(self, client, company_user):
        """Company without profile gets helpful error."""
        response = client.get(
            "/matches/journalists",
            headers={"Authorization": f"Bearer {company_user['token']}"},
        )
        assert response.status_code == 400
        assert "profile" in response.json()["detail"].lower()


class TestMatchPagination:
    """Tests for match result pagination."""

    def test_pagination_metadata(self, client, company_with_profile, journalist_with_profile):
        """Match results include pagination metadata."""
        response = client.get(
            "/matches/journalists?page=1&page_size=10",
            headers={"Authorization": f"Bearer {company_with_profile['token']}"},
        )
        assert response.status_code == 200
        data = response.json()

        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "has_more" in data
        assert data["page"] == 1
        assert data["page_size"] == 10


class TestMatchExplainability:
    """Tests for match explanation quality."""

    def test_match_reason_includes_names(
        self, client, journalist_with_profile, company_with_profile
    ):
        """Match reason mentions journalist and company names."""
        response = client.get(
            "/matches/journalists",
            headers={"Authorization": f"Bearer {company_with_profile['token']}"},
        )
        data = response.json()

        journalist_id = journalist_with_profile["profile"]["id"]
        match = next(
            (m for m in data["matches"] if m["journalist_id"] == journalist_id), None
        )

        assert match is not None
        reason = match["match_reason"]

        # Reason should mention the journalist name and company name
        assert journalist_with_profile["profile"]["full_name"] in reason
        assert company_with_profile["profile"]["company_name"] in reason

    def test_matched_topics_are_actual_overlap(
        self, client, journalist_with_profile, company_with_profile
    ):
        """Matched topics are genuine overlap between profiles."""
        response = client.get(
            "/matches/journalists",
            headers={"Authorization": f"Bearer {company_with_profile['token']}"},
        )
        data = response.json()

        journalist_id = journalist_with_profile["profile"]["id"]
        match = next(
            (m for m in data["matches"] if m["journalist_id"] == journalist_id), None
        )

        # Get the actual topics from both profiles
        journalist_topics = {t["id"] for t in journalist_with_profile["profile"]["topics"]}
        company_topics = {t["id"] for t in company_with_profile["profile"]["topics"]}

        # Matched topics should be the intersection
        for topic in match["matched_topics"]:
            assert topic["id"] in journalist_topics
            assert topic["id"] in company_topics
