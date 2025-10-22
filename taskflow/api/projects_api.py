"""Project management API endpoints."""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from taskflow.models.base import get_db_session
from taskflow.services.project_service import ProjectService
from taskflow.api.users_api import get_current_user

router = APIRouter()


class ProjectCreateRequest(BaseModel):
    name: str
    description: str | None = None


class ProjectUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None
    owner_id: int
    status: str
    created_at: str | None = None
    updated_at: str | None = None


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    request: ProjectCreateRequest,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
):
    """
    Create a new project for the authenticated user.

    Parameters
    ----------
    request : ProjectCreateRequest
        Project data including name and optional description
    current_user : User
        Authenticated user from JWT token
    db : Session
        Database session

    Returns
    -------
    ProjectResponse
        The created project

    Notes
    -----
    This endpoint uses NumPy-style docstring for variety.
    """
    project_service = ProjectService(db)
    project = project_service.create_project(
        name=request.name,
        owner_id=current_user.id,  # type: ignore
        description=request.description,
    )

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        owner_id=project.owner_id,
        status=project.status,
        created_at=project.created_at.isoformat() if project.created_at else None,
        updated_at=project.updated_at.isoformat() if project.updated_at else None,
    )


@router.get("")
def list_projects(
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
):
    # No docstring - inconsistent style
    project_service = ProjectService(db)
    projects = project_service.list_projects_for_user(current_user.id)  # type: ignore

    # Manually return list of dicts instead of using Pydantic model
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "owner_id": p.owner_id,
            "status": p.status,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        }
        for p in projects
    ]


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
):
    """Get project by ID."""
    project_service = ProjectService(db)
    project = project_service.get_project_by_id(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Check access
    if not project_service.check_user_access(project_id, current_user.id):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        owner_id=project.owner_id,
        status=project.status,
        created_at=project.created_at.isoformat() if project.created_at else None,
        updated_at=project.updated_at.isoformat() if project.updated_at else None,
    )


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    request: ProjectUpdateRequest,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
):
    """Update a project."""
    project_service = ProjectService(db)

    # Check access
    if not project_service.check_user_access(project_id, current_user.id):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    project = project_service.update_project(
        project_id=project_id,
        name=request.name,
        description=request.description,
        status=request.status,
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        owner_id=project.owner_id,
        status=project.status,
        created_at=project.created_at.isoformat() if project.created_at else None,
        updated_at=project.updated_at.isoformat() if project.updated_at else None,
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
):
    """Delete a project."""
    project_service = ProjectService(db)

    # Check access
    if not project_service.check_user_access(project_id, current_user.id):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    success = project_service.delete_project(project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )


@router.get("/{project_id}/stats")
def get_project_stats(
    project_id: int,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
):
    """Get project statistics (uses raw SQL)."""
    project_service = ProjectService(db)

    # Check access
    if not project_service.check_user_access(project_id, current_user.id):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    stats = project_service.get_project_stats(project_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return stats
