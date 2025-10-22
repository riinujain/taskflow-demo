"""Reports and analytics API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from taskflow.models.base import get_db_session
from taskflow.services.report_service import ReportService
from taskflow.services.task_service import TaskService
from taskflow.api.users_api import get_current_user

router = APIRouter()


class DailySummaryRequest(BaseModel):
    project_id: int
    include_overdue: bool = True
    include_assignees: bool = True
    compact: bool = False


@router.get("/daily-summary")
def get_daily_summary(
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
):
    """Get daily summary for current user."""
    report_service = ReportService(db)
    summary = report_service.generate_daily_summary(current_user.id)  # type: ignore
    return summary


@router.post("/daily_summary")
def create_daily_summary(
    request: DailySummaryRequest,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
):
    # No docstring - inconsistent style
    from taskflow.services.project_service import ProjectService

    project_service = ProjectService(db)

    # Check access
    if not project_service.check_user_access(request.project_id, current_user.id):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this project",
        )

    report_service = ReportService(db)

    # Get the text blob using the long conditional chain function
    text_summary = report_service.build_daily_summary(
        project_id=request.project_id,
        include_overdue=request.include_overdue,
        include_assignees=request.include_assignees,
        compact=request.compact,
    )

    # Also get simple metrics
    project_report = report_service.generate_project_report(request.project_id)

    if not project_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Return both text blob and metrics - manually built dict for inconsistency
    return {
        "text_summary": text_summary,
        "metrics": {
            "total_tasks": project_report["total_tasks"],
            "todo_count": project_report["todo_count"],
            "in_progress_count": project_report["in_progress_count"],
            "done_count": project_report["done_count"],
            "blocked_count": project_report["blocked_count"],
            "completion_rate": project_report["completion_rate"],
        },
        "project_id": request.project_id,
        "project_name": project_report["project_name"],
    }


@router.get("/project/{project_id}")
def get_project_report(
    project_id: int,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
):
    """Get comprehensive project report."""
    from taskflow.services.project_service import ProjectService

    project_service = ProjectService(db)

    # Check access
    if not project_service.check_user_access(project_id, current_user.id):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    report_service = ReportService(db)
    report = report_service.generate_project_report(project_id)

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return report


@router.get("/overdue")
def get_overdue_report(
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
):
    """Get report of all overdue tasks."""
    report_service = ReportService(db)
    return report_service.get_overdue_report()


@router.get("/productivity")
def get_productivity_report(
    days: int = Query(default=7, ge=1, le=90),
    current_user: Annotated[object, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db_session)] = None,
):
    """Get productivity report for current user."""
    report_service = ReportService(db)
    return report_service.get_user_productivity_report(
        user_id=current_user.id,  # type: ignore
        days=days,
    )


@router.get("/system-overview")
def get_system_overview(
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
):
    """Get overall system statistics.

    Note: In production, this should be admin-only.
    """
    report_service = ReportService(db)
    return report_service.get_system_overview()


@router.get("/task/{task_id}/verbose-summary")
def get_task_verbose_summary(
    task_id: int,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
):
    """Get verbose task summary using the long conditional chain function."""
    task_service = TaskService(db)
    task = task_service.get_task_by_id(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Check access
    from taskflow.services.project_service import ProjectService

    project_service = ProjectService(db)
    if not project_service.check_user_access(task.project_id, current_user.id):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Use the deliberately long function
    report_service = ReportService(db)
    summary_text = report_service.build_task_summary_string(
        task=task,
        include_description=True,
        include_dates=True,
        include_assignment=True,
        include_priority=True,
        include_comments=True,
        verbose=True,
    )

    return {"task_id": task_id, "summary": summary_text}
