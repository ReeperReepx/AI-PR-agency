"""
Test fixtures for the Editorial PR Matchmaking platform.

Uses an in-memory SQLite database for test isolation.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.database import Base, get_db
from src.main import app
from src.topics.service import seed_topics


# In-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency with test database."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Helper Functions ---


def create_test_user(client: TestClient, user_type: str) -> dict:
    """
    Create a test user of the specified type and return user data with token.

    Args:
        client: Test client instance
        user_type: One of "journalist", "company", or "admin"

    Returns:
        Dict with "user" data and "token" for authentication
    """
    email = f"{user_type}@example.com"
    password = "securepass123"

    response = client.post(
        "/auth/register",
        json={"email": email, "password": password, "user_type": user_type},
    )
    user = response.json()

    login_response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    token = login_response.json()["access_token"]

    return {"user": user, "token": token}


# --- Database Fixtures ---


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_topics(db)
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with the test database."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# --- User Fixtures ---


@pytest.fixture
def journalist_user(client):
    """Create and return a journalist user with token."""
    return create_test_user(client, "journalist")


@pytest.fixture
def company_user(client):
    """Create and return a company user with token."""
    return create_test_user(client, "company")


@pytest.fixture
def admin_user(client):
    """Create and return an admin user with token."""
    return create_test_user(client, "admin")


@pytest.fixture
def journalist_with_profile(client, journalist_user):
    """Create a journalist user with a complete profile."""
    # Get a topic ID
    topics_response = client.get("/topics/")
    topic_id = topics_response.json()[0]["id"]

    profile_response = client.post(
        "/journalists/me",
        json={
            "full_name": "Test Journalist",
            "bio": "A test journalist for testing",
            "outlet_name": "Test News",
            "outlet_type": "online",
            "beat_description": "Testing and quality assurance in software",
            "min_pitch_notice_days": 3,
            "preferred_contact_method": "email",
            "is_accepting_pitches": True,
            "topic_ids": [topic_id],
        },
        headers={"Authorization": f"Bearer {journalist_user['token']}"},
    )
    profile = profile_response.json()

    return {
        "user": journalist_user["user"],
        "token": journalist_user["token"],
        "profile": profile,
    }


@pytest.fixture
def company_with_profile(client, company_user):
    """Create a company user with a complete profile."""
    # Get a topic ID
    topics_response = client.get("/topics/")
    topic_id = topics_response.json()[0]["id"]

    profile_response = client.post(
        "/companies/me",
        json={
            "company_name": "Test Company",
            "description": "A test company for testing",
            "website": "https://test.example.com",
            "industry": "Technology",
            "company_size": "startup",
            "founded_year": 2020,
            "headquarters": "Test City",
            "topic_ids": [topic_id],
        },
        headers={"Authorization": f"Bearer {company_user['token']}"},
    )
    profile = profile_response.json()

    return {
        "user": company_user["user"],
        "token": company_user["token"],
        "profile": profile,
    }
