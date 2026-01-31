"""
Tests for company profile endpoints.
"""


class TestCompanyProfileCreate:
    """Tests for POST /companies/me"""

    def test_create_profile_as_company(self, client, company_user):
        """Company can create their profile."""
        # Get a topic ID from seeded data
        topics_response = client.get("/topics/")
        topic_id = topics_response.json()[0]["id"]

        response = client.post(
            "/companies/me",
            json={
                "company_name": "TechStartup Inc",
                "description": "We build AI-powered tools for developers",
                "website": "https://techstartup.example.com",
                "industry": "Software",
                "company_size": "startup",
                "founded_year": 2022,
                "headquarters": "San Francisco, CA",
                "topic_ids": [topic_id],
            },
            headers={"Authorization": f"Bearer {company_user['token']}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["company_name"] == "TechStartup Inc"
        assert data["company_size"] == "startup"
        assert data["is_active"] is True
        assert len(data["topics"]) == 1

    def test_create_profile_as_journalist_fails(self, client, journalist_user):
        """Journalist cannot create company profile."""
        response = client.post(
            "/companies/me",
            json={
                "company_name": "Fake Company",
                "industry": "Fake",
                "company_size": "startup",
            },
            headers={"Authorization": f"Bearer {journalist_user['token']}"},
        )
        assert response.status_code == 403

    def test_create_duplicate_profile_fails(self, client, company_with_profile):
        """Cannot create profile if one already exists."""
        response = client.post(
            "/companies/me",
            json={
                "company_name": "Another Company",
                "industry": "Tech",
                "company_size": "medium",
            },
            headers={"Authorization": f"Bearer {company_with_profile['token']}"},
        )
        assert response.status_code == 409


class TestCompanyProfileGet:
    """Tests for GET /companies/me"""

    def test_get_own_profile(self, client, company_with_profile):
        """Company can get their own profile."""
        response = client.get(
            "/companies/me",
            headers={"Authorization": f"Bearer {company_with_profile['token']}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["company_name"] == "Test Company"
        assert "topics" in data
        assert "is_active" in data  # Full profile includes is_active

    def test_get_profile_when_none_exists(self, client, company_user):
        """Returns 404 if no profile exists."""
        response = client.get(
            "/companies/me",
            headers={"Authorization": f"Bearer {company_user['token']}"},
        )
        assert response.status_code == 404


class TestCompanyProfileUpdate:
    """Tests for PUT /companies/me"""

    def test_update_profile(self, client, company_with_profile):
        """Company can update their profile."""
        response = client.put(
            "/companies/me",
            json={
                "description": "Updated company description",
                "company_size": "medium",
            },
            headers={"Authorization": f"Bearer {company_with_profile['token']}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated company description"
        assert data["company_size"] == "medium"
        # Other fields unchanged
        assert data["company_name"] == "Test Company"

    def test_deactivate_profile(self, client, company_with_profile):
        """Company can deactivate their profile."""
        response = client.put(
            "/companies/me",
            json={"is_active": False},
            headers={"Authorization": f"Bearer {company_with_profile['token']}"},
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is False


class TestCompanyProfilePublic:
    """Tests for GET /companies/{profile_id}"""

    def test_journalist_can_view_company(self, client, journalist_user, company_with_profile):
        """Journalist can view company's public profile."""
        profile_id = company_with_profile["profile"]["id"]
        response = client.get(
            f"/companies/{profile_id}",
            headers={"Authorization": f"Bearer {journalist_user['token']}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "company_name" in data
        assert "industry" in data
        assert "topics" in data
        # Public view shouldn't include user_id or is_active
        assert "user_id" not in data
        assert "is_active" not in data

    def test_view_nonexistent_profile(self, client, journalist_user):
        """Returns 404 for non-existent profile."""
        response = client.get(
            "/companies/nonexistent-id",
            headers={"Authorization": f"Bearer {journalist_user['token']}"},
        )
        assert response.status_code == 404
