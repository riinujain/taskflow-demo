"""Scheduler service for background tasks and periodic jobs (simulated)."""

from datetime import datetime, timedelta, time as dt_time
from typing import List, Dict, Any, Callable, Optional
import logging

from sqlalchemy.orm import Session

from taskflow.services.task_service import TaskService
from taskflow.services.notification_service import NotificationService
from taskflow.services.report_service import ReportService
from taskflow.utils.logger import get_logger

logger = get_logger(__name__)


class ScheduledJob:
    """Represents a scheduled job."""

    def __init__(
        self,
        name: str,
        func: Callable,
        interval_minutes: Optional[int] = None,
        schedule_time: Optional[dt_time] = None,
        enabled: bool = True,
    ):
        """Initialize a scheduled job.

        Args:
            name: Job name
            func: Function to execute
            interval_minutes: Run every N minutes (or None for daily)
            schedule_time: Specific time to run daily jobs
            enabled: Whether job is enabled
        """
        self.name = name
        self.func = func
        self.interval_minutes = interval_minutes
        self.schedule_time = schedule_time
        self.enabled = enabled
        self.last_run: Optional[datetime] = None
        self.run_count = 0
        self.error_count = 0

    def should_run(self) -> bool:
        """Check if job should run now.

        Returns:
            True if job should run
        """
        if not self.enabled:
            return False

        now = datetime.utcnow()

        # First time running
        if self.last_run is None:
            return True

        # Interval-based job
        if self.interval_minutes:
            next_run = self.last_run + timedelta(minutes=self.interval_minutes)
            return now >= next_run

        # Daily scheduled job
        if self.schedule_time:
            # Check if we've passed the schedule time today and haven't run yet today
            today_schedule = datetime.combine(now.date(), self.schedule_time)

            if now >= today_schedule:
                # Check if last run was before today's schedule time
                if self.last_run < today_schedule:
                    return True

        return False

    def execute(self, *args, **kwargs) -> Any:
        """Execute the job function.

        Returns:
            Result from function
        """
        try:
            logger.info(f"Executing scheduled job: {self.name}")
            result = self.func(*args, **kwargs)
            self.last_run = datetime.utcnow()
            self.run_count += 1
            logger.info(f"Job {self.name} completed successfully")
            return result
        except Exception as e:
            self.error_count += 1
            logger.error(f"Job {self.name} failed: {e}")
            raise


class SchedulerService:
    """Service for managing scheduled background jobs.

    Note: This is a simplified scheduler. In production, use Celery or similar.
    """

    def __init__(self, db: Session):
        self.db = db
        self.jobs: List[ScheduledJob] = []
        self._setup_default_jobs()

    def _setup_default_jobs(self):
        """Set up default scheduled jobs."""
        # Send daily summaries at 8 AM
        self.register_job(
            name="daily_summary",
            func=self._send_daily_summaries,
            schedule_time=dt_time(hour=8, minute=0),
        )

        # Check for overdue tasks every hour
        self.register_job(
            name="overdue_check",
            func=self._check_overdue_tasks,
            interval_minutes=60,
        )

        # Send task reminders every 2 hours
        self.register_job(
            name="task_reminders",
            func=self._send_task_reminders,
            interval_minutes=120,
        )

        # Cleanup old data daily at midnight
        self.register_job(
            name="cleanup",
            func=self._cleanup_old_data,
            schedule_time=dt_time(hour=0, minute=0),
        )

    def register_job(
        self,
        name: str,
        func: Callable,
        interval_minutes: Optional[int] = None,
        schedule_time: Optional[dt_time] = None,
        enabled: bool = True,
    ) -> ScheduledJob:
        """Register a new scheduled job.

        Args:
            name: Job name
            func: Function to execute
            interval_minutes: Run every N minutes
            schedule_time: Daily schedule time
            enabled: Whether job is enabled

        Returns:
            Created job
        """
        job = ScheduledJob(
            name=name,
            func=func,
            interval_minutes=interval_minutes,
            schedule_time=schedule_time,
            enabled=enabled,
        )

        self.jobs.append(job)
        logger.info(f"Registered job: {name}")

        return job

    def run_pending_jobs(self):
        """Run all jobs that are due.

        This would be called by a scheduler daemon/worker.
        """
        pending_count = 0

        for job in self.jobs:
            if job.should_run():
                try:
                    job.execute(self.db)
                    pending_count += 1
                except Exception as e:
                    logger.error(f"Failed to execute job {job.name}: {e}")

        if pending_count > 0:
            logger.info(f"Executed {pending_count} pending jobs")

        return pending_count

    def runJobNow(self, job_name: str) -> bool:  # Deliberately camelCase
        """Run a specific job immediately.

        Args:
            job_name: Name of job to run

        Returns:
            True if job was found and executed
        """
        for job in self.jobs:
            if job.name == job_name:
                try:
                    job.execute(self.db)
                    return True
                except Exception as e:
                    logger.error(f"Failed to run job {job_name}: {e}")
                    return False

        logger.warning(f"Job not found: {job_name}")
        return False

    def get_job_status(self, job_name: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job.

        Args:
            job_name: Job name

        Returns:
            Job status dictionary or None
        """
        for job in self.jobs:
            if job.name == job_name:
                return {
                    "name": job.name,
                    "enabled": job.enabled,
                    "last_run": job.last_run.isoformat() if job.last_run else None,
                    "run_count": job.run_count,
                    "error_count": job.error_count,
                    "interval_minutes": job.interval_minutes,
                    "schedule_time": str(job.schedule_time) if job.schedule_time else None,
                }

        return None

    def getAllJobsStatus(self) -> List[Dict[str, Any]]:  # Deliberately camelCase
        """Get status of all jobs.

        Returns:
            List of job status dictionaries
        """
        return [self.get_job_status(job.name) for job in self.jobs]

    def enable_job(self, job_name: str) -> bool:
        """Enable a job.

        Args:
            job_name: Job name

        Returns:
            True if job was found
        """
        for job in self.jobs:
            if job.name == job_name:
                job.enabled = True
                logger.info(f"Job enabled: {job_name}")
                return True

        return False

    def disable_job(self, job_name: str) -> bool:
        """Disable a job.

        Args:
            job_name: Job name

        Returns:
            True if job was found
        """
        for job in self.jobs:
            if job.name == job_name:
                job.enabled = False
                logger.info(f"Job disabled: {job_name}")
                return True

        return False

    # Default job implementations

    def _send_daily_summaries(self, db: Session):
        """Send daily summary emails to all active users.

        This is a scheduled job implementation.
        """
        logger.info("Running daily summary job")

        # In a real implementation, get all active users
        # For now, just log
        notification_service = NotificationService(db)

        # Would iterate through users and send summaries
        logger.info("Daily summaries would be sent here")

        return {"sent": 0}

    def _check_overdue_tasks(self, db: Session):
        """Check for overdue tasks and send notifications.

        This is a scheduled job implementation.
        """
        logger.info("Checking for overdue tasks")

        task_service = TaskService(db)
        overdue_tasks = task_service.get_overdue_tasks()

        logger.info(f"Found {len(overdue_tasks)} overdue tasks")

        # Would send notifications here
        return {"overdue_count": len(overdue_tasks)}

    def _send_task_reminders(self, db: Session):
        """Send reminders for tasks due soon.

        This is a scheduled job implementation.
        """
        logger.info("Sending task reminders")

        task_service = TaskService(db)
        due_soon = task_service.get_tasks_due_soon(days=3)

        logger.info(f"Found {len(due_soon)} tasks due soon")

        # Would send reminder emails here
        return {"reminders_sent": 0}

    def _cleanup_old_data(self, db: Session):
        """Cleanup old completed tasks and data.

        This is a scheduled job implementation.
        """
        logger.info("Running cleanup job")

        # Would cleanup old data here
        # For example: archive completed tasks > 90 days old

        return {"cleaned_up": 0}


def create_scheduler_daemon(db: Session, check_interval: int = 60):
    """Create a scheduler daemon that runs jobs periodically.

    Args:
        db: Database session
        check_interval: How often to check for pending jobs (seconds)

    Note: This is a simplified example. In production, use a proper
    task queue like Celery.
    """
    import time
    import threading

    scheduler = SchedulerService(db)

    def run_scheduler():
        while True:
            try:
                scheduler.run_pending_jobs()
            except Exception as e:
                logger.error(f"Scheduler error: {e}")

            time.sleep(check_interval)

    # Run in background thread
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()

    logger.info(f"Scheduler daemon started (check interval: {check_interval}s)")

    return scheduler
