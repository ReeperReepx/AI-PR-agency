"""
Tests for topic endpoints.

Topics are publicly readable but admin-only for creation.
"""


class TestListTopics:
    """Tests for GET /topics/"""

    def test_list_topics_unauthenticated(self, client):
        """Topics can be listed without authentication."""
        response = client.get("/topics/")
        assert response.status_code == 200
        topics = response.json()
        # Seeded topics should exist
        assert len(topics) > 0

    def test_list_topics_has_seeded_data(self, client):
        """Seeded topics include expected entries."""
        response = client.get("/topics/")
        topics = response.json()
        names = [t["name"] for t in topics]
        assert "artificial-intelligence" in names
        assert "startups" in names
        assert "climate-tech" in names

    def test_list_topics_filter_by_category(self, client):
        """Topics can be filtered by category."""
        response = client.get("/topics/?category=technology")
        assert response.status_code == 200
        topics = response.json()
        assert len(topics) > 0
        for topic in topics:
            assert topic["category"] == "technology"


class TestCreateTopic:
    """Tests for POST /topics/"""

    def test_create_topic_as_admin(self, client, admin_user):
        """Admin can create a new topic."""
        response = client.post(
            "/topics/",
            json={
                "name": "test-topic",
                "display_name": "Test Topic",
                "category": "test",
            },
            headers={"Authorization": f"Bearer {admin_user['token']}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test-topic"
        assert data["display_name"] == "Test Topic"
        assert data["category"] == "test"

    def test_create_topic_as_journalist_fails(self, client, journalist_user):
        """Non-admin cannot create topics."""
        response = client.post(
            "/topics/",
            json={
                "name": "another-topic",
                "display_name": "Another Topic",
                "category": "test",
            },
            headers={"Authorization": f"Bearer {journalist_user['token']}"},
        )
        assert response.status_code == 403

    def test_create_duplicate_topic_fails(self, client, admin_user):
        """Cannot create topic with existing name."""
        response = client.post(
            "/topics/",
            json={
                "name": "artificial-intelligence",
                "display_name": "AI Duplicate",
                "category": "technology",
            },
            headers={"Authorization": f"Bearer {admin_user['token']}"},
        )
        assert response.status_code == 409

    def test_create_topic_invalid_name_fails(self, client, admin_user):
        """Topic name must be slug format."""
        response = client.post(
            "/topics/",
            json={
                "name": "Invalid Topic Name",  # spaces not allowed
                "display_name": "Invalid",
                "category": "test",
            },
            headers={"Authorization": f"Bearer {admin_user['token']}"},
        )
        assert response.status_code == 422  # validation error
