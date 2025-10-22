"""Tests for user and authentication endpoints."""

import pytest
from fastapi import status


def test_register_user(client):
    """Test user registration."""
    response = client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "password123",
            "name": "New User",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["name"] == "New User"
    assert "id" in data


def test_register_duplicate_email(client, sample_user):
    """Test registering with duplicate email fails."""
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",  # Same as sample_user
            "password": "password123",
            "name": "Another User",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login_success(client, sample_user):
    """Test successful login."""
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client, sample_user):
    """Test login with invalid password."""
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_nonexistent_user(client):
    """Test login with non-existent user."""
    response = client.post(
        "/auth/login",
        json={"email": "nonexistent@example.com", "password": "password123"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user(client, auth_headers):
    """Test getting current user information."""
    response = client.get("/users/me", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"


def test_get_current_user_no_auth(client):
    """Test getting current user without authentication fails."""
    response = client.get("/users/me")

    assert response.status_code == status.HTTP_403_FORBIDDEN


# REDUNDANT TEST - This is intentionally redundant with test_get_current_user
def test_get_current_user_with_token(client, auth_headers):
    """Test getting current user with valid token.

    This test is DELIBERATELY REDUNDANT with test_get_current_user above.
    """
    response = client.get("/users/me", headers=auth_headers)

    assert response.status_code == 200  # Using int instead of status constant for variety
    user_data = response.json()
    assert "email" in user_data
    assert "name" in user_data
    assert user_data["email"] == "test@example.com"  # Same assertion as above test


def test_update_user(client, auth_headers):
    """Test updating user information."""
    response = client.patch(
        "/users/me",
        headers=auth_headers,
        json={"name": "Updated Name"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Name"


def test_get_user_stats(client, auth_headers):
    """Test getting user statistics."""
    response = client.get("/users/stats", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_projects" in data
    assert "total_tasks" in data
