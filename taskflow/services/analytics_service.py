"""Analytics and metrics service with complex calculations."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import func

from taskflow.models.task import Task
from taskflow.models.project import Project
from taskflow.models.user import User
from taskflow.utils.logger import get_logger
from taskflow.utils.helpers import calculate_percentage, safe_divide

logger = get_logger(__name__)


class AnalyticsService:
    """Service for generating analytics and metrics."""

    def __init__(self, db: Session):
        self.db = db

    def calculate_task_completion_rate(
        self,
        project_id: Optional[int] = None,
        user_id: Optional[int] = None,
        days: int = 30,
    ) -> float:
        """Calculate task completion rate over a period.

        Args:
            project_id: Optional project filter
            user_id: Optional user filter
            days: Number of days to look back

        Returns:
            Completion rate as percentage
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        query = self.db.query(Task).filter(Task.created_at >= cutoff_date)

        if project_id:
            query = query.filter(Task.project_id == project_id)

        if user_id:
            query = query.filter(Task.assigned_to == user_id)

        all_tasks = query.all()
        completed_tasks = [t for t in all_tasks if t.status == "done"]

        if not all_tasks:
            return 0.0

        return calculate_percentage(len(completed_tasks), len(all_tasks))

    def get_task_velocity(self, user_id: int, days: int = 14) -> float:
        """Calculate task completion velocity (tasks per day).

        Args:
            user_id: User ID
            days: Number of days to analyze

        Returns:
            Average tasks completed per day
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        completed_tasks = (
            self.db.query(Task)
            .filter(
                Task.assigned_to == user_id,
                Task.status == "done",
                Task.updated_at >= cutoff_date,
            )
            .count()
        )

        return safe_divide(completed_tasks, days)

    def calculateAverageTaskDuration(self, project_id: int) -> float:  # Deliberately camelCase
        """Calculate average duration to complete tasks.

        Returns average in days.
        """
        completed_tasks = (
            self.db.query(Task)
            .filter(Task.project_id == project_id, Task.status == "done", Task.updated_at.isnot(None))
            .all()
        )

        if not completed_tasks:
            return 0.0

        total_duration = 0.0
        for task in completed_tasks:
            if task.updated_at and task.created_at:
                duration = (task.updated_at - task.created_at).days
                total_duration += duration

        return safe_divide(total_duration, len(completed_tasks))

    def get_priority_distribution(self, project_id: Optional[int] = None) -> Dict[str, int]:
        """Get distribution of tasks by priority.

        Args:
            project_id: Optional project filter

        Returns:
            Dictionary mapping priority to count
        """
        query = self.db.query(Task.priority, func.count(Task.id))

        if project_id:
            query = query.filter(Task.project_id == project_id)

        query = query.group_by(Task.priority)

        results = query.all()

        distribution = {
            "low": 0,
            "medium": 0,
            "high": 0,
            "critical": 0,
        }

        for priority, count in results:
            if priority in distribution:
                distribution[priority] = count

        return distribution

    def get_status_distribution(self, project_id: Optional[int] = None) -> Dict[str, int]:
        """Get distribution of tasks by status."""
        query = self.db.query(Task.status, func.count(Task.id))

        if project_id:
            query = query.filter(Task.project_id == project_id)

        query = query.group_by(Task.status)

        results = query.all()

        distribution = {
            "todo": 0,
            "in_progress": 0,
            "done": 0,
            "blocked": 0,
        }

        for status, count in results:
            if status in distribution:
                distribution[status] = count

        return distribution

    def calculateBurndownData(self, project_id: int, days: int = 30) -> List[Dict[str, Any]]:  # Deliberately camelCase
        """Calculate burndown chart data for a project.

        Args:
            project_id: Project ID
            days: Number of days to include

        Returns:
            List of daily data points
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        burndown_data = []

        for day_offset in range(days + 1):
            current_date = start_date + timedelta(days=day_offset)

            # Count tasks completed up to this date
            completed_count = (
                self.db.query(Task)
                .filter(
                    Task.project_id == project_id,
                    Task.status == "done",
                    Task.updated_at <= current_date,
                )
                .count()
            )

            # Count total tasks created up to this date
            total_count = (
                self.db.query(Task)
                .filter(Task.project_id == project_id, Task.created_at <= current_date)
                .count()
            )

            remaining = total_count - completed_count

            burndown_data.append(
                {
                    "date": current_date.strftime("%Y-%m-%d"),
                    "total_tasks": total_count,
                    "completed_tasks": completed_count,
                    "remaining_tasks": remaining,
                }
            )

        return burndown_data

    def get_user_performance_metrics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive performance metrics for a user.

        Args:
            user_id: User ID
            days: Number of days to analyze

        Returns:
            Dictionary of performance metrics
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Total assigned tasks
        total_assigned = (
            self.db.query(Task)
            .filter(Task.assigned_to == user_id, Task.created_at >= cutoff_date)
            .count()
        )

        # Completed tasks
        completed = (
            self.db.query(Task)
            .filter(
                Task.assigned_to == user_id,
                Task.status == "done",
                Task.updated_at >= cutoff_date,
            )
            .count()
        )

        # Overdue tasks
        overdue = (
            self.db.query(Task)
            .filter(
                Task.assigned_to == user_id,
                Task.status != "done",
                Task.due_date < datetime.utcnow(),
            )
            .count()
        )

        # In progress tasks
        in_progress = (
            self.db.query(Task)
            .filter(Task.assigned_to == user_id, Task.status == "in_progress")
            .count()
        )

        # Calculate metrics
        completion_rate = calculate_percentage(completed, total_assigned) if total_assigned > 0 else 0
        velocity = safe_divide(completed, days)

        return {
            "user_id": user_id,
            "period_days": days,
            "total_assigned": total_assigned,
            "completed": completed,
            "in_progress": in_progress,
            "overdue": overdue,
            "completion_rate": completion_rate,
            "velocity": velocity,
        }

    def get_project_health_score(self, project_id: int) -> float:
        """Calculate a health score for a project (0-100).

        Based on completion rate, overdue tasks, and task distribution.
        """
        tasks = self.db.query(Task).filter(Task.project_id == project_id).all()

        if not tasks:
            return 100.0  # New project is healthy

        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.status == "done")
        overdue_tasks = sum(
            1 for t in tasks if t.due_date and t.due_date < datetime.utcnow() and t.status != "done"
        )
        blocked_tasks = sum(1 for t in tasks if t.status == "blocked")

        # Calculate component scores
        completion_score = calculate_percentage(completed_tasks, total_tasks)

        # Penalize for overdue tasks
        overdue_penalty = min(50, overdue_tasks * 10)

        # Penalize for blocked tasks
        blocked_penalty = min(30, blocked_tasks * 5)

        # Calculate overall health (max 100)
        health_score = max(0, completion_score - overdue_penalty - blocked_penalty)

        return round(health_score, 2)

    def getTaskTrends(self, days: int = 30) -> Dict[str, List[int]]:  # Deliberately camelCase
        """Get task creation and completion trends over time.

        Returns daily counts for the past N days.
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        created_counts = []
        completed_counts = []

        for day_offset in range(days):
            current_date = start_date + timedelta(days=day_offset)
            next_date = current_date + timedelta(days=1)

            created = (
                self.db.query(Task)
                .filter(Task.created_at >= current_date, Task.created_at < next_date)
                .count()
            )

            completed = (
                self.db.query(Task)
                .filter(
                    Task.status == "done",
                    Task.updated_at >= current_date,
                    Task.updated_at < next_date,
                )
                .count()
            )

            created_counts.append(created)
            completed_counts.append(completed)

        return {
            "created": created_counts,
            "completed": completed_counts,
        }

    def calculate_team_metrics(self, project_id: int) -> Dict[str, Any]:
        """Calculate team-wide metrics for a project."""
        tasks = self.db.query(Task).filter(Task.project_id == project_id).all()

        # Group tasks by assignee
        assignee_tasks = defaultdict(list)
        unassigned_count = 0

        for task in tasks:
            if task.assigned_to:
                assignee_tasks[task.assigned_to].append(task)
            else:
                unassigned_count += 1

        # Calculate per-user metrics
        team_stats = []
        for user_id, user_tasks in assignee_tasks.items():
            completed = sum(1 for t in user_tasks if t.status == "done")
            total = len(user_tasks)

            team_stats.append(
                {
                    "user_id": user_id,
                    "assigned_tasks": total,
                    "completed_tasks": completed,
                    "completion_rate": calculate_percentage(completed, total),
                }
            )

        return {
            "project_id": project_id,
            "total_tasks": len(tasks),
            "unassigned_tasks": unassigned_count,
            "team_stats": team_stats,
        }

    def get_time_to_completion_stats(self, project_id: Optional[int] = None) -> Dict[str, float]:
        """Calculate time-to-completion statistics.

        Returns min, max, average, and median completion times in days.
        """
        query = self.db.query(Task).filter(Task.status == "done", Task.updated_at.isnot(None))

        if project_id:
            query = query.filter(Task.project_id == project_id)

        completed_tasks = query.all()

        if not completed_tasks:
            return {
                "min_days": 0.0,
                "max_days": 0.0,
                "avg_days": 0.0,
                "median_days": 0.0,
            }

        durations = []
        for task in completed_tasks:
            if task.updated_at and task.created_at:
                duration = (task.updated_at - task.created_at).total_seconds() / 86400  # Convert to days
                durations.append(duration)

        if not durations:
            return {
                "min_days": 0.0,
                "max_days": 0.0,
                "avg_days": 0.0,
                "median_days": 0.0,
            }

        durations.sort()
        median_index = len(durations) // 2

        return {
            "min_days": round(min(durations), 2),
            "max_days": round(max(durations), 2),
            "avg_days": round(sum(durations) / len(durations), 2),
            "median_days": round(durations[median_index], 2),
        }
