"""User management service."""

from typing import List, Optional
import logging

from sqlalchemy.orm import Session

from taskflow.models.user import User
from taskflow.models.repository import UserRepository

# Yet another logging pattern - direct logger creation
logger = logging.getLogger(__name__)


class UserService:
    """Service for user management operations."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(User, db)

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        return self.user_repo.get_by_id(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email address."""
        return self.user_repo.get_by_email(email)

    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        return self.user_repo.get_all(skip=skip, limit=limit)

    def get_active_users(self) -> List[User]:
        """Get all active users."""
        return self.user_repo.get_active_users()

    def update_user(
        self,
        user_id: int,
        name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Optional[User]:
        """Update user information.

        Args:
            user_id: User ID to update
            name: New name (optional)
            email: New email (optional)

        Returns:
            Updated user or None if not found
        """
        update_data = {}
        if name:
            update_data["name"] = name
        if email:
            # Check if email is already taken
            existing = self.user_repo.get_by_email(email)
            if existing and existing.id != user_id:
                logger.error(f"Email {email} is already taken")
                return None
            update_data["email"] = email

        if not update_data:
            logger.warning(f"No update data provided for user {user_id}")
            return self.user_repo.get_by_id(user_id)

        return self.user_repo.update(user_id, **update_data)

    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user account.

        Args:
            user_id: User ID to deactivate

        Returns:
            True if successful
        """
        user = self.user_repo.update(user_id, is_active=False)
        if user:
            logger.info(f"User {user_id} deactivated")
            return True
        return False

    def activate_user(self, user_id: int) -> bool:
        """Activate a user account."""
        user = self.user_repo.update(user_id, is_active=True)
        if user:
            logger.info(f"User {user_id} activated")
            return True
        return False

    def delete_user(self, user_id: int) -> bool:
        """Delete a user.

        Note: This is a hard delete. Consider soft delete in production.
        """
        success = self.user_repo.delete(user_id)
        if success:
            logger.info(f"User {user_id} deleted")
        return success

    def count_users(self) -> int:
        """Get total number of users."""
        return self.user_repo.count()

    def get_user_projects(self, user_id: int) -> List:
        """Get all projects owned by a user.

        Args:
            user_id: User ID

        Returns:
            List of projects owned by the user
        """
        # Import here to avoid circular dependency at module level
        from taskflow.models.repository import ProjectRepository
        from taskflow.models.project import Project

        project_repo = ProjectRepository(Project, self.db)
        projects = project_repo.get_by_owner(user_id)

        logger.info(f"Retrieved {len(projects)} projects for user {user_id}")
        return projects

    def add_user_to_project(self, user_id: int, project_id: int) -> bool:
        """Add a user to a project (placeholder - would assign membership in full implementation).

        In a real system, this would add a user to a project's member list.
        For now, this just validates that both user and project exist.

        Args:
            user_id: User ID
            project_id: Project ID

        Returns:
            True if successful, False otherwise
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            logger.error(f"User {user_id} not found")
            return False

        # Import here to avoid circular dependency
        from taskflow.models.repository import ProjectRepository
        from taskflow.models.project import Project

        project_repo = ProjectRepository(Project, self.db)
        project = project_repo.get_by_id(project_id)

        if not project:
            logger.error(f"Project {project_id} not found")
            return False

        # In a full implementation, we would add to a project_members table
        # For now, just log the action
        logger.info(f"User {user_id} added to project {project_id} (placeholder)")
        return True

    def getUserStats(self, user_id: int):  # Deliberately camelCase
        """Get statistics for a user.

        Missing type hint deliberately.
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None

        # Import here to avoid circular dependency (bad practice)
        from taskflow.models.repository import ProjectRepository, TaskRepository
        from taskflow.models.project import Project
        from taskflow.models.task import Task

        project_repo = ProjectRepository(Project, self.db)
        task_repo = TaskRepository(Task, self.db)

        owned_projects = project_repo.get_by_owner(user_id)
        assigned_tasks = task_repo.get_by_assignee(user_id)

        return {
            "user_id": user_id,
            "total_projects": len(owned_projects),
            "total_tasks": len(assigned_tasks),
            "active": user.is_active,
        }
