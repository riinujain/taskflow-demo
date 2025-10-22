"""Notification service for sending reminders and alerts.

This module contains DELIBERATE DUPLICATE FUNCTIONS to demonstrate code smell.
"""

from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from taskflow.models.task import Task
from taskflow.models.user import User
from taskflow.utils.email_client import email_client
from taskflow.utils.date_utils import format_datetime, format_date_pretty
from taskflow.utils.helpers import format_date_simple
from taskflow.utils.logger import get_logger

logger = get_logger(__name__)


class NotificationService:
    """Service for managing notifications and reminders."""

    def __init__(self, db: Session):
        self.db = db

    # DELIBERATE DUPLICATE #1: First version of task reminder
    def send_task_reminder(self, task: Task, user: User) -> bool:
        """Send a task reminder to a user.

        This is the first version of task reminder function.
        There's another similar function below with slight differences.

        Args:
            task: Task object to remind about
            user: User to send reminder to

        Returns:
            True if reminder sent successfully
        """
        if not task or not user:
            logger.error("Invalid task or user provided")
            return False

        # Use one date formatting style
        due_date_str = format_datetime(task.due_date) if task.due_date else "No due date"

        subject = f"Reminder: {task.title}"
        body = f"""
Hello {user.name},

This is a reminder about your task:

Task: {task.title}
Status: {task.status}
Priority: {task.priority}
Due Date: {due_date_str}

Please complete this task at your earliest convenience.

Best regards,
TaskFlow
        """

        success = email_client.send_email(
            to=user.email,
            subject=subject,
            body=body,
        )

        if success:
            logger.info(f"Task reminder sent to {user.email} for task {task.id}")
        else:
            logger.error(f"Failed to send task reminder to {user.email}")

        return success

    # DELIBERATE DUPLICATE #2: Second version of task reminder
    def remind_task_due(
        self,
        task_obj: Task,
        user_obj: User,
        urgent: bool = False,
    ) -> bool:
        """Send a task due reminder to user.

        This is nearly identical to send_task_reminder but with slight variations.
        This duplication is INTENTIONAL for demo purposes.

        Args:
            task_obj: The task to remind about
            user_obj: The user to notify
            urgent: Whether this is an urgent reminder

        Returns:
            True if sent successfully
        """
        if not task_obj or not user_obj:
            return False

        # Use a different date formatting style
        if task_obj.due_date:
            due_str = format_date_pretty(task_obj.due_date)
        else:
            due_str = "Not set"

        urgency_prefix = "URGENT: " if urgent else ""
        email_subject = f"{urgency_prefix}Task Reminder: {task_obj.title}"

        email_body = f"""
Hi {user_obj.name},

{'⚠️ URGENT REMINDER ⚠️' if urgent else 'Reminder'}

Task: {task_obj.title}
Priority: {task_obj.priority.upper()}
Status: {task_obj.status}
Due: {due_str}

{'This task requires your immediate attention!' if urgent else 'Please work on this task.'}

Thank you,
TaskFlow Team
        """

        result = email_client.send_email(
            to=user_obj.email,
            subject=email_subject,
            body=email_body,
        )

        if result:
            logger.info(f"Due reminder sent for task {task_obj.id}")

        return result

    def send_overdue_notification(self, task: Task, user: User) -> bool:
        """Send notification for overdue task."""
        if not task or not user or not task.due_date:
            return False

        days_overdue = (datetime.utcnow() - task.due_date).days

        subject = f"OVERDUE: {task.title}"
        body = f"""
Hello {user.name},

Your task is overdue by {days_overdue} day(s):

Task: {task.title}
Priority: {task.priority}
Was Due: {format_date_simple(task.due_date)}

Please complete this task as soon as possible!

Best regards,
TaskFlow
        """

        return email_client.send_email(user.email, subject, body)

    def send_daily_summary(
        self,
        user: User,
        pending_tasks: List[Task],
        completed_tasks: List[Task],
        overdue_tasks: List[Task],
    ) -> bool:
        """Send daily summary to user.

        Args:
            user: User to send summary to
            pending_tasks: List of pending tasks
            completed_tasks: List of completed tasks today
            overdue_tasks: List of overdue tasks

        Returns:
            True if sent successfully
        """
        subject = f"Daily Summary - {datetime.utcnow().strftime('%B %d, %Y')}"

        body = f"""
Hello {user.name},

Here's your daily task summary:

✅ Completed Today: {len(completed_tasks)}
📋 Pending Tasks: {len(pending_tasks)}
⚠️ Overdue Tasks: {len(overdue_tasks)}

"""

        if overdue_tasks:
            body += "\nOverdue Tasks:\n"
            for task in overdue_tasks[:5]:  # Limit to 5
                body += f"  - {task.title} (Due: {format_date_simple(task.due_date)})\n"

        if pending_tasks:
            body += "\nHigh Priority Pending:\n"
            high_priority = [t for t in pending_tasks if t.priority in ["high", "critical"]]
            for task in high_priority[:5]:
                body += f"  - {task.title} ({task.priority})\n"

        body += "\n\nKeep up the great work!\n\nBest regards,\nTaskFlow"

        return email_client.send_email(user.email, subject, body)

    def send_assignment_notification(
        self,
        task: Task,
        assignee: User,
        assigner: Optional[User] = None,
    ) -> bool:
        """Notify user that they've been assigned a task."""
        assigner_name = assigner.name if assigner else "Someone"

        subject = f"New Task Assigned: {task.title}"
        body = f"""
Hello {assignee.name},

{assigner_name} has assigned you a new task:

Task: {task.title}
Priority: {task.priority}
Due Date: {format_date_pretty(task.due_date) if task.due_date else 'Not set'}

Description:
{task.description or 'No description provided'}

Best regards,
TaskFlow
        """

        return email_client.send_email(assignee.email, subject, body)

    def notify_task_completion(self, task: Task, project_owner: User) -> bool:
        """Notify project owner that a task was completed."""
        subject = f"Task Completed: {task.title}"
        body = f"""
Hello {project_owner.name},

A task in your project has been completed:

Task: {task.title}
Completed: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}

Great progress!

Best regards,
TaskFlow
        """

        return email_client.send_email(project_owner.email, subject, body)

    def send_bulk_reminders(self, task_user_pairs: List[tuple]) -> int:
        """Send reminders for multiple task-user pairs.

        Args:
            task_user_pairs: List of (task, user) tuples

        Returns:
            Number of reminders sent successfully
        """
        count = 0
        for task, user in task_user_pairs:
            # Randomly use either duplicate function to show inconsistency
            import random

            if random.choice([True, False]):
                if self.send_task_reminder(task, user):
                    count += 1
            else:
                if self.remind_task_due(task, user):
                    count += 1

        logger.info(f"Sent {count} bulk reminders")
        return count
