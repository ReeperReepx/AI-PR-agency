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


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with the test database."""
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def journalist_user(client):
    """Create and return a journalist user with token."""
    response = client.post(
        "/auth/register",
        json={
            "email": "journalist@example.com",
            "password": "securepass123",
            "user_type": "journalist",
        },
    )
    user = response.json()

    login_response = client.post(
        "/auth/login",
        json={"email": "journalist@example.com", "password": "securepass123"},
    )
    token = login_response.json()["access_token"]

    return {"user": user, "token": token}


@pytest.fixture
def company_user(client):
    """Create and return a company user with token."""
    response = client.post(
        "/auth/register",
        json={
            "email": "company@example.com",
            "password": "securepass123",
            "user_type": "company",
        },
    )
    user = response.json()

    login_response = client.post(
        "/auth/login",
        json={"email": "company@example.com", "password": "securepass123"},
    )
    token = login_response.json()["access_token"]

    return {"user": user, "token": token}


@pytest.fixture
def admin_user(client):
    """Create and return an admin user with token."""
    response = client.post(
        "/auth/register",
        json={
            "email": "admin@example.com",
            "password": "securepass123",
            "user_type": "admin",
        },
    )
    user = response.json()

    login_response = client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "securepass123"},
    )
    token = login_response.json()["access_token"]

    return {"user": user, "token": token}
