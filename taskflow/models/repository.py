"""Generic repository pattern for database operations.

This module provides a generic repository pattern for CRUD operations on database models.
The Repository class uses Python generics to provide type-safe operations for any model
that inherits from Base.

Note: While this pattern is used throughout most of the application, some services
(like project_service.py) contain raw SQL queries for "temporary" reasons - demonstrating
an inconsistency in the codebase.
"""

from typing import TypeVar, Generic, Type, Optional, List, Any

from sqlalchemy.orm import Session
from sqlalchemy import select

from taskflow.models.base import Base

T = TypeVar("T", bound=Base)


class Repository(Generic[T]):
    """Generic repository for CRUD operations.

    This provides a reusable pattern for database operations including:
    - create: Create new records
    - get_by_id: Retrieve by primary key
    - get_all: List all records with pagination
    - update: Update existing records
    - delete: Delete records
    - find_by: Query by arbitrary filters
    - find_one_by: Query for a single record
    - count: Count total records
    - exists: Check record existence

    Though this pattern is available, some services bypass it for
    "temporary" reasons (see project_service.py for raw SQL examples).
    """

    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db

    def create(self, **kwargs) -> T:
        """Create a new record."""
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def get_by_id(self, record_id: int) -> Optional[T]:
        """Get a record by ID."""
        return self.db.get(self.model, record_id)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination."""
        stmt = select(self.model).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def update(self, record_id: int, **kwargs) -> Optional[T]:
        """Update a record by ID."""
        instance = self.get_by_id(record_id)
        if not instance:
            return None

        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete(self, record_id: int) -> bool:
        """Delete a record by ID."""
        instance = self.get_by_id(record_id)
        if not instance:
            return False

        self.db.delete(instance)
        self.db.commit()
        return True

    def find_by(self, **filters) -> List[T]:
        """Find records by arbitrary filters."""
        stmt = select(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                stmt = stmt.where(getattr(self.model, key) == value)

        return list(self.db.execute(stmt).scalars().all())

    def find_one_by(self, **filters) -> Optional[T]:
        """Find a single record by filters."""
        results = self.find_by(**filters)
        return results[0] if results else None

    def count(self) -> int:
        """Count total records."""
        return self.db.query(self.model).count()  # type: ignore

    def exists(self, record_id: int) -> bool:
        """Check if a record exists."""
        return self.get_by_id(record_id) is not None


class UserRepository(Repository):
    """User-specific repository with custom methods."""

    def get_by_email(self, email: str):
        """Get user by email address."""
        return self.find_one_by(email=email)

    def get_active_users(self):
        """Get all active users."""
        return self.find_by(is_active=True)


class ProjectRepository(Repository):
    """Project-specific repository with custom methods."""

    def get_by_owner(self, owner_id: int):
        """Get all projects owned by a user."""
        return self.find_by(owner_id=owner_id)

    def get_active_projects(self):
        """Get all active projects."""
        return self.find_by(status="active")


class TaskRepository(Repository):
    """Task-specific repository with custom methods."""

    def get_by_project(self, project_id: int):
        """Get all tasks for a project."""
        return self.find_by(project_id=project_id)

    def get_by_assignee(self, user_id: int):
        """Get all tasks assigned to a user."""
        return self.find_by(assigned_to=user_id)

    def get_by_status(self, status: str):
        """Get all tasks with a specific status."""
        return self.find_by(status=status)

    def get_overdue_tasks(self):
        """Get overdue tasks - requires custom query."""
        from datetime import datetime
        stmt = select(self.model).where(
            self.model.due_date < datetime.utcnow(),
            self.model.status != "done"
        )
        return list(self.db.execute(stmt).scalars().all())
