"""User model and schemas.

This module defines the User model for authentication and profile management.
Users can own projects and be assigned to tasks.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from taskflow.models.base import Base


class User(Base):
    """User model for authentication and profile management.

    Relationships:
        - owned_projects: Projects created by this user
        - assigned_tasks: Tasks assigned to this user
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=None, onupdate=datetime.utcnow
    )

    # Relationships
    owned_projects: Mapped[list["Project"]] = relationship(  # type: ignore
        "Project", back_populates="owner", foreign_keys="Project.owner_id"
    )
    assigned_tasks: Mapped[list["Task"]] = relationship(  # type: ignore
        "Task", back_populates="assignee", foreign_keys="Task.assigned_to"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"

    def to_dict(self):
        """Convert user to dictionary (exclude password)."""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
