"""Tests for report endpoints.

This module includes a FRAGILE TEST that depends on exact string formatting.
"""

import pytest
from datetime import datetime, timedelta
from fastapi import status


@pytest.fixture
def setup_test_data(client, auth_headers):
    """Set up test data for report tests."""
    # Create project
    project_response = client.post(
        "/projects",
        headers=auth_headers,
        json={"name": "Report Test Project"},
    )
    project_id = project_response.json()["id"]

    # Create some tasks
    task_ids = []
    for i in range(3):
        task_response = client.post(
            "/tasks",
            headers=auth_headers,
            json={
                "project_id": project_id,
                "title": f"Task {i + 1}",
                "status": "todo" if i < 2 else "done",
                "priority": "high" if i == 0 else "medium",
            },
        )
        task_ids.append(task_response.json()["id"])

    return {"project_id": project_id, "task_ids": task_ids}


def test_get_daily_summary(client, auth_headers):
    """Test getting daily summary report."""
    response = client.get("/reports/daily-summary", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "completed_count" in data
    assert "pending_count" in data
    assert "overdue_count" in data


def test_get_project_report(client, auth_headers, setup_test_data):
    """Test getting project report."""
    project_id = setup_test_data["project_id"]

    response = client.get(f"/reports/project/{project_id}", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["project_id"] == project_id
    assert "total_tasks" in data
    assert "completion_rate" in data


def test_get_overdue_report(client, auth_headers):
    """Test getting overdue tasks report."""
    response = client.get("/reports/overdue", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_overdue" in data
    assert "by_priority" in data


def test_get_productivity_report(client, auth_headers):
    """Test getting productivity report."""
    response = client.get("/reports/productivity?days=7", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "tasks_completed" in data
    assert "period_days" in data
    assert data["period_days"] == 7


def test_get_system_overview(client, auth_headers):
    """Test getting system overview."""
    response = client.get("/reports/system-overview", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_projects" in data
    assert "total_tasks" in data


# FRAGILE TEST - Depends on exact string formatting from build_task_summary_string
def test_get_task_verbose_summary_format(client, auth_headers, setup_test_data):
    """Test verbose task summary has exact expected format.

    This test is DELIBERATELY FRAGILE - it depends on exact string formatting
    from the report_service.build_task_summary_string() function.
    Any change to that function's output format will break this test.
    """
    task_id = setup_test_data["task_ids"][0]  # High priority task

    response = client.get(
        f"/reports/task/{task_id}/verbose-summary",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "summary" in data

    summary_text = data["summary"]

    # FRAGILE ASSERTIONS - Depend on exact string format
    assert summary_text.startswith(f"Task #{task_id}:")
    assert "⬆️ HIGH PRIORITY" in summary_text  # Exact emoji and text
    assert "📋 Status: TODO" in summary_text  # Exact format
    assert "👤 Not assigned" in summary_text  # Exact text

    # This will break if the format changes even slightly
    lines = summary_text.split("\n")
    assert len(lines) >= 5  # Expects at least 5 lines

    # Expecting exact line positions (VERY FRAGILE)
    # This assumes the function always outputs in the same order
    assert "Task #" in lines[0]  # First line has task ID
    # Note: This test will break easily with any format changes


# Another fragile test variant
def test_verbose_summary_priority_critical(client, auth_headers, setup_test_data):
    """Test that critical priority shows exact warning format.

    Another FRAGILE test checking exact string format.
    """
    project_id = setup_test_data["project_id"]

    # Create a critical priority task
    create_response = client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "project_id": project_id,
            "title": "Critical Task",
            "priority": "critical",
        },
    )
    task_id = create_response.json()["id"]

    response = client.get(
        f"/reports/task/{task_id}/verbose-summary",
        headers=auth_headers,
    )

    summary = response.json()["summary"]

    # FRAGILE: Expects exact emoji and text
    assert "⚠️ CRITICAL PRIORITY ⚠️" in summary
    assert "This task requires immediate attention!" in summary


# REDUNDANT TEST - This tests the same functionality as test_get_daily_summary
# but via a different code path (POST /reports/daily_summary vs GET /reports/daily-summary)
def test_create_daily_summary_redundant(client, auth_headers, setup_test_data):
    """Test creating daily summary via POST endpoint.

    This is REDUNDANT with test_get_daily_summary - both test daily summary functionality
    but this uses the POST endpoint that returns text_summary + metrics,
    while the other uses GET endpoint. The underlying service call is nearly identical.
    """
    project_id = setup_test_data["project_id"]

    response = client.post(
        "/reports/daily_summary",
        headers=auth_headers,
        json={
            "project_id": project_id,
            "include_overdue": True,
            "include_assignees": True,
            "compact": False,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # These assertions test the same underlying functionality as test_get_daily_summary
    assert "metrics" in data
    assert "text_summary" in data
    assert data["project_id"] == project_id

    # Check metrics structure (redundant with other tests)
    metrics = data["metrics"]
    assert "total_tasks" in metrics
    assert "todo_count" in metrics
    assert "done_count" in metrics
    assert "completion_rate" in metrics

    # The text_summary is just a different format of the same data
    # This is testing the same business logic via a different presentation layer
