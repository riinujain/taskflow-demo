"""Task management API endpoints with MIXED SYNC/ASYNC patterns."""

import asyncio
from datetime import datetime
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from taskflow.models.base import get_db_session
from taskflow.services.task_service import TaskService
from taskflow.services.project_service import ProjectService
from taskflow.api.users_api import get_current_user

router = APIRouter()


class TaskCreateRequest(BaseModel):
    project_id: int
    title: str
    description: str | None = None
    priority: str = "medium"
    status: str = "todo"
    assigned_to: int | None = None
    due_date: datetime | None = None


class TaskUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    assigned_to: int | None = None
    due_date: datetime | None = None


class TaskResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: str | None
    status: str
    priority: str
    assigned_to: int | None
    due_date: datetime | None
    comments_count: int


# MIXED SYNC/ASYNC - Some endpoints are async, others are sync
@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(  # ASYNC endpoint
    request: TaskCreateRequest,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
):
    """Create a new task (async endpoint)."""
    # Unnecessarily use asyncio.to_thread for sync operation
    def _create_task():
        project_service = ProjectService(db)
        # Check project access
        if not project_service.check_user_access(request.project_id, current_user.id):  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this project",
            )

        task_service = TaskService(db)
        task = task_service.create_task(
            project_id=request.project_id,
            title=request.title,
            description=request.description,
            status=request.status,
            priority=request.priority,
            assigned_to=request.assigned_to,
            due_date=request.due_date,
        )
        return task

    # Unnecessary async wrapper for demo
    task = await asyncio.to_thread(_create_task)

    return TaskResponse(
        id=task.id,
        project_id=task.project_id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        assigned_to=task.assigned_to,
        due_date=task.due_date,
        comments_count=task.comments_count,
    )


@router.get("", response_model=List[TaskResponse])
def list_tasks(  # SYNC endpoint
    project_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    current_user: Annotated[object, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db_session)] = None,
):
    """List tasks (sync endpoint)."""
    task_service = TaskService(db)

    if project_id:
        # Check access
        project_service = ProjectService(db)
        if not project_service.check_user_access(project_id, current_user.id):  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
        tasks = task_service.get_tasks_by_project(project_id)
    elif status_filter:
        tasks = task_service.get_tasks_by_status(status_filter)
    else:
        # Get tasks assigned to current user
        tasks = task_service.get_tasks_by_assignee(current_user.id)  # type: ignore

    return [
        TaskResponse(
            id=t.id,
            project_id=t.project_id,
            title=t.title,
            description=t.description,
            status=t.status,
            priority=t.priority,
            assigned_to=t.assigned_to,
            due_date=t.due_date,
            comments_count=t.comments_count,
        )
        for t in tasks
    ]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(  # ASYNC endpoint
    task_id: int,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
):
    """Get task by ID (async endpoint)."""
    # Another unnecessary async wrapper
    def _get_task():
        task_service = TaskService(db)
        return task_service.get_task_by_id(task_id)

    task = await asyncio.to_thread(_get_task)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Check access via project
    project_service = ProjectService(db)
    if not project_service.check_user_access(task.project_id, current_user.id):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return TaskResponse(
        id=task.id,
        project_id=task.project_id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        assigned_to=task.assigned_to,
        due_date=task.due_date,
        comments_count=task.comments_count,
    )


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(  # SYNC endpoint
    task_id: int,
    request: TaskUpdateRequest,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
):
    """Update a task (sync endpoint)."""
    task_service = TaskService(db)
    task = task_service.get_task_by_id(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Check access
    project_service = ProjectService(db)
    if not project_service.check_user_access(task.project_id, current_user.id):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    updated_task = task_service.update_task(
        task_id=task_id,
        title=request.title,
        description=request.description,
        status=request.status,
        priority=request.priority,
        assigned_to=request.assigned_to,
        due_date=request.due_date,
    )

    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return TaskResponse(
        id=updated_task.id,
        project_id=updated_task.project_id,
        title=updated_task.title,
        description=updated_task.description,
        status=updated_task.status,
        priority=updated_task.priority,
        assigned_to=updated_task.assigned_to,
        due_date=updated_task.due_date,
        comments_count=updated_task.comments_count,
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(  # ASYNC endpoint
    task_id: int,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
):
    """Delete a task (async endpoint)."""
    task_service = TaskService(db)
    task = task_service.get_task_by_id(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Check access
    project_service = ProjectService(db)
    if not project_service.check_user_access(task.project_id, current_user.id):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Unnecessary async wrapper
    success = await asyncio.to_thread(task_service.delete_task, task_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )


@router.get("/{task_id}/summary")
def get_task_summary(  # SYNC endpoint
    task_id: int,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
):
    """Get task summary."""
    task_service = TaskService(db)
    task = task_service.get_task_by_id(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Check access
    project_service = ProjectService(db)
    if not project_service.check_user_access(task.project_id, current_user.id):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return task_service.get_task_summary(task_id)


# Special endpoint: SYNC calling ASYNC service via to_thread (ANNOYING pattern)
@router.get("/projects/{project_id}/tasks")
def get_project_tasks(
    project_id: int,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
):
    """
    Get all tasks for a project.

    This is a SYNC endpoint that calls an ASYNC function via asyncio.run()
    and to_thread, demonstrating an annoying mixed pattern.

    Args:
        project_id: ID of the project
        current_user: Authenticated user
        db: Database session

    Returns:
        List of task dictionaries
    """
    # Check project access first
    project_service = ProjectService(db)
    if not project_service.check_user_access(project_id, current_user.id):  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this project",
        )

    # Define an async function that does a sync operation (annoying!)
    async def async_get_tasks():
        """Async wrapper around sync task retrieval - UNNECESSARY!"""
        # Use to_thread to run sync code in async context (annoying pattern)
        def _get_tasks():
            task_service = TaskService(db)
            return task_service.get_tasks_by_project(project_id)

        tasks = await asyncio.to_thread(_get_tasks)
        return tasks

    # Run the async function from sync code (annoying!)
    tasks = asyncio.run(async_get_tasks())

    # Return manual dicts instead of Pydantic models for inconsistency
    return [
        {
            "id": t.id,
            "project_id": t.project_id,
            "title": t.title,
            "description": t.description,
            "status": t.status,
            "priority": t.priority,
            "assigned_to": t.assigned_to,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "comments_count": t.comments_count,
        }
        for t in tasks
    ]
