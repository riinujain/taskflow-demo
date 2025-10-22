"""API route handlers for TaskFlow."""

from fastapi import APIRouter

from taskflow.api import users_api, projects_api, tasks_api, reports_api, health_api, analytics_api

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(users_api.router, prefix="/auth", tags=["auth"])
api_router.include_router(users_api.user_router, prefix="/users", tags=["users"])
api_router.include_router(projects_api.router, prefix="/projects", tags=["projects"])
api_router.include_router(tasks_api.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(reports_api.router, prefix="/reports", tags=["reports"])
api_router.include_router(analytics_api.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(health_api.router, tags=["health"])

__all__ = ["api_router"]
