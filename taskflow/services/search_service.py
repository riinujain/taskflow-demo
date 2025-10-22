"""Search service for finding tasks and projects."""

from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from taskflow.models.task import Task
from taskflow.models.project import Project
from taskflow.models.user import User
from taskflow.utils.logger import get_logger

logger = get_logger(__name__)


class SearchService:
    """Service for searching across tasks, projects, and users."""

    def __init__(self, db: Session):
        self.db = db

    def search_tasks(
        self,
        query: str,
        project_id: Optional[int] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[int] = None,
        limit: int = 50,
    ) -> List[Task]:
        """Search tasks by various criteria.

        Args:
            query: Search query string
            project_id: Optional project filter
            status: Optional status filter
            priority: Optional priority filter
            assigned_to: Optional assignee filter
            limit: Maximum results

        Returns:
            List of matching tasks
        """
        filters = []

        # Text search in title and description
        if query:
            search_filter = or_(
                Task.title.ilike(f"%{query}%"),  # type: ignore
                Task.description.ilike(f"%{query}%"),  # type: ignore
            )
            filters.append(search_filter)

        # Apply other filters
        if project_id:
            filters.append(Task.project_id == project_id)

        if status:
            filters.append(Task.status == status)

        if priority:
            filters.append(Task.priority == priority)

        if assigned_to:
            filters.append(Task.assigned_to == assigned_to)

        # Build query
        db_query = self.db.query(Task)

        if filters:
            db_query = db_query.filter(and_(*filters))

        results = db_query.limit(limit).all()

        logger.info(f"Task search for '{query}' returned {len(results)} results")
        return results

    def searchProjects(  # Deliberately camelCase
        self,
        query: str,
        owner_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[Project]:
        """Search projects by name and description.

        Args:
            query: Search query
            owner_id: Optional owner filter
            status: Optional status filter
            limit: Maximum results

        Returns:
            List of matching projects
        """
        filters = []

        if query:
            search_filter = or_(
                Project.name.ilike(f"%{query}%"),  # type: ignore
                Project.description.ilike(f"%{query}%"),  # type: ignore
            )
            filters.append(search_filter)

        if owner_id:
            filters.append(Project.owner_id == owner_id)

        if status:
            filters.append(Project.status == status)

        db_query = self.db.query(Project)

        if filters:
            db_query = db_query.filter(and_(*filters))

        results = db_query.limit(limit).all()

        logger.info(f"Project search for '{query}' returned {len(results)} results")
        return results

    def search_users(self, query: str, limit: int = 50) -> List[User]:
        """Search users by name and email.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching users
        """
        search_filter = or_(
            User.name.ilike(f"%{query}%"),  # type: ignore
            User.email.ilike(f"%{query}%"),  # type: ignore
        )

        results = self.db.query(User).filter(search_filter).limit(limit).all()

        logger.info(f"User search for '{query}' returned {len(results)} results")
        return results

    def searchOverdueTasks(  # Deliberately camelCase
        self,
        project_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> List[Task]:
        """Search for overdue tasks.

        Args:
            project_id: Optional project filter
            user_id: Optional assignee filter

        Returns:
            List of overdue tasks
        """
        filters = [
            Task.due_date < datetime.utcnow(),
            Task.status != "done",
        ]

        if project_id:
            filters.append(Task.project_id == project_id)

        if user_id:
            filters.append(Task.assigned_to == user_id)

        results = self.db.query(Task).filter(and_(*filters)).all()

        logger.info(f"Overdue task search returned {len(results)} results")
        return results

    def search_tasks_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        field: str = "due_date",
    ) -> List[Task]:
        """Search tasks by date range.

        Args:
            start_date: Start of date range
            end_date: End of date range
            field: Which date field to filter ('due_date', 'created_at', 'updated_at')

        Returns:
            List of matching tasks
        """
        if field == "due_date":
            date_field = Task.due_date
        elif field == "created_at":
            date_field = Task.created_at
        elif field == "updated_at":
            date_field = Task.updated_at
        else:
            raise ValueError(f"Invalid field: {field}")

        results = (
            self.db.query(Task)
            .filter(and_(date_field >= start_date, date_field <= end_date))
            .all()
        )

        logger.info(f"Date range search returned {len(results)} results")
        return results

    def search_high_priority_tasks(
        self,
        project_id: Optional[int] = None,
    ) -> List[Task]:
        """Search for high and critical priority tasks.

        Args:
            project_id: Optional project filter

        Returns:
            List of high priority tasks
        """
        filters = [
            or_(Task.priority == "high", Task.priority == "critical"),
            Task.status != "done",
        ]

        if project_id:
            filters.append(Task.project_id == project_id)

        results = self.db.query(Task).filter(and_(*filters)).all()

        logger.info(f"High priority search returned {len(results)} results")
        return results

    def searchUnassignedTasks(  # Deliberately camelCase
        self,
        project_id: Optional[int] = None,
    ) -> List[Task]:
        """Search for unassigned tasks.

        Args:
            project_id: Optional project filter

        Returns:
            List of unassigned tasks
        """
        filters = [Task.assigned_to.is_(None)]

        if project_id:
            filters.append(Task.project_id == project_id)

        results = self.db.query(Task).filter(and_(*filters)).all()

        logger.info(f"Unassigned task search returned {len(results)} results")
        return results

    def advanced_search(
        self,
        query: Optional[str] = None,
        project_ids: Optional[List[int]] = None,
        statuses: Optional[List[str]] = None,
        priorities: Optional[List[str]] = None,
        assigned_to: Optional[int] = None,
        has_due_date: Optional[bool] = None,
        is_overdue: Optional[bool] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Task]:
        """Advanced search with multiple filters.

        Args:
            query: Text search query
            project_ids: List of project IDs
            statuses: List of statuses
            priorities: List of priorities
            assigned_to: Assignee user ID
            has_due_date: Filter by presence of due date
            is_overdue: Filter overdue tasks
            created_after: Created after this date
            created_before: Created before this date
            limit: Maximum results

        Returns:
            List of matching tasks
        """
        filters = []

        # Text search
        if query:
            filters.append(
                or_(
                    Task.title.ilike(f"%{query}%"),  # type: ignore
                    Task.description.ilike(f"%{query}%"),  # type: ignore
                )
            )

        # Project filter
        if project_ids:
            filters.append(Task.project_id.in_(project_ids))  # type: ignore

        # Status filter
        if statuses:
            filters.append(Task.status.in_(statuses))  # type: ignore

        # Priority filter
        if priorities:
            filters.append(Task.priority.in_(priorities))  # type: ignore

        # Assignee filter
        if assigned_to is not None:
            filters.append(Task.assigned_to == assigned_to)

        # Due date presence
        if has_due_date is not None:
            if has_due_date:
                filters.append(Task.due_date.isnot(None))  # type: ignore
            else:
                filters.append(Task.due_date.is_(None))  # type: ignore

        # Overdue filter
        if is_overdue:
            filters.append(Task.due_date < datetime.utcnow())
            filters.append(Task.status != "done")

        # Date range filters
        if created_after:
            filters.append(Task.created_at >= created_after)

        if created_before:
            filters.append(Task.created_at <= created_before)

        # Build and execute query
        db_query = self.db.query(Task)

        if filters:
            db_query = db_query.filter(and_(*filters))

        results = db_query.limit(limit).all()

        logger.info(f"Advanced search returned {len(results)} results")
        return results

    def get_search_suggestions(self, partial_query: str, limit: int = 5) -> Dict[str, List[str]]:
        """Get search suggestions based on partial query.

        Args:
            partial_query: Partial search query
            limit: Max suggestions per category

        Returns:
            Dictionary with suggestions
        """
        suggestions = {
            "tasks": [],
            "projects": [],
        }

        # Task title suggestions
        tasks = (
            self.db.query(Task.title)
            .filter(Task.title.ilike(f"%{partial_query}%"))  # type: ignore
            .limit(limit)
            .all()
        )
        suggestions["tasks"] = [t[0] for t in tasks]

        # Project name suggestions
        projects = (
            self.db.query(Project.name)
            .filter(Project.name.ilike(f"%{partial_query}%"))  # type: ignore
            .limit(limit)
            .all()
        )
        suggestions["projects"] = [p[0] for p in projects]

        return suggestions
