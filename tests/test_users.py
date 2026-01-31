"""
Tests for user endpoints.

Covers user retrieval and authorization.
"""


class TestGetCurrentUser:
    """Tests for GET /users/me"""

    def test_get_me_authenticated(self, client, journalist_user):
        """Authenticated user can get their own details."""
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {journalist_user['token']}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "journalist@example.com"
        assert data["user_type"] == "journalist"

    def test_get_me_unauthenticated_fails(self, client):
        """Unauthenticated request is rejected."""
        response = client.get("/users/me")
        # HTTPBearer returns 401 when no Authorization header present
        assert response.status_code in (401, 403)

    def test_get_me_invalid_token_fails(self, client):
        """Invalid token is rejected."""
        response = client.get(
            "/users/me", headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == 401


class TestGetUser:
    """Tests for GET /users/{user_id}"""

    def test_get_own_user(self, client, journalist_user):
        """User can view their own profile."""
        user_id = journalist_user["user"]["id"]
        response = client.get(
            f"/users/{user_id}",
            headers={"Authorization": f"Bearer {journalist_user['token']}"},
        )
        assert response.status_code == 200
        assert response.json()["id"] == user_id

    def test_get_other_user_as_non_admin_fails(self, client, journalist_user, company_user):
        """Non-admin cannot view another user's profile."""
        other_user_id = company_user["user"]["id"]
        response = client.get(
            f"/users/{other_user_id}",
            headers={"Authorization": f"Bearer {journalist_user['token']}"},
        )
        assert response.status_code == 403

    def test_get_other_user_as_admin_succeeds(self, client, admin_user, journalist_user):
        """Admin can view any user's profile."""
        other_user_id = journalist_user["user"]["id"]
        response = client.get(
            f"/users/{other_user_id}",
            headers={"Authorization": f"Bearer {admin_user['token']}"},
        )
        assert response.status_code == 200
        assert response.json()["id"] == other_user_id

    def test_get_nonexistent_user_fails(self, client, admin_user):
        """Requesting non-existent user returns 404."""
        response = client.get(
            "/users/nonexistent-uuid",
            headers={"Authorization": f"Bearer {admin_user['token']}"},
        )
        assert response.status_code == 404


class TestListUsers:
    """Tests for GET /users/"""

    def test_list_users_as_admin(self, client, admin_user, journalist_user, company_user):
        """Admin can list all users."""
        response = client.get(
            "/users/",
            headers={"Authorization": f"Bearer {admin_user['token']}"},
        )
        assert response.status_code == 200
        users = response.json()
        assert len(users) == 3  # admin, journalist, company
        emails = [u["email"] for u in users]
        assert "admin@example.com" in emails
        assert "journalist@example.com" in emails
        assert "company@example.com" in emails

    def test_list_users_as_non_admin_fails(self, client, journalist_user):
        """Non-admin cannot list users."""
        response = client.get(
            "/users/",
            headers={"Authorization": f"Bearer {journalist_user['token']}"},
        )
        assert response.status_code == 403
        assert "admin" in response.json()["detail"].lower()

    def test_list_users_unauthenticated_fails(self, client):
        """Unauthenticated request to list users is rejected."""
        response = client.get("/users/")
        # HTTPBearer returns 401 when no Authorization header present
        assert response.status_code in (401, 403)


class TestHealthCheck:
    """Tests for GET /health"""

    def test_health_check(self, client):
        """Health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "phase" in data
