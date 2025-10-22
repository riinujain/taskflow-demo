"""Email client for sending notifications (simulated)."""

import logging
from typing import List, Optional

from taskflow.utils.config import settings

logger = logging.getLogger(__name__)


class EmailClient:
    """Email client that simulates sending emails.

    In a real application, this would integrate with SendGrid, AWS SES, etc.
    """

    def __init__(self):
        self.enabled = settings.EMAIL_ENABLED
        self.from_address = settings.EMAIL_FROM

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: Optional[str] = None,
    ) -> bool:
        """Send an email.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Plain text body
            html: Optional HTML body

        Returns:
            True if email was "sent" successfully
        """
        if not self.enabled:
            logger.info(f"Email disabled. Would send to {to}: {subject}")
            return False

        # Simulate sending
        logger.info(f"📧 Sending email to {to}")
        logger.info(f"   Subject: {subject}")
        logger.info(f"   Body: {body[:100]}...")

        return True

    def send_bulk_email(
        self,
        recipients: List[str],
        subject: str,
        body: str,
    ) -> int:
        """Send the same email to multiple recipients.

        Returns:
            Number of emails successfully sent
        """
        count = 0
        for recipient in recipients:
            if self.send_email(recipient, subject, body):
                count += 1
        return count

    def send_template_email(
        self,
        to: str,
        template_name: str,
        template_data: dict,
    ) -> bool:
        """Send a templated email.

        Args:
            to: Recipient
            template_name: Name of template
            template_data: Data to populate template

        Returns:
            True if successful
        """
        # Simulate template rendering
        subject = f"TaskFlow: {template_name.replace('_', ' ').title()}"
        body = self._render_template(template_name, template_data)
        return self.send_email(to, subject, body)

    def _render_template(self, template_name: str, data: dict) -> str:
        """Render a simple email template.

        In production, use a real templating engine.
        """
        templates = {
            "task_reminder": """
Hi {user_name},

This is a reminder that the following task is due soon:

Task: {task_title}
Due Date: {due_date}
Priority: {priority}

Please complete it at your earliest convenience.

Best regards,
TaskFlow Team
            """,
            "daily_summary": """
Hi {user_name},

Here's your daily summary for {date}:

Tasks Completed: {completed_count}
Tasks In Progress: {in_progress_count}
Overdue Tasks: {overdue_count}

Keep up the great work!

Best regards,
TaskFlow Team
            """,
            "welcome": """
Welcome to TaskFlow, {user_name}!

Your account has been created successfully.

Get started by creating your first project!

Best regards,
TaskFlow Team
            """,
        }

        template = templates.get(template_name, "")
        return template.format(**data)


# Global email client instance
email_client = EmailClient()


# Convenience functions
def send_welcome_email(user_email: str, user_name: str) -> bool:
    """Send welcome email to new user."""
    return email_client.send_template_email(
        to=user_email,
        template_name="welcome",
        template_data={"user_name": user_name},
    )


def send_task_reminder_email(
    user_email: str,
    user_name: str,
    task_title: str,
    due_date: str,
    priority: str,
) -> bool:
    """Send task reminder email."""
    return email_client.send_template_email(
        to=user_email,
        template_name="task_reminder",
        template_data={
            "user_name": user_name,
            "task_title": task_title,
            "due_date": due_date,
            "priority": priority,
        },
    )
