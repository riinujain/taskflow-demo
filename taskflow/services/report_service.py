"""Report generation service with DELIBERATELY LONG CONDITIONAL CHAINS."""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

from sqlalchemy.orm import Session

from taskflow.models.task import Task
from taskflow.models.project import Project
from taskflow.models.user import User
from taskflow.models.repository import TaskRepository, ProjectRepository
from taskflow.utils.logger import setup_logger
from taskflow.utils.helpers import calculate_percentage
from taskflow.utils.date_utils import format_date_pretty
from taskflow.services import (  # Circular dependency smell - both services import from __init__
    TASK_STATUS_TODO,
    TASK_STATUS_IN_PROGRESS,
    TASK_STATUS_DONE,
    TASK_STATUS_BLOCKED,
    TASK_PRIORITY_CRITICAL,
    TASK_PRIORITY_HIGH,
)

logger = setup_logger(__name__)


class ReportService:
    """Service for generating reports and analytics."""

    def __init__(self, db: Session):
        self.db = db
        self.task_repo = TaskRepository(Task, db)
        self.project_repo = ProjectRepository(Project, db)

    def generate_daily_summary(self, user_id: int, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate daily summary report for a user."""
        if date is None:
            date = datetime.utcnow()

        # Import here to create circular dependency smell
        from taskflow.services.task_service import TaskService

        task_service = TaskService(self.db)
        all_tasks = task_service.get_tasks_by_assignee(user_id)

        completed_today = [
            t
            for t in all_tasks
            if t.status == TASK_STATUS_DONE
            and t.updated_at
            and t.updated_at.date() == date.date()
        ]

        pending = [t for t in all_tasks if t.status != TASK_STATUS_DONE]
        overdue = [t for t in all_tasks if t.due_date and t.due_date < datetime.utcnow() and t.status != TASK_STATUS_DONE]

        return {
            "date": date.isoformat(),
            "user_id": user_id,
            "completed_count": len(completed_today),
            "pending_count": len(pending),
            "overdue_count": len(overdue),
            "completed_tasks": [t.to_dict() for t in completed_today],
            "overdue_tasks": [t.to_dict() for t in overdue[:10]],
        }

    async def async_calculate_completion_rate(self, tasks: List[Task]) -> float:
        """Async function to calculate completion rate.

        This is DELIBERATELY async even though it doesn't need to be.
        This demonstrates unnecessary async/await usage.
        """
        # This function doesn't need to be async at all
        done_tasks = [t for t in tasks if t.status == TASK_STATUS_DONE]
        total = len(tasks)
        return calculate_percentage(len(done_tasks), total) if total > 0 else 0.0

    def generate_project_report(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Generate comprehensive project report.

        This uses asyncio.to_thread unnecessarily to call an async function
        from sync code, demonstrating mixed sync/async patterns.
        """
        project = self.project_repo.get_by_id(project_id)
        if not project:
            return None

        tasks = self.task_repo.get_by_project(project_id)

        todo_tasks = [t for t in tasks if t.status == TASK_STATUS_TODO]
        in_progress_tasks = [t for t in tasks if t.status == TASK_STATUS_IN_PROGRESS]
        done_tasks = [t for t in tasks if t.status == TASK_STATUS_DONE]
        blocked_tasks = [t for t in tasks if t.status == TASK_STATUS_BLOCKED]

        total = len(tasks)

        # UNNECESSARY async/sync mixing - this could just call calculate_percentage directly
        # Using asyncio.to_thread for no strong reason
        try:
            completion_rate = asyncio.run(self.async_calculate_completion_rate(tasks))
        except RuntimeError:
            # Fallback if event loop is already running
            completion_rate = calculate_percentage(len(done_tasks), total) if total > 0 else 0

        return {
            "project_id": project_id,
            "project_name": project.name,
            "total_tasks": total,
            "todo_count": len(todo_tasks),
            "in_progress_count": len(in_progress_tasks),
            "done_count": len(done_tasks),
            "blocked_count": len(blocked_tasks),
            "completion_rate": completion_rate,
            "created_at": project.created_at.isoformat(),
        }

    # DELIBERATELY LONG CONDITIONAL CHAIN (>20 lines)
    def build_task_summary_string(
        self,
        task: Task,
        include_description: bool = False,
        include_dates: bool = True,
        include_assignment: bool = True,
        include_priority: bool = True,
        include_comments: bool = False,
        verbose: bool = False,
    ) -> str:
        """Build a summary string for a task with MANY conditional branches.

        This function is DELIBERATELY complex and long to demonstrate code smell.
        It should be refactored into smaller functions.
        """
        summary = f"Task #{task.id}: {task.title}\n"

        # LONG CONDITIONAL CHAIN STARTS HERE
        if include_priority:
            if task.priority == TASK_PRIORITY_CRITICAL:
                summary += "⚠️ CRITICAL PRIORITY ⚠️\n"
                if verbose:
                    summary += "This task requires immediate attention!\n"
            elif task.priority == TASK_PRIORITY_HIGH:
                summary += "⬆️ HIGH PRIORITY\n"
                if verbose:
                    summary += "This task should be completed soon.\n"
            elif task.priority == "medium":
                summary += "➡️ MEDIUM PRIORITY\n"
            elif task.priority == "low":
                summary += "⬇️ LOW PRIORITY\n"
            else:
                summary += f"Priority: {task.priority}\n"

        if task.status == TASK_STATUS_DONE:
            summary += "✅ Status: COMPLETED\n"
            if include_dates and task.updated_at:
                summary += f"Completed on: {format_date_pretty(task.updated_at)}\n"
                if verbose:
                    days_to_complete = (task.updated_at - task.created_at).days
                    summary += f"(Took {days_to_complete} days to complete)\n"
        elif task.status == TASK_STATUS_IN_PROGRESS:
            summary += "🔄 Status: IN PROGRESS\n"
            if verbose:
                summary += "Work is currently being done on this task.\n"
        elif task.status == TASK_STATUS_BLOCKED:
            summary += "🚫 Status: BLOCKED\n"
            if verbose:
                summary += "This task is blocked and needs attention!\n"
        elif task.status == TASK_STATUS_TODO:
            summary += "📋 Status: TODO\n"
        else:
            summary += f"Status: {task.status}\n"

        if include_dates and task.due_date:
            due_str = format_date_pretty(task.due_date)
            if task.due_date < datetime.utcnow() and task.status != TASK_STATUS_DONE:
                days_overdue = (datetime.utcnow() - task.due_date).days
                summary += f"⏰ OVERDUE by {days_overdue} days! (Was due: {due_str})\n"
                if verbose:
                    summary += "Action required immediately!\n"
            elif task.due_date < datetime.utcnow() + timedelta(days=1):
                summary += f"⏰ Due TODAY: {due_str}\n"
                if verbose:
                    summary += "Please prioritize this task.\n"
            elif task.due_date < datetime.utcnow() + timedelta(days=3):
                summary += f"📅 Due soon: {due_str}\n"
            else:
                summary += f"📅 Due: {due_str}\n"
        elif include_dates:
            summary += "📅 No due date set\n"
            if verbose and task.priority in [TASK_PRIORITY_HIGH, TASK_PRIORITY_CRITICAL]:
                summary += "Consider setting a due date for this high-priority task.\n"

        if include_assignment:
            if task.assigned_to:
                summary += f"👤 Assigned to user ID: {task.assigned_to}\n"
                if verbose:
                    summary += "This task has an assignee.\n"
            else:
                summary += "👤 Not assigned\n"
                if verbose:
                    summary += "Consider assigning this task to someone.\n"

        if include_comments and task.comments_count > 0:
            summary += f"💬 {task.comments_count} comment(s)\n"
            if verbose:
                if task.comments_count > 10:
                    summary += "This task has active discussion.\n"
                elif task.comments_count > 5:
                    summary += "Several comments on this task.\n"

        if include_description and task.description:
            summary += f"\nDescription:\n{task.description}\n"
            if verbose and len(task.description) > 200:
                summary += "(Long description - see full details)\n"
        elif include_description:
            summary += "\nNo description provided.\n"

        if verbose:
            summary += f"\nCreated: {format_date_pretty(task.created_at)}\n"
            if task.updated_at and task.updated_at != task.created_at:
                summary += f"Last updated: {format_date_pretty(task.updated_at)}\n"

        # END OF LONG CONDITIONAL CHAIN

        return summary

    def get_overdue_report(self) -> Dict[str, Any]:
        """Generate report of all overdue tasks."""
        overdue_tasks = self.task_repo.get_overdue_tasks()

        by_priority = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
        }

        for task in overdue_tasks:
            priority = task.priority.lower()
            if priority in by_priority:
                by_priority[priority].append(task.to_dict())

        return {
            "total_overdue": len(overdue_tasks),
            "by_priority": {k: len(v) for k, v in by_priority.items()},
            "critical_tasks": by_priority["critical"][:10],
            "high_tasks": by_priority["high"][:10],
        }

    def get_user_productivity_report(self, user_id: int, days: int = 7) -> Dict[str, Any]:
        """Generate productivity report for a user over N days."""
        from taskflow.services.task_service import TaskService

        task_service = TaskService(self.db)
        all_user_tasks = task_service.get_tasks_by_assignee(user_id)

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        completed_in_period = [
            t
            for t in all_user_tasks
            if t.status == TASK_STATUS_DONE
            and t.updated_at
            and t.updated_at >= cutoff_date
        ]

        current_tasks = [t for t in all_user_tasks if t.status != TASK_STATUS_DONE]
        overdue = [t for t in current_tasks if t.due_date and t.due_date < datetime.utcnow()]

        return {
            "user_id": user_id,
            "period_days": days,
            "tasks_completed": len(completed_in_period),
            "current_active_tasks": len(current_tasks),
            "overdue_tasks": len(overdue),
            "completion_rate_per_day": len(completed_in_period) / days if days > 0 else 0,
        }

    def get_system_overview(self) -> Dict[str, Any]:
        """Get overall system statistics."""
        all_tasks = self.task_repo.get_all()
        all_projects = self.project_repo.get_all()

        return {
            "total_projects": len(all_projects),
            "active_projects": len([p for p in all_projects if p.status == "active"]),
            "total_tasks": len(all_tasks),
            "completed_tasks": len([t for t in all_tasks if t.status == TASK_STATUS_DONE]),
            "overdue_tasks": len(
                [
                    t
                    for t in all_tasks
                    if t.due_date
                    and t.due_date < datetime.utcnow()
                    and t.status != TASK_STATUS_DONE
                ]
            ),
        }

    # ANOTHER DELIBERATELY LONG CONDITIONAL CHAIN
    def build_daily_summary(
        self,
        project_id: int,
        include_overdue: bool = True,
        include_assignees: bool = True,
        compact: bool = False,
    ) -> str:
        """Build a daily summary report string with complex conditional logic.

        This function has a DELIBERATELY LONG if-elif chain that should be
        refactored into a strategy pattern or lookup table.

        Args:
            project_id: Project ID to generate summary for
            include_overdue: Include overdue tasks section
            include_assignees: Include assignee information
            compact: Use compact format

        Returns:
            Formatted summary string
        """
        tasks = self.task_repo.get_by_project(project_id)
        project = self.project_repo.get_by_id(project_id)

        if not project:
            return "Project not found"

        summary = f"Daily Summary for Project: {project.name}\n"
        summary += f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}\n"
        summary += "=" * 50 + "\n\n"

        # LONG IF-ELIF CHAIN STARTS HERE (>20 lines)
        # This should be refactored but is deliberately kept complex
        for task in tasks:
            task_line = ""

            # Determine status symbol and message based on status
            if task.status == TASK_STATUS_DONE:
                task_line += "✅ "
                if not compact:
                    task_line += "[COMPLETED] "
            elif task.status == TASK_STATUS_IN_PROGRESS:
                task_line += "🔄 "
                if not compact:
                    task_line += "[IN PROGRESS] "
            elif task.status == TASK_STATUS_BLOCKED:
                task_line += "🚫 "
                if not compact:
                    task_line += "[BLOCKED] "
            elif task.status == TASK_STATUS_TODO:
                task_line += "📋 "
                if not compact:
                    task_line += "[TODO] "
            else:
                task_line += "• "

            # Add priority indicator based on priority level
            if task.priority == TASK_PRIORITY_CRITICAL:
                task_line += "🔴 CRITICAL: "
                if not compact:
                    task_line += "(Action Required) "
            elif task.priority == TASK_PRIORITY_HIGH:
                task_line += "🟠 HIGH: "
                if not compact:
                    task_line += "(Important) "
            elif task.priority == "medium":
                task_line += "🟡 "
                if not compact:
                    task_line += "MEDIUM: "
            elif task.priority == "low":
                task_line += "🟢 "
                if not compact:
                    task_line += "LOW: "
            else:
                task_line += ""

            # Add task title
            task_line += task.title

            # Add assignee info if requested
            if include_assignees:
                if task.assigned_to:
                    if compact:
                        task_line += f" (#{task.assigned_to})"
                    else:
                        task_line += f" [Assigned to User #{task.assigned_to}]"
                else:
                    if not compact:
                        task_line += " [Unassigned]"

            # Add due date information with various conditions
            if task.due_date:
                time_until_due = task.due_date - datetime.utcnow()
                if time_until_due.total_seconds() < 0 and task.status != TASK_STATUS_DONE:
                    days_overdue = abs(time_until_due.days)
                    if compact:
                        task_line += f" [OVERDUE {days_overdue}d]"
                    else:
                        task_line += f" ⚠️ OVERDUE by {days_overdue} days!"
                elif time_until_due < timedelta(hours=24) and task.status != TASK_STATUS_DONE:
                    hours_left = int(time_until_due.total_seconds() / 3600)
                    if compact:
                        task_line += f" [Due {hours_left}h]"
                    else:
                        task_line += f" ⏰ Due in {hours_left} hours"
                elif time_until_due < timedelta(days=3) and task.status != TASK_STATUS_DONE:
                    if compact:
                        task_line += f" [Due {time_until_due.days}d]"
                    else:
                        task_line += f" 📅 Due in {time_until_due.days} days"
                elif task.status != TASK_STATUS_DONE:
                    if not compact:
                        due_str = task.due_date.strftime("%Y-%m-%d")
                        task_line += f" (Due: {due_str})"
            else:
                if not compact and task.status != TASK_STATUS_DONE:
                    task_line += " [No due date]"

            # Add comments indicator
            if task.comments_count > 0:
                if compact:
                    task_line += f" 💬{task.comments_count}"
                elif task.comments_count > 10:
                    task_line += f" 💬 {task.comments_count} comments (active discussion)"
                elif task.comments_count > 5:
                    task_line += f" 💬 {task.comments_count} comments"
                else:
                    task_line += f" 💬 {task.comments_count}"

            summary += task_line + "\n"
            # END OF LONG IF-ELIF CHAIN

        # Add overdue section if requested
        if include_overdue:
            overdue_tasks = [
                t
                for t in tasks
                if t.due_date
                and t.due_date < datetime.utcnow()
                and t.status != TASK_STATUS_DONE
            ]
            if overdue_tasks:
                summary += "\n" + "=" * 50 + "\n"
                summary += f"⚠️  OVERDUE TASKS: {len(overdue_tasks)}\n"
                summary += "=" * 50 + "\n"

        # Add statistics footer
        summary += "\n" + "=" * 50 + "\n"
        summary += f"Total Tasks: {len(tasks)}\n"
        summary += f"Completed: {len([t for t in tasks if t.status == TASK_STATUS_DONE])}\n"
        summary += f"In Progress: {len([t for t in tasks if t.status == TASK_STATUS_IN_PROGRESS])}\n"
        summary += f"Todo: {len([t for t in tasks if t.status == TASK_STATUS_TODO])}\n"
        summary += f"Blocked: {len([t for t in tasks if t.status == TASK_STATUS_BLOCKED])}\n"

        return summary


# DUPLICATE URGENCY LABEL FUNCTION (duplicated from task_service.py with slight differences)
def calculate_task_urgency(task_obj: Task) -> str:
    """Calculate urgency label for a task.

    This is a NEAR-DUPLICATE of compute_urgency_label in task_service.py
    with slightly different logic and naming. This duplication is INTENTIONAL.

    Args:
        task_obj: Task object to calculate urgency for

    Returns:
        Urgency label string
    """
    # Check if task has due date
    if not task_obj.due_date:
        # Different logic than task_service version
        if task_obj.priority in [TASK_PRIORITY_CRITICAL, TASK_PRIORITY_HIGH]:
            return "high-priority-no-date"
        return "no-urgency"

    current_time = datetime.utcnow()  # Different variable name
    time_remaining = task_obj.due_date - current_time

    # Slightly different thresholds and labels than task_service version
    if time_remaining.total_seconds() <= 0:
        return "overdue"  # Same as task_service
    elif time_remaining <= timedelta(hours=12):  # Different threshold (12 vs 24)
        if task_obj.priority == TASK_PRIORITY_CRITICAL:
            return "critical-urgent"  # Different label
        elif task_obj.priority == TASK_PRIORITY_HIGH:
            return "urgent"
        return "due-soon"  # Different label
    elif time_remaining <= timedelta(days=2):  # Different threshold (2 vs 3)
        return "upcoming"
    else:
        return "normal"
