"""Project model and schemas.

This module defines the Project model for organizing tasks.
Projects are owned by users and contain multiple tasks.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from taskflow.models.base import Base


class Project(Base):
    """Project model for organizing tasks.

    A project belongs to an owner (user) and can contain multiple tasks.
    Projects have a composite unique constraint on (name, owner_id) to prevent
    duplicate project names for the same owner.

    Relationships:
        - owner: The user who owns this project
        - tasks: All tasks within this project
    """

    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint("name", "owner_id", name="uq_project_name_owner"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, default=None)
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), default="active", nullable=False
    )  # active, archived, completed
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=None, onupdate=datetime.utcnow
    )

    # Relationships
    owner: Mapped["User"] = relationship(  # type: ignore
        "User", back_populates="owned_projects", foreign_keys=[owner_id]
    )
    tasks: Mapped[list["Task"]] = relationship(  # type: ignore
        "Task", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name}, owner_id={self.owner_id})>"

    def to_dict(self):
        """Convert project to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
