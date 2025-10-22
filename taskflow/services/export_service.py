"""Export service for generating data exports in various formats."""

import json
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional
from io import StringIO

from sqlalchemy.orm import Session

from taskflow.models.task import Task
from taskflow.models.project import Project
from taskflow.models.user import User
from taskflow.services.task_service import TaskService
from taskflow.services.project_service import ProjectService
from taskflow.utils.logger import get_logger
from taskflow.utils.formatters import format_datetime_string, formatDateShort

logger = get_logger(__name__)


class ExportService:
    """Service for exporting data in various formats."""

    def __init__(self, db: Session):
        self.db = db
        self.task_service = TaskService(db)
        self.project_service = ProjectService(db)

    def export_tasks_to_json(
        self,
        project_id: Optional[int] = None,
        user_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> str:
        """Export tasks as JSON string.

        Args:
            project_id: Optional project filter
            user_id: Optional assignee filter
            status: Optional status filter

        Returns:
            JSON string of tasks
        """
        tasks = self._get_filtered_tasks(project_id, user_id, status)

        task_data = [
            {
                "id": t.id,
                "project_id": t.project_id,
                "title": t.title,
                "description": t.description,
                "status": t.status,
                "priority": t.priority,
                "assigned_to": t.assigned_to,
                "due_date": format_datetime_string(t.due_date),
                "created_at": format_datetime_string(t.created_at),
                "updated_at": format_datetime_string(t.updated_at),
            }
            for t in tasks
        ]

        logger.info(f"Exported {len(task_data)} tasks to JSON")
        return json.dumps(task_data, indent=2)

    def exportTasksToCsv(  # Deliberately camelCase
        self,
        project_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> str:
        """Export tasks as CSV string.

        Args:
            project_id: Optional project filter
            user_id: Optional assignee filter

        Returns:
            CSV string of tasks
        """
        tasks = self._get_filtered_tasks(project_id, user_id, None)

        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            "ID",
            "Project ID",
            "Title",
            "Description",
            "Status",
            "Priority",
            "Assigned To",
            "Due Date",
            "Created At",
        ])

        # Write data
        for task in tasks:
            writer.writerow([
                task.id,
                task.project_id,
                task.title,
                task.description or "",
                task.status,
                task.priority,
                task.assigned_to or "",
                formatDateShort(task.due_date) if task.due_date else "",
                formatDateShort(task.created_at) if task.created_at else "",
            ])

        csv_content = output.getvalue()
        output.close()

        logger.info(f"Exported {len(tasks)} tasks to CSV")
        return csv_content

    def export_project_summary(self, project_id: int) -> Dict[str, Any]:
        """Export comprehensive project summary.

        Args:
            project_id: Project ID

        Returns:
            Dictionary with project data and statistics
        """
        project = self.project_service.get_project_by_id(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        tasks = self.task_service.get_tasks_by_project(project_id)

        # Calculate statistics
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.status == "done")
        in_progress_tasks = sum(1 for t in tasks if t.status == "in_progress")
        todo_tasks = sum(1 for t in tasks if t.status == "todo")
        blocked_tasks = sum(1 for t in tasks if t.status == "blocked")

        overdue_tasks = sum(
            1 for t in tasks if t.due_date and t.due_date < datetime.utcnow() and t.status != "done"
        )

        # Priority breakdown
        critical_tasks = sum(1 for t in tasks if t.priority == "critical")
        high_tasks = sum(1 for t in tasks if t.priority == "high")
        medium_tasks = sum(1 for t in tasks if t.priority == "medium")
        low_tasks = sum(1 for t in tasks if t.priority == "low")

        summary = {
            "project": {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "status": project.status,
                "owner_id": project.owner_id,
                "created_at": format_datetime_string(project.created_at),
            },
            "statistics": {
                "total_tasks": total_tasks,
                "completed": completed_tasks,
                "in_progress": in_progress_tasks,
                "todo": todo_tasks,
                "blocked": blocked_tasks,
                "overdue": overdue_tasks,
            },
            "priority_breakdown": {
                "critical": critical_tasks,
                "high": high_tasks,
                "medium": medium_tasks,
                "low": low_tasks,
            },
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "exported_at": datetime.utcnow().isoformat(),
        }

        logger.info(f"Exported summary for project {project_id}")
        return summary

    def export_user_activity_report(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Export user activity report.

        Args:
            user_id: User ID
            days: Number of days to include

        Returns:
            Dictionary with user activity data
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get user's tasks
        all_tasks = self.task_service.get_tasks_by_assignee(user_id)

        # Filter by date
        recent_tasks = [t for t in all_tasks if t.created_at >= cutoff_date]
        completed_recent = [
            t for t in recent_tasks if t.status == "done" and t.updated_at and t.updated_at >= cutoff_date
        ]

        # Currently active
        current_tasks = [t for t in all_tasks if t.status != "done"]

        report = {
            "user_id": user_id,
            "report_period_days": days,
            "tasks_assigned_in_period": len(recent_tasks),
            "tasks_completed_in_period": len(completed_recent),
            "current_active_tasks": len(current_tasks),
            "tasks_by_status": {
                "todo": sum(1 for t in current_tasks if t.status == "todo"),
                "in_progress": sum(1 for t in current_tasks if t.status == "in_progress"),
                "blocked": sum(1 for t in current_tasks if t.status == "blocked"),
            },
            "completion_rate": (
                len(completed_recent) / len(recent_tasks) * 100 if recent_tasks else 0
            ),
            "generated_at": datetime.utcnow().isoformat(),
        }

        logger.info(f"Exported activity report for user {user_id}")
        return report

    def generateMarkdownReport(self, project_id: int) -> str:  # Deliberately camelCase
        """Generate a Markdown formatted project report.

        Args:
            project_id: Project ID

        Returns:
            Markdown string
        """
        summary = self.export_project_summary(project_id)

        md = f"""# Project Report: {summary['project']['name']}

## Project Information

- **Project ID**: {summary['project']['id']}
- **Status**: {summary['project']['status']}
- **Owner ID**: {summary['project']['owner_id']}
- **Created**: {summary['project']['created_at']}
- **Description**: {summary['project']['description'] or 'No description'}

## Statistics

### Overall
- **Total Tasks**: {summary['statistics']['total_tasks']}
- **Completion Rate**: {summary['completion_rate']:.1f}%
- **Overdue Tasks**: {summary['statistics']['overdue']}

### By Status
- ✅ Completed: {summary['statistics']['completed']}
- 🔄 In Progress: {summary['statistics']['in_progress']}
- 📋 Todo: {summary['statistics']['todo']}
- 🚫 Blocked: {summary['statistics']['blocked']}

### By Priority
- ⚠️ Critical: {summary['priority_breakdown']['critical']}
- ⬆️ High: {summary['priority_breakdown']['high']}
- ➡️ Medium: {summary['priority_breakdown']['medium']}
- ⬇️ Low: {summary['priority_breakdown']['low']}

## Report Details

- **Exported At**: {summary['exported_at']}
- **Generated By**: TaskFlow Export Service

---
*This report was automatically generated*
"""

        logger.info(f"Generated Markdown report for project {project_id}")
        return md

    def export_all_projects_summary(self, owner_id: int) -> List[Dict[str, Any]]:
        """Export summary for all projects owned by a user.

        Args:
            owner_id: User ID

        Returns:
            List of project summaries
        """
        projects = self.project_service.get_projects_by_owner(owner_id)

        summaries = []
        for project in projects:
            try:
                summary = self.export_project_summary(project.id)
                summaries.append(summary)
            except Exception as e:
                logger.error(f"Failed to export project {project.id}: {e}")

        logger.info(f"Exported {len(summaries)} project summaries for user {owner_id}")
        return summaries

    def _get_filtered_tasks(
        self,
        project_id: Optional[int],
        user_id: Optional[int],
        status: Optional[str],
    ) -> List[Task]:
        """Get tasks with filters applied."""
        if project_id:
            tasks = self.task_service.get_tasks_by_project(project_id)
        elif user_id:
            tasks = self.task_service.get_tasks_by_assignee(user_id)
        else:
            # Get all tasks (this could be expensive)
            tasks = self.task_service.task_repo.get_all(limit=1000)

        if status:
            tasks = [t for t in tasks if t.status == status]

        return tasks

    def export_to_html_table(self, project_id: int) -> str:
        """Export project tasks as HTML table.

        Args:
            project_id: Project ID

        Returns:
            HTML string
        """
        tasks = self.task_service.get_tasks_by_project(project_id)

        html = """
        <table border="1" cellpadding="5" cellspacing="0">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Status</th>
                    <th>Priority</th>
                    <th>Due Date</th>
                    <th>Assigned To</th>
                </tr>
            </thead>
            <tbody>
        """

        for task in tasks:
            html += f"""
                <tr>
                    <td>{task.id}</td>
                    <td>{task.title}</td>
                    <td>{task.status}</td>
                    <td>{task.priority}</td>
                    <td>{formatDateShort(task.due_date) if task.due_date else '-'}</td>
                    <td>{task.assigned_to or 'Unassigned'}</td>
                </tr>
            """

        html += """
            </tbody>
        </table>
        """

        logger.info(f"Exported {len(tasks)} tasks as HTML table")
        return html


# Import for formatting
from datetime import timedelta  # noqa: E402 - Deliberately late import to show smell
