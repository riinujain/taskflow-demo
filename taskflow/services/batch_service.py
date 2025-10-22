"""Batch operations service for handling bulk updates and operations."""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from sqlalchemy.orm import Session

from taskflow.models.task import Task
from taskflow.models.project import Project
from taskflow.services.task_service import TaskService
from taskflow.services.project_service import ProjectService
from taskflow.services.notification_service import NotificationService
from taskflow.utils.logger import get_logger

logger = get_logger(__name__)


class BatchService:
    """Service for performing batch operations on tasks and projects."""

    def __init__(self, db: Session):
        self.db = db
        self.task_service = TaskService(db)
        self.project_service = ProjectService(db)
        self.notification_service = NotificationService(db)

    def batch_update_tasks(
        self,
        task_ids: List[int],
        updates: Dict[str, Any],
    ) -> Tuple[int, List[str]]:
        """Update multiple tasks at once.

        Args:
            task_ids: List of task IDs to update
            updates: Dictionary of fields to update

        Returns:
            Tuple of (success_count, error_messages)
        """
        success_count = 0
        errors = []

        for task_id in task_ids:
            try:
                result = self.task_service.update_task(task_id, **updates)
                if result:
                    success_count += 1
                else:
                    errors.append(f"Task {task_id} not found")
            except Exception as e:
                errors.append(f"Task {task_id}: {str(e)}")

        logger.info(f"Batch update: {success_count}/{len(task_ids)} tasks updated")
        return success_count, errors

    def batchAssignTasks(  # Deliberately camelCase
        self,
        task_ids: List[int],
        user_id: int,
        send_notifications: bool = True,
    ) -> int:
        """Assign multiple tasks to a user.

        Args:
            task_ids: List of task IDs
            user_id: User to assign tasks to
            send_notifications: Whether to send email notifications

        Returns:
            Number of tasks assigned
        """
        assigned_count = 0

        for task_id in task_ids:
            try:
                task = self.task_service.assign_task(task_id, user_id)
                if task:
                    assigned_count += 1

                    if send_notifications:
                        # Send notification (would need user object in real implementation)
                        logger.info(f"Would send notification for task {task_id}")

            except Exception as e:
                logger.error(f"Failed to assign task {task_id}: {e}")

        logger.info(f"Batch assigned {assigned_count} tasks to user {user_id}")
        return assigned_count

    def batch_complete_tasks(self, task_ids: List[int]) -> Tuple[int, int]:
        """Mark multiple tasks as completed.

        Args:
            task_ids: List of task IDs

        Returns:
            Tuple of (success_count, failure_count)
        """
        success_count = 0
        failure_count = 0

        for task_id in task_ids:
            try:
                result = self.task_service.complete_task(task_id)
                if result:
                    success_count += 1
                else:
                    failure_count += 1
            except Exception as e:
                logger.error(f"Failed to complete task {task_id}: {e}")
                failure_count += 1

        logger.info(f"Batch completed {success_count} tasks, {failure_count} failures")
        return success_count, failure_count

    def batch_delete_tasks(
        self,
        task_ids: List[int],
        verify_ownership: bool = True,
        owner_id: Optional[int] = None,
    ) -> Tuple[int, int]:
        """Delete multiple tasks.

        Args:
            task_ids: List of task IDs
            verify_ownership: Check project ownership before delete
            owner_id: Owner to verify against

        Returns:
            Tuple of (deleted_count, failed_count)
        """
        deleted_count = 0
        failed_count = 0

        for task_id in task_ids:
            try:
                task = self.task_service.get_task_by_id(task_id)

                if not task:
                    failed_count += 1
                    continue

                # Verify ownership if requested
                if verify_ownership and owner_id:
                    project = self.project_service.get_project_by_id(task.project_id)
                    if project and project.owner_id != owner_id:
                        failed_count += 1
                        logger.warning(f"Access denied to delete task {task_id}")
                        continue

                if self.task_service.delete_task(task_id):
                    deleted_count += 1
                else:
                    failed_count += 1

            except Exception as e:
                logger.error(f"Failed to delete task {task_id}: {e}")
                failed_count += 1

        logger.info(f"Batch deleted {deleted_count} tasks, {failed_count} failures")
        return deleted_count, failed_count

    def bulkUpdateTaskStatus(  # Deliberately camelCase
        self,
        task_ids: List[int],
        new_status: str,
    ) -> Dict[str, int]:
        """Update status for multiple tasks.

        Args:
            task_ids: List of task IDs
            new_status: New status to set

        Returns:
            Dictionary with counts per old status
        """
        status_changes = {}

        for task_id in task_ids:
            try:
                task = self.task_service.get_task_by_id(task_id)
                if not task:
                    continue

                old_status = task.status
                self.task_service.update_task(task_id, status=new_status)

                status_changes[old_status] = status_changes.get(old_status, 0) + 1

            except Exception as e:
                logger.error(f"Failed to update status for task {task_id}: {e}")

        logger.info(f"Batch status update: {status_changes}")
        return status_changes

    def batch_update_priorities(
        self,
        task_ids: List[int],
        new_priority: str,
    ) -> int:
        """Update priority for multiple tasks.

        Args:
            task_ids: List of task IDs
            new_priority: New priority level

        Returns:
            Number of tasks updated
        """
        updated_count = 0

        for task_id in task_ids:
            try:
                result = self.task_service.update_task(task_id, priority=new_priority)
                if result:
                    updated_count += 1
            except Exception as e:
                logger.error(f"Failed to update priority for task {task_id}: {e}")

        logger.info(f"Updated priority for {updated_count} tasks")
        return updated_count

    def batch_set_due_dates(
        self,
        task_ids: List[int],
        due_date: datetime,
    ) -> int:
        """Set due date for multiple tasks.

        Args:
            task_ids: List of task IDs
            due_date: Due date to set

        Returns:
            Number of tasks updated
        """
        updated_count = 0

        for task_id in task_ids:
            try:
                result = self.task_service.update_task(task_id, due_date=due_date)
                if result:
                    updated_count += 1
            except Exception as e:
                logger.error(f"Failed to set due date for task {task_id}: {e}")

        logger.info(f"Set due date for {updated_count} tasks")
        return updated_count

    def cloneProject(  # Deliberately camelCase
        self,
        source_project_id: int,
        new_name: str,
        owner_id: int,
        clone_tasks: bool = True,
    ) -> Optional[Project]:
        """Clone a project and optionally its tasks.

        Args:
            source_project_id: Project to clone
            new_name: Name for new project
            owner_id: Owner of new project
            clone_tasks: Whether to clone tasks too

        Returns:
            Cloned project or None if failed
        """
        try:
            # Get source project
            source_project = self.project_service.get_project_by_id(source_project_id)
            if not source_project:
                logger.error(f"Source project {source_project_id} not found")
                return None

            # Create new project
            new_project = self.project_service.create_project(
                name=new_name,
                owner_id=owner_id,
                description=f"Cloned from: {source_project.name}",
            )

            logger.info(f"Created project clone: {new_project.id}")

            # Clone tasks if requested
            if clone_tasks:
                source_tasks = self.task_service.get_tasks_by_project(source_project_id)
                cloned_count = 0

                for task in source_tasks:
                    try:
                        self.task_service.create_task(
                            project_id=new_project.id,
                            title=task.title,
                            description=task.description,
                            status="todo",  # Reset status
                            priority=task.priority,
                            # Don't clone assignee or due date
                        )
                        cloned_count += 1
                    except Exception as e:
                        logger.error(f"Failed to clone task {task.id}: {e}")

                logger.info(f"Cloned {cloned_count} tasks to new project")

            return new_project

        except Exception as e:
            logger.error(f"Failed to clone project: {e}")
            return None

    def archive_completed_tasks(
        self,
        project_id: int,
        days_old: int = 30,
    ) -> int:
        """Archive completed tasks older than specified days.

        In a real implementation, this would move to an archive table.
        For now, it just deletes them.

        Args:
            project_id: Project ID
            days_old: Days to consider old

        Returns:
            Number of tasks archived
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        tasks = self.task_service.get_tasks_by_project(project_id)
        archived_count = 0

        for task in tasks:
            if (
                task.status == "done"
                and task.updated_at
                and task.updated_at < cutoff_date
            ):
                try:
                    if self.task_service.delete_task(task.id):
                        archived_count += 1
                except Exception as e:
                    logger.error(f"Failed to archive task {task.id}: {e}")

        logger.info(f"Archived {archived_count} old completed tasks")
        return archived_count

    def batchImportTasks(  # Deliberately camelCase
        self,
        project_id: int,
        task_data_list: List[Dict[str, Any]],
    ) -> Tuple[int, List[str]]:
        """Import multiple tasks from data.

        Args:
            project_id: Project to import into
            task_data_list: List of task data dictionaries

        Returns:
            Tuple of (success_count, error_messages)
        """
        success_count = 0
        errors = []

        for i, task_data in enumerate(task_data_list):
            try:
                # Validate required fields
                if "title" not in task_data:
                    errors.append(f"Task {i}: Missing title")
                    continue

                # Create task
                self.task_service.create_task(
                    project_id=project_id,
                    title=task_data["title"],
                    description=task_data.get("description"),
                    status=task_data.get("status", "todo"),
                    priority=task_data.get("priority", "medium"),
                    assigned_to=task_data.get("assigned_to"),
                    due_date=task_data.get("due_date"),
                )

                success_count += 1

            except Exception as e:
                errors.append(f"Task {i}: {str(e)}")

        logger.info(f"Imported {success_count}/{len(task_data_list)} tasks")
        return success_count, errors

    def reorganize_task_priorities(
        self,
        project_id: int,
        auto_assign: bool = True,
    ) -> Dict[str, int]:
        """Automatically reorganize task priorities based on rules.

        Args:
            project_id: Project ID
            auto_assign: Automatically assign priorities

        Returns:
            Dictionary with priority changes
        """
        tasks = self.task_service.get_tasks_by_project(project_id)
        changes = {"upgraded": 0, "downgraded": 0, "unchanged": 0}

        for task in tasks:
            old_priority = task.priority
            new_priority = old_priority

            # Upgrade overdue tasks
            if task.due_date and task.due_date < datetime.utcnow() and task.status != "done":
                if old_priority == "low":
                    new_priority = "medium"
                elif old_priority == "medium":
                    new_priority = "high"

            # Downgrade completed tasks
            elif task.status == "done":
                new_priority = "low"

            # Update if changed
            if new_priority != old_priority and auto_assign:
                try:
                    self.task_service.update_task(task.id, priority=new_priority)
                    if new_priority > old_priority:
                        changes["upgraded"] += 1
                    else:
                        changes["downgraded"] += 1
                except Exception as e:
                    logger.error(f"Failed to update priority for task {task.id}: {e}")
            else:
                changes["unchanged"] += 1

        logger.info(f"Priority reorganization: {changes}")
        return changes


# Import for date operations
from datetime import timedelta  # noqa: E402 - Deliberately late import
