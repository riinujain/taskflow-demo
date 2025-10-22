"""Webhook service for external integrations (simulated)."""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

from sqlalchemy.orm import Session

from taskflow.models.task import Task
from taskflow.models.project import Project
from taskflow.utils.logger import get_logger
from taskflow.utils.helpers import generate_random_string

logger = get_logger(__name__)


class WebhookEvent(str, Enum):
    """Webhook event types."""

    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_DELETED = "task.deleted"
    TASK_COMPLETED = "task.completed"
    PROJECT_CREATED = "project.created"
    PROJECT_UPDATED = "project.updated"
    PROJECT_DELETED = "project.deleted"
    USER_REGISTERED = "user.registered"


class WebhookService:
    """Service for managing webhooks and sending webhook events."""

    def __init__(self, db: Session):
        self.db = db
        self.registered_webhooks: List[Dict[str, Any]] = []

    def register_webhook(
        self,
        url: str,
        events: List[str],
        secret: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Register a new webhook endpoint.

        Args:
            url: Webhook URL
            events: List of event types to subscribe to
            secret: Optional secret for signature verification

        Returns:
            Registered webhook configuration
        """
        webhook_id = generate_random_string(16)

        webhook = {
            "id": webhook_id,
            "url": url,
            "events": events,
            "secret": secret or generate_random_string(32),
            "created_at": datetime.utcnow().isoformat(),
            "active": True,
        }

        self.registered_webhooks.append(webhook)
        logger.info(f"Webhook registered: {webhook_id} for {url}")

        return webhook

    def sendWebhookEvent(  # Deliberately camelCase
        self,
        event_type: str,
        payload: Dict[str, Any],
    ) -> int:
        """Send webhook event to all registered endpoints.

        Args:
            event_type: Type of event
            payload: Event data

        Returns:
            Number of webhooks triggered
        """
        triggered_count = 0

        for webhook in self.registered_webhooks:
            if not webhook["active"]:
                continue

            if event_type not in webhook["events"]:
                continue

            # Simulate sending webhook
            self._send_webhook_request(
                url=webhook["url"],
                event_type=event_type,
                payload=payload,
                secret=webhook["secret"],
            )

            triggered_count += 1

        logger.info(f"Webhook event {event_type} sent to {triggered_count} endpoints")
        return triggered_count

    def _send_webhook_request(
        self,
        url: str,
        event_type: str,
        payload: Dict[str, Any],
        secret: str,
    ) -> bool:
        """Simulate sending a webhook HTTP request.

        In production, use httpx or requests to actually send.
        """
        webhook_payload = {
            "event": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": payload,
        }

        logger.info(f"📤 Webhook POST to {url}")
        logger.info(f"   Event: {event_type}")
        logger.info(f"   Payload: {json.dumps(payload, indent=2)[:200]}...")

        # Simulate success
        return True

    def notify_task_created(self, task: Task) -> int:
        """Notify webhooks about task creation."""
        payload = {
            "task_id": task.id,
            "project_id": task.project_id,
            "title": task.title,
            "status": task.status,
            "priority": task.priority,
            "created_at": task.created_at.isoformat() if task.created_at else None,
        }

        return self.sendWebhookEvent(WebhookEvent.TASK_CREATED, payload)

    def notify_task_updated(self, task: Task, changes: Dict[str, Any]) -> int:
        """Notify webhooks about task update."""
        payload = {
            "task_id": task.id,
            "project_id": task.project_id,
            "title": task.title,
            "changes": changes,
            "updated_at": datetime.utcnow().isoformat(),
        }

        return self.sendWebhookEvent(WebhookEvent.TASK_UPDATED, payload)

    def notify_task_completed(self, task: Task) -> int:
        """Notify webhooks about task completion."""
        payload = {
            "task_id": task.id,
            "project_id": task.project_id,
            "title": task.title,
            "completed_at": task.updated_at.isoformat() if task.updated_at else None,
        }

        return self.sendWebhookEvent(WebhookEvent.TASK_COMPLETED, payload)

    def notifyProjectCreated(self, project: Project) -> int:  # Deliberately camelCase
        """Notify webhooks about project creation."""
        payload = {
            "project_id": project.id,
            "name": project.name,
            "owner_id": project.owner_id,
            "created_at": project.created_at.isoformat() if project.created_at else None,
        }

        return self.sendWebhookEvent(WebhookEvent.PROJECT_CREATED, payload)

    def get_webhook_stats(self) -> Dict[str, Any]:
        """Get webhook statistics."""
        active_webhooks = sum(1 for w in self.registered_webhooks if w["active"])

        event_subscriptions = {}
        for webhook in self.registered_webhooks:
            if webhook["active"]:
                for event in webhook["events"]:
                    event_subscriptions[event] = event_subscriptions.get(event, 0) + 1

        return {
            "total_webhooks": len(self.registered_webhooks),
            "active_webhooks": active_webhooks,
            "event_subscriptions": event_subscriptions,
        }

    def deactivate_webhook(self, webhook_id: str) -> bool:
        """Deactivate a webhook."""
        for webhook in self.registered_webhooks:
            if webhook["id"] == webhook_id:
                webhook["active"] = False
                logger.info(f"Webhook {webhook_id} deactivated")
                return True

        return False

    def delete_webhook(self, webhook_id: str) -> bool:
        """Delete a webhook."""
        for i, webhook in enumerate(self.registered_webhooks):
            if webhook["id"] == webhook_id:
                del self.registered_webhooks[i]
                logger.info(f"Webhook {webhook_id} deleted")
                return True

        return False

    def test_webhook(self, webhook_id: str) -> bool:
        """Send a test event to a webhook."""
        for webhook in self.registered_webhooks:
            if webhook["id"] == webhook_id:
                test_payload = {
                    "message": "This is a test webhook",
                    "webhook_id": webhook_id,
                }

                return self._send_webhook_request(
                    url=webhook["url"],
                    event_type="test.event",
                    payload=test_payload,
                    secret=webhook["secret"],
                )

        return False
