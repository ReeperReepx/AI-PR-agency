"""
Tests for authentication endpoints.

Covers registration, login, and token validation.
"""


class TestRegistration:
    """Tests for POST /auth/register"""

    def test_register_journalist(self, client):
        """Journalists can register successfully."""
        response = client.post(
            "/auth/register",
            json={
                "email": "new.journalist@example.com",
                "password": "securepass123",
                "user_type": "journalist",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new.journalist@example.com"
        assert data["user_type"] == "journalist"
        assert data["is_active"] is True
        assert "id" in data
        assert "password" not in data
        assert "password_hash" not in data

    def test_register_company(self, client):
        """Companies can register successfully."""
        response = client.post(
            "/auth/register",
            json={
                "email": "company@startup.com",
                "password": "securepass123",
                "user_type": "company",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["user_type"] == "company"

    def test_register_admin(self, client):
        """Admins can register successfully."""
        response = client.post(
            "/auth/register",
            json={
                "email": "admin@platform.com",
                "password": "securepass123",
                "user_type": "admin",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["user_type"] == "admin"

    def test_register_duplicate_email_fails(self, client):
        """Registration with duplicate email is rejected."""
        client.post(
            "/auth/register",
            json={
                "email": "existing@example.com",
                "password": "securepass123",
                "user_type": "journalist",
            },
        )

        response = client.post(
            "/auth/register",
            json={
                "email": "existing@example.com",
                "password": "differentpass",
                "user_type": "company",
            },
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email_fails(self, client):
        """Registration with invalid email format is rejected."""
        response = client.post(
            "/auth/register",
            json={
                "email": "not-an-email",
                "password": "securepass123",
                "user_type": "journalist",
            },
        )
        assert response.status_code == 422

    def test_register_invalid_user_type_fails(self, client):
        """Registration with invalid user type is rejected."""
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "securepass123",
                "user_type": "hacker",
            },
        )
        assert response.status_code == 422


class TestLogin:
    """Tests for POST /auth/login"""

    def test_login_success(self, client):
        """Valid credentials return an access token."""
        client.post(
            "/auth/register",
            json={
                "email": "login.test@example.com",
                "password": "securepass123",
                "user_type": "journalist",
            },
        )

        response = client.post(
            "/auth/login",
            json={"email": "login.test@example.com", "password": "securepass123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password_fails(self, client):
        """Wrong password is rejected."""
        client.post(
            "/auth/register",
            json={
                "email": "password.test@example.com",
                "password": "correctpassword",
                "user_type": "journalist",
            },
        )

        response = client.post(
            "/auth/login",
            json={"email": "password.test@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_login_nonexistent_user_fails(self, client):
        """Login with non-existent email is rejected."""
        response = client.post(
            "/auth/login",
            json={"email": "nobody@example.com", "password": "anypassword"},
        )
        assert response.status_code == 401

    def test_login_returns_valid_token(self, client):
        """Token from login can be used to access protected endpoints."""
        client.post(
            "/auth/register",
            json={
                "email": "token.test@example.com",
                "password": "securepass123",
                "user_type": "journalist",
            },
        )

        login_response = client.post(
            "/auth/login",
            json={"email": "token.test@example.com", "password": "securepass123"},
        )
        token = login_response.json()["access_token"]

        me_response = client.get(
            "/users/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == 200
        assert me_response.json()["email"] == "token.test@example.com"
