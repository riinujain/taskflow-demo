"""Project management service."""

from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text  # For raw SQL

from taskflow.models.project import Project
from taskflow.models.repository import ProjectRepository
from taskflow.utils.logger import get_logger

logger = get_logger(__name__)


class ProjectService:
    """Service for project management operations."""

    def __init__(self, db: Session):
        self.db = db
        self.project_repo = ProjectRepository(Project, db)

    def create_project(
        self,
        name: str,
        owner_id: int,
        description: Optional[str] = None,
    ) -> Project:
        """Create a new project.

        Args:
            name: Project name
            owner_id: User ID of project owner
            description: Optional project description

        Returns:
            Created project
        """
        project = self.project_repo.create(
            name=name,
            owner_id=owner_id,
            description=description,
            status="active",
        )
        logger.info(f"Project created: {project.id} - {project.name}")
        return project

    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        """Get a project by ID."""
        return self.project_repo.get_by_id(project_id)

    def get_projects_by_owner(self, owner_id: int) -> List[Project]:
        """Get all projects owned by a user."""
        return self.project_repo.get_by_owner(owner_id)

    def list_projects_for_user(self, user_id: int) -> List[Project]:
        """List all projects for a user (alias for get_projects_by_owner).

        Args:
            user_id: User ID to get projects for

        Returns:
            List of projects owned by the user
        """
        projects = self.project_repo.get_by_owner(user_id)
        logger.info(f"Listed {len(projects)} projects for user {user_id}")
        return projects

    def get_active_projects(self) -> List[Project]:
        """Get all active projects."""
        return self.project_repo.get_active_projects()

    def update_project(
        self,
        project_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Optional[Project]:
        """Update project information."""
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if status is not None:
            update_data["status"] = status

        if not update_data:
            return self.project_repo.get_by_id(project_id)

        return self.project_repo.update(project_id, **update_data)

    def delete_project(self, project_id: int) -> bool:
        """Delete a project and all its tasks."""
        success = self.project_repo.delete(project_id)
        if success:
            logger.info(f"Project {project_id} deleted")
        return success

    def archive_project(self, project_id: int) -> Optional[Project]:
        """Archive a project."""
        return self.update_project(project_id, status="archived")

    def get_project_stats(self, project_id: int) -> Optional[dict]:
        """Get statistics for a project using RAW SQL.

        TODO: This should use SQLAlchemy instead of raw SQL.
        Using raw SQL here as a "temporary optimization" to bypass the repository pattern.
        This is deliberately using raw SQL to demonstrate a code smell.
        """
        # Temporary optimization: using raw SQL instead of SQLAlchemy/repository
        # This bypasses the repository pattern and should be refactored
        query = text("""
            SELECT
                p.id,
                p.name,
                COUNT(t.id) as total_tasks,
                SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END) as completed_tasks,
                SUM(CASE WHEN t.status = 'todo' THEN 1 ELSE 0 END) as todo_tasks,
                SUM(CASE WHEN t.status = 'in_progress' THEN 1 ELSE 0 END) as in_progress_tasks,
                SUM(CASE WHEN t.status = 'blocked' THEN 1 ELSE 0 END) as blocked_tasks
            FROM projects p
            LEFT JOIN tasks t ON p.id = t.project_id
            WHERE p.id = :project_id
            GROUP BY p.id, p.name
        """)

        result = self.db.execute(query, {"project_id": project_id}).fetchone()

        if not result:
            return None

        return {
            "project_id": result[0],
            "project_name": result[1],
            "total_tasks": result[2] or 0,
            "completed_tasks": result[3] or 0,
            "todo_tasks": result[4] or 0,
            "in_progress_tasks": result[5] or 0,
            "blocked_tasks": result[6] or 0,
        }

    def get_all_projects(self, skip: int = 0, limit: int = 100) -> List[Project]:
        """Get all projects with pagination."""
        return self.project_repo.get_all(skip=skip, limit=limit)

    def check_user_access(self, project_id: int, user_id: int) -> bool:
        """Check if a user has access to a project.

        Currently only checks ownership. In production, would check memberships too.
        """
        project = self.get_project_by_id(project_id)
        if not project:
            return False
        return project.owner_id == user_id

    def count_projects(self) -> int:
        """Get total number of projects."""
        return self.project_repo.count()
