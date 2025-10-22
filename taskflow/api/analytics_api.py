"""Analytics API endpoints."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from taskflow.models.base import get_db_session
from taskflow.services.analytics_service import AnalyticsService
from taskflow.services.project_service import ProjectService
from taskflow.api.users_api import get_current_user

router = APIRouter()


@router.get("/completion-rate")
def get_completion_rate(
    project_id: Optional[int] = Query(default=None),
    days: int = Query(default=30, ge=1, le=365),
    current_user: Annotated[object, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db_session)] = None,
):
    """Get task completion rate."""
    if project_id:
        # Check access
        project_service = ProjectService(db)
        if not project_service.check_user_access(project_id, current_user.id):  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

    analytics_service = AnalyticsService(db)
    rate = analytics_service.calculate_task_completion_rate(
        project_id=project_id,
        user_id=current_user.id if not project_id else None,  # type: ignore
        days=days,
    )

    return {
        "completion_rate": rate,
        "period_days": days,
        "project_id": project_id,
    }


@router.get("/velocity")
def get_user_velocity(
    days: int = Query(default=14, ge=1, le=90),
    current_user: Annotated[object, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db_session)] = None,
):
    """Get user's task completion velocity."""
    analytics_service = AnalyticsService(db)
    velocity = analytics_service.get_task_velocity(current_user.id, days)  # type: ignore

    return {
        "velocity": velocity,
        "period_days": days,
        "user_id": current_user.id,  # type: ignore
    }


@router.get("/priority-distribution")
def get_priority_distribution(
    project_id: Optional[int] = Query(default=None),
    current_user: Annotated[object, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db_session)] = None,
):
    """Get task distribution by priority."""
    if project_id:
        project_service = ProjectService(db)
        if not project_service.check_user_access(project_id, current_user.id):  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

    analytics_service = AnalyticsService(db)
    distribution = analytics_service.get_priority_distribution(project_id)

    return distribution


@router.get("/status-distribution")
def get_status_distribution(
    project_id: Optional[int] = Query(default=None),
    current_user: Annotated[object, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db_session)] = None,
):
    """Get task distribution by status."""
    if project_id:
        project_service = ProjectService(db)
        if not project_service.check_user_access(project_id, current_user.id):  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

    analytics_service = AnalyticsService(db)
    distribution = analytics_service.get_status_distribution(project_id)

    return distribution


@router.get("/burndown/{project_id}")
def get_burndown_data(
    project_id: int,
    days: int = Query(default=30, ge=7, le=90),
    current_user: Annotated[object, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db_session)] = None,
):
    """Get burndown chart data for a project."""
    project_service = ProjectService(db)
    if not project_service.check_user_access(project_id, current_user.id):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    analytics_service = AnalyticsService(db)
    burndown_data = analytics_service.calculateBurndownData(project_id, days)

    return {
        "project_id": project_id,
        "period_days": days,
        "data": burndown_data,
    }


@router.get("/performance")
def get_performance_metrics(
    days: int = Query(default=30, ge=1, le=365),
    current_user: Annotated[object, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db_session)] = None,
):
    """Get comprehensive performance metrics for current user."""
    analytics_service = AnalyticsService(db)
    metrics = analytics_service.get_user_performance_metrics(current_user.id, days)  # type: ignore

    return metrics


@router.get("/project-health/{project_id}")
def get_project_health(
    project_id: int,
    current_user: Annotated[object, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db_session)] = None,
):
    """Get project health score."""
    project_service = ProjectService(db)
    if not project_service.check_user_access(project_id, current_user.id):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    analytics_service = AnalyticsService(db)
    health_score = analytics_service.get_project_health_score(project_id)

    return {
        "project_id": project_id,
        "health_score": health_score,
    }


@router.get("/trends")
def get_task_trends(
    days: int = Query(default=30, ge=7, le=90),
    current_user: Annotated[object, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db_session)] = None,
):
    """Get task creation and completion trends."""
    analytics_service = AnalyticsService(db)
    trends = analytics_service.getTaskTrends(days)

    return {
        "period_days": days,
        "trends": trends,
    }


@router.get("/team-metrics/{project_id}")
def get_team_metrics(
    project_id: int,
    current_user: Annotated[object, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db_session)] = None,
):
    """Get team-wide metrics for a project."""
    project_service = ProjectService(db)
    if not project_service.check_user_access(project_id, current_user.id):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    analytics_service = AnalyticsService(db)
    metrics = analytics_service.calculate_team_metrics(project_id)

    return metrics


@router.get("/time-to-completion")
def get_time_to_completion_stats(
    project_id: Optional[int] = Query(default=None),
    current_user: Annotated[object, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db_session)] = None,
):
    """Get time-to-completion statistics."""
    if project_id:
        project_service = ProjectService(db)
        if not project_service.check_user_access(project_id, current_user.id):  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

    analytics_service = AnalyticsService(db)
    stats = analytics_service.get_time_to_completion_stats(project_id)

    return {
        "project_id": project_id,
        "stats": stats,
    }
