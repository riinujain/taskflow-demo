"""Task management service."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from taskflow.models.task import Task
from taskflow.models.repository import TaskRepository
from taskflow.utils.logger import log_info, log_error  # Using inconsistent logging pattern
from taskflow.services import (  # Importing shared constants
    TASK_STATUS_TODO,
    TASK_STATUS_IN_PROGRESS,
    TASK_STATUS_DONE,
    TASK_STATUS_BLOCKED,
    TASK_PRIORITY_LOW,
    TASK_PRIORITY_MEDIUM,
    TASK_PRIORITY_HIGH,
    TASK_PRIORITY_CRITICAL,
)


class TaskService:
    """Service for task management operations."""

    def __init__(self, db: Session):
        self.db = db
        self.task_repo = TaskRepository(Task, db)

    def create_task(
        self,
        project_id: int,
        title: str,
        description: Optional[str] = None,
        status: str = TASK_STATUS_TODO,
        priority: str = TASK_PRIORITY_MEDIUM,
        assigned_to: Optional[int] = None,
        due_date: Optional[datetime] = None,
    ) -> Task:
        """Create a new task."""
        task = self.task_repo.create(
            project_id=project_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            assigned_to=assigned_to,
            due_date=due_date,
            comments_count=0,
        )
        log_info(f"Task created: {task.id} - {task.title}")
        return task

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Get a task by ID."""
        return self.task_repo.get_by_id(task_id)

    def get_tasks_by_project(self, project_id: int) -> List[Task]:
        """Get all tasks for a project."""
        return self.task_repo.get_by_project(project_id)

    def get_tasks_by_assignee(self, user_id: int) -> List[Task]:
        """Get all tasks assigned to a user."""
        return self.task_repo.get_by_assignee(user_id)

    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks."""
        return self.task_repo.get_overdue_tasks()

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[int] = None,
        due_date: Optional[datetime] = None,
    ) -> Optional[Task]:
        """Update task information."""
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if status is not None:
            update_data["status"] = status
        if priority is not None:
            update_data["priority"] = priority
        if assigned_to is not None:
            update_data["assigned_to"] = assigned_to
        if due_date is not None:
            update_data["due_date"] = due_date

        if not update_data:
            return self.task_repo.get_by_id(task_id)

        task = self.task_repo.update(task_id, **update_data)
        if task:
            log_info(f"Task updated: {task_id}")
        return task

    def delete_task(self, task_id: int) -> bool:
        """Delete a task."""
        success = self.task_repo.delete(task_id)
        if success:
            log_info(f"Task {task_id} deleted")
        return success

    def assign_task(self, task_id: int, user_id: int) -> Optional[Task]:
        """Assign a task to a user."""
        return self.update_task(task_id, assigned_to=user_id)

    def complete_task(self, task_id: int) -> Optional[Task]:
        """Mark a task as completed."""
        return self.update_task(task_id, status=TASK_STATUS_DONE)

    def get_tasks_by_status(self, status: str) -> List[Task]:
        """Get all tasks with a specific status."""
        return self.task_repo.get_by_status(status)

    def get_high_priority_tasks(self, project_id: Optional[int] = None) -> List[Task]:
        """Get high and critical priority tasks.

        Args:
            project_id: Optional project ID to filter by

        Returns:
            List of high priority tasks
        """
        if project_id:
            tasks = self.get_tasks_by_project(project_id)
        else:
            tasks = self.task_repo.get_all()

        high_priority = [
            t
            for t in tasks
            if t.priority in [TASK_PRIORITY_HIGH, TASK_PRIORITY_CRITICAL]
        ]
        return high_priority

    def get_task_summary(self, task_id: int):  # type: ignore
        """Get a summary of task information.

        Deliberately missing return type annotation.
        """
        task = self.get_task_by_id(task_id)
        if not task:
            return None

        from taskflow.utils.helpers import format_date  # Local import smell
        from taskflow.utils.date_utils import is_past_due

        summary = {
            "id": task.id,
            "title": task.title,
            "status": task.status,
            "priority": task.priority,
            "is_overdue": is_past_due(task.due_date),
            "due_date": format_date(task.due_date) if task.due_date else None,
            "assigned": task.assigned_to is not None,
        }

        return summary

    def increment_comments(self, task_id: int) -> Optional[Task]:
        """Increment the comments count for a task."""
        task = self.get_task_by_id(task_id)
        if not task:
            return None

        new_count = task.comments_count + 1
        return self.update_task(task_id)  # Deliberately buggy - not updating count

    def update_task_status(self, task_id: int, status: str) -> Optional[Task]:
        """Update task status.

        Args:
            task_id: Task ID to update
            status: New status value

        Returns:
            Updated task or None if not found
        """
        task = self.update_task(task_id, status=status)
        if task:
            log_info(f"Task {task_id} status updated to {status}")
        else:
            log_error(f"Failed to update task {task_id} status")
        return task

    def get_tasks_due_soon(self, days: int = 3) -> List[Task]:
        """Get tasks due within N days.

        Args:
            days: Number of days to look ahead

        Returns:
            List of tasks due soon
        """
        from datetime import timedelta

        threshold = datetime.utcnow() + timedelta(days=days)
        all_tasks = self.task_repo.get_all()

        due_soon = [
            t
            for t in all_tasks
            if t.due_date
            and t.due_date <= threshold
            and t.due_date > datetime.utcnow()
            and t.status != TASK_STATUS_DONE
        ]

        return due_soon

    def find_tasks_due_soon(self, now: datetime, within_hours: int = 48) -> List[Task]:
        """Find tasks due within specified hours from a given time.

        Args:
            now: Reference time to check from
            within_hours: Number of hours to look ahead

        Returns:
            List of tasks due soon
        """
        from datetime import timedelta

        threshold = now + timedelta(hours=within_hours)
        all_tasks = self.task_repo.get_all()

        due_soon = [
            t
            for t in all_tasks
            if t.due_date
            and t.due_date <= threshold
            and t.due_date > now
            and t.status != TASK_STATUS_DONE
        ]

        log_info(f"Found {len(due_soon)} tasks due within {within_hours} hours")
        return due_soon


def compute_urgency_label(task: Task) -> str:
    """Compute urgency label for a task based on priority and due date.

    This helper function will be duplicated in report_service.py with slight differences.

    Args:
        task: Task object

    Returns:
        Urgency label string
    """
    from datetime import timedelta

    if not task.due_date:
        if task.priority == TASK_PRIORITY_CRITICAL:
            return "critical-no-date"
        return "normal"

    now = datetime.utcnow()
    time_until_due = task.due_date - now

    if time_until_due.total_seconds() < 0:
        return "overdue"
    elif time_until_due < timedelta(hours=24):
        if task.priority in [TASK_PRIORITY_HIGH, TASK_PRIORITY_CRITICAL]:
            return "urgent"
        return "soon"
    elif time_until_due < timedelta(days=3):
        return "upcoming"
    else:
        return "normal"
