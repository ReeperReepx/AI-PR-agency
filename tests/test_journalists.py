"""
Tests for journalist profile endpoints.
"""

import pytest


class TestJournalistProfileCreate:
    """Tests for POST /journalists/me"""

    def test_create_profile_as_journalist(self, client, journalist_user, db_session):
        """Journalist can create their profile."""
        # Get a topic ID from seeded data
        topics_response = client.get("/topics/")
        topic_id = topics_response.json()[0]["id"]

        response = client.post(
            "/journalists/me",
            json={
                "full_name": "Jane Reporter",
                "bio": "Tech journalist covering AI and startups",
                "outlet_name": "Tech Daily",
                "outlet_type": "online",
                "beat_description": "I cover artificial intelligence, machine learning, and early-stage startups in Silicon Valley.",
                "min_pitch_notice_days": 5,
                "preferred_contact_method": "email",
                "is_accepting_pitches": True,
                "topic_ids": [topic_id],
            },
            headers={"Authorization": f"Bearer {journalist_user['token']}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == "Jane Reporter"
        assert data["outlet_name"] == "Tech Daily"
        assert data["outlet_type"] == "online"
        assert len(data["topics"]) == 1

    def test_create_profile_as_company_fails(self, client, company_user):
        """Company cannot create journalist profile."""
        response = client.post(
            "/journalists/me",
            json={
                "full_name": "Fake Journalist",
                "outlet_name": "Fake News",
                "outlet_type": "online",
                "beat_description": "This should not work",
            },
            headers={"Authorization": f"Bearer {company_user['token']}"},
        )
        assert response.status_code == 403

    def test_create_duplicate_profile_fails(self, client, journalist_with_profile):
        """Cannot create profile if one already exists."""
        response = client.post(
            "/journalists/me",
            json={
                "full_name": "Another Name",
                "outlet_name": "Another Outlet",
                "outlet_type": "newspaper",
                "beat_description": "This should fail because profile exists",
            },
            headers={"Authorization": f"Bearer {journalist_with_profile['token']}"},
        )
        assert response.status_code == 409


class TestJournalistProfileGet:
    """Tests for GET /journalists/me"""

    def test_get_own_profile(self, client, journalist_with_profile):
        """Journalist can get their own profile."""
        response = client.get(
            "/journalists/me",
            headers={"Authorization": f"Bearer {journalist_with_profile['token']}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Test Journalist"
        assert "topics" in data

    def test_get_profile_when_none_exists(self, client, journalist_user):
        """Returns 404 if no profile exists."""
        response = client.get(
            "/journalists/me",
            headers={"Authorization": f"Bearer {journalist_user['token']}"},
        )
        assert response.status_code == 404


class TestJournalistProfileUpdate:
    """Tests for PUT /journalists/me"""

    def test_update_profile(self, client, journalist_with_profile):
        """Journalist can update their profile."""
        response = client.put(
            "/journalists/me",
            json={
                "bio": "Updated bio with new information",
                "is_accepting_pitches": False,
            },
            headers={"Authorization": f"Bearer {journalist_with_profile['token']}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["bio"] == "Updated bio with new information"
        assert data["is_accepting_pitches"] is False
        # Other fields unchanged
        assert data["full_name"] == "Test Journalist"

    def test_update_topics(self, client, journalist_with_profile):
        """Journalist can update their topics."""
        # Get different topic IDs
        topics_response = client.get("/topics/?category=business")
        new_topic_ids = [t["id"] for t in topics_response.json()[:2]]

        response = client.put(
            "/journalists/me",
            json={"topic_ids": new_topic_ids},
            headers={"Authorization": f"Bearer {journalist_with_profile['token']}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["topics"]) == 2


class TestJournalistProfilePublic:
    """Tests for GET /journalists/{profile_id}"""

    def test_company_can_view_journalist(self, client, company_user, journalist_with_profile):
        """Company can view journalist's public profile."""
        profile_id = journalist_with_profile["profile"]["id"]
        response = client.get(
            f"/journalists/{profile_id}",
            headers={"Authorization": f"Bearer {company_user['token']}"},
        )
        assert response.status_code == 200
        data = response.json()
        # Public profile has limited fields
        assert "full_name" in data
        assert "outlet_name" in data
        assert "topics" in data
        # Should NOT include private preferences
        assert "min_pitch_notice_days" not in data
        assert "is_accepting_pitches" not in data

    def test_view_nonexistent_profile(self, client, company_user):
        """Returns 404 for non-existent profile."""
        response = client.get(
            "/journalists/nonexistent-id",
            headers={"Authorization": f"Bearer {company_user['token']}"},
        )
        assert response.status_code == 404
