"""Tests for task endpoints."""

import pytest
from datetime import datetime, timedelta
from fastapi import status


@pytest.fixture
def project_id(client, auth_headers):
    """Create a test project and return its ID."""
    response = client.post(
        "/projects",
        headers=auth_headers,
        json={"name": "Test Project for Tasks"},
    )
    return response.json()["id"]


def test_create_task(client, auth_headers, project_id):
    """Test creating a new task."""
    response = client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "project_id": project_id,
            "title": "Test Task",
            "description": "A test task",
            "priority": "high",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["priority"] == "high"


def test_list_tasks(client, auth_headers, project_id):
    """Test listing tasks."""
    # Create a task
    client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "project_id": project_id,
            "title": "Task 1",
        },
    )

    # List tasks
    response = client.get(
        f"/tasks?project_id={project_id}",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_task(client, auth_headers, project_id):
    """Test getting a specific task."""
    # Create task
    create_response = client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "project_id": project_id,
            "title": "Get Task Test",
        },
    )
    task_id = create_response.json()["id"]

    # Get task
    response = client.get(f"/tasks/{task_id}", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Get Task Test"


def test_update_task(client, auth_headers, project_id):
    """Test updating a task."""
    # Create task
    create_response = client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "project_id": project_id,
            "title": "Original Title",
            "status": "todo",
        },
    )
    task_id = create_response.json()["id"]

    # Update task
    response = client.patch(
        f"/tasks/{task_id}",
        headers=auth_headers,
        json={
            "title": "Updated Title",
            "status": "in_progress",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "in_progress"


def test_delete_task(client, auth_headers, project_id):
    """Test deleting a task."""
    # Create task
    create_response = client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "project_id": project_id,
            "title": "To Delete",
        },
    )
    task_id = create_response.json()["id"]

    # Delete task
    response = client.delete(f"/tasks/{task_id}", headers=auth_headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_get_task_summary(client, auth_headers, project_id):
    """Test getting task summary."""
    # Create task
    create_response = client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "project_id": project_id,
            "title": "Summary Test",
            "priority": "high",
        },
    )
    task_id = create_response.json()["id"]

    # Get summary
    response = client.get(f"/tasks/{task_id}/summary", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "title" in data
    assert "status" in data


def test_create_task_with_due_date(client, auth_headers, project_id):
    """Test creating task with due date."""
    due_date = (datetime.utcnow() + timedelta(days=7)).isoformat()

    response = client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "project_id": project_id,
            "title": "Task with Due Date",
            "due_date": due_date,
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["due_date"] is not None
