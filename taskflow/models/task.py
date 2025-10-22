"""Task model and schemas.

This module defines the Task model for tracking work items within projects.
Tasks can be assigned to users and have priorities, statuses, and due dates.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from taskflow.models.base import Base


class Task(Base):
    """Task model for tracking work items.

    Tasks belong to projects and can be assigned to users. They have various
    attributes like status, priority, and due dates for task management.

    Indexes:
        - project_id: For efficient project-based queries
        - assigned_to: For efficient user assignment queries
        - due_date: For efficient due date and overdue queries

    Relationships:
        - project: The project this task belongs to
        - assignee: The user this task is assigned to (optional)
    """

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, default=None)
    status: Mapped[str] = mapped_column(
        String(50), default="todo", nullable=False
    )  # todo, in_progress, done, blocked
    priority: Mapped[str] = mapped_column(
        String(50), default="medium", nullable=False
    )  # low, medium, high, critical
    assigned_to: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), default=None, index=True
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=None, index=True  # Index for efficient due date queries
    )
    comments_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=None, onupdate=datetime.utcnow
    )

    # Relationships
    project: Mapped["Project"] = relationship(  # type: ignore
        "Project", back_populates="tasks", foreign_keys=[project_id]
    )
    assignee: Mapped[Optional["User"]] = relationship(  # type: ignore
        "User", back_populates="assigned_tasks", foreign_keys=[assigned_to]
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"

    def to_dict(self):
        """Convert task to dictionary."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "assigned_to": self.assigned_to,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "comments_count": self.comments_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
