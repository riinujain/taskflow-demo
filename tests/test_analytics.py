"""Tests for analytics endpoints."""

import pytest
from datetime import datetime, timedelta
from fastapi import status


@pytest.fixture
def project_with_tasks(client, auth_headers):
    """Create a project with multiple tasks."""
    # Create project
    project_response = client.post(
        "/projects",
        headers=auth_headers,
        json={"name": "Analytics Test Project"},
    )
    project_id = project_response.json()["id"]

    # Create tasks with various states
    task_data = [
        {"title": "Completed Task 1", "status": "done", "priority": "high"},
        {"title": "Completed Task 2", "status": "done", "priority": "medium"},
        {"title": "In Progress Task", "status": "in_progress", "priority": "critical"},
        {"title": "Todo Task 1", "status": "todo", "priority": "low"},
        {"title": "Todo Task 2", "status": "todo", "priority": "high"},
        {"title": "Blocked Task", "status": "blocked", "priority": "medium"},
    ]

    task_ids = []
    for task in task_data:
        response = client.post(
            "/tasks",
            headers=auth_headers,
            json={
                "project_id": project_id,
                **task,
            },
        )
        task_ids.append(response.json()["id"])

    return {"project_id": project_id, "task_ids": task_ids}


def test_get_completion_rate(client, auth_headers, project_with_tasks):
    """Test getting completion rate."""
    project_id = project_with_tasks["project_id"]

    response = client.get(
        f"/analytics/completion-rate?project_id={project_id}",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "completion_rate" in data
    assert "period_days" in data


def test_get_velocity(client, auth_headers):
    """Test getting user velocity."""
    response = client.get(
        "/analytics/velocity?days=14",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "velocity" in data
    assert data["period_days"] == 14


def test_get_priority_distribution(client, auth_headers, project_with_tasks):
    """Test getting priority distribution."""
    project_id = project_with_tasks["project_id"]

    response = client.get(
        f"/analytics/priority-distribution?project_id={project_id}",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "critical" in data
    assert "high" in data
    assert "medium" in data
    assert "low" in data
    # We created 1 critical, 2 high, 2 medium, 1 low
    assert data["critical"] == 1
    assert data["high"] == 2


def test_get_status_distribution(client, auth_headers, project_with_tasks):
    """Test getting status distribution."""
    project_id = project_with_tasks["project_id"]

    response = client.get(
        f"/analytics/status-distribution?project_id={project_id}",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "todo" in data
    assert "in_progress" in data
    assert "done" in data
    assert "blocked" in data
    # We created 2 done, 1 in_progress, 2 todo, 1 blocked
    assert data["done"] == 2


def test_get_burndown_data(client, auth_headers, project_with_tasks):
    """Test getting burndown chart data."""
    project_id = project_with_tasks["project_id"]

    response = client.get(
        f"/analytics/burndown/{project_id}?days=7",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "project_id" in data
    assert "data" in data
    assert isinstance(data["data"], list)


def test_get_performance_metrics(client, auth_headers):
    """Test getting performance metrics."""
    response = client.get(
        "/analytics/performance?days=30",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "user_id" in data
    assert "period_days" in data
    assert "completion_rate" in data


def test_get_project_health(client, auth_headers, project_with_tasks):
    """Test getting project health score."""
    project_id = project_with_tasks["project_id"]

    response = client.get(
        f"/analytics/project-health/{project_id}",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "health_score" in data
    assert 0 <= data["health_score"] <= 100


def test_get_task_trends(client, auth_headers):
    """Test getting task trends."""
    response = client.get(
        "/analytics/trends?days=14",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "period_days" in data
    assert "trends" in data
    assert "created" in data["trends"]
    assert "completed" in data["trends"]


def test_get_team_metrics(client, auth_headers, project_with_tasks):
    """Test getting team metrics."""
    project_id = project_with_tasks["project_id"]

    response = client.get(
        f"/analytics/team-metrics/{project_id}",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "project_id" in data
    assert "total_tasks" in data


def test_get_time_to_completion(client, auth_headers):
    """Test getting time-to-completion stats."""
    response = client.get(
        "/analytics/time-to-completion",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "stats" in data
    assert "min_days" in data["stats"]
    assert "max_days" in data["stats"]


def test_analytics_access_control(client, auth_headers):
    """Test that users can't access other users' projects."""
    # This would need a second user to properly test
    response = client.get(
        "/analytics/project-health/9999",  # Non-existent project
        headers=auth_headers,
    )

    # Should return 403 or 404
    assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]


def test_completion_rate_with_empty_project(client, auth_headers):
    """Test completion rate with project that has no tasks."""
    # Create empty project
    project_response = client.post(
        "/projects",
        headers=auth_headers,
        json={"name": "Empty Project"},
    )
    project_id = project_response.json()["id"]

    response = client.get(
        f"/analytics/completion-rate?project_id={project_id}",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # Should handle empty project gracefully
    assert data["completion_rate"] == 0.0
