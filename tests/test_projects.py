"""Tests for project endpoints."""

import pytest
from fastapi import status


def test_create_project(client, auth_headers):
    """Test creating a new project."""
    response = client.post(
        "/projects",
        headers=auth_headers,
        json={
            "name": "Test Project",
            "description": "A test project",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "A test project"
    assert "id" in data


def test_list_projects(client, auth_headers):
    """Test listing user's projects."""
    # Create a project first
    client.post(
        "/projects",
        headers=auth_headers,
        json={"name": "Project 1"},
    )

    response = client.get("/projects", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_project(client, auth_headers):
    """Test getting a specific project."""
    # Create project
    create_response = client.post(
        "/projects",
        headers=auth_headers,
        json={"name": "Test Project"},
    )
    project_id = create_response.json()["id"]

    # Get project
    response = client.get(f"/projects/{project_id}", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == "Test Project"


def test_update_project(client, auth_headers):
    """Test updating a project."""
    # Create project
    create_response = client.post(
        "/projects",
        headers=auth_headers,
        json={"name": "Original Name"},
    )
    project_id = create_response.json()["id"]

    # Update project
    response = client.patch(
        f"/projects/{project_id}",
        headers=auth_headers,
        json={"name": "Updated Name"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Name"


def test_delete_project(client, auth_headers):
    """Test deleting a project."""
    # Create project
    create_response = client.post(
        "/projects",
        headers=auth_headers,
        json={"name": "To Delete"},
    )
    project_id = create_response.json()["id"]

    # Delete project
    response = client.delete(f"/projects/{project_id}", headers=auth_headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify deleted
    get_response = client.get(f"/projects/{project_id}", headers=auth_headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_get_project_stats(client, auth_headers):
    """Test getting project statistics."""
    # Create project
    create_response = client.post(
        "/projects",
        headers=auth_headers,
        json={"name": "Stats Test Project"},
    )
    project_id = create_response.json()["id"]

    # Get stats
    response = client.get(f"/projects/{project_id}/stats", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_tasks" in data
    assert "completed_tasks" in data
