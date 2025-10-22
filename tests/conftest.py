"""Pytest configuration and fixtures."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from taskflow.main import app
from taskflow.models.base import Base, get_db_session


# Test database URL
TEST_DATABASE_URL = "sqlite:///./test_taskflow.db"


@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    yield TestSessionLocal()

    # Drop all tables after test
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with overridden database dependency."""

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db_session] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_user(client):
    """Create a sample user for testing."""
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test User",
        },
    )
    return response.json()


@pytest.fixture
def auth_headers(client, sample_user):
    """Get authentication headers for a sample user."""
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
