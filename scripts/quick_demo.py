#!/usr/bin/env python3
"""Quick demo script to showcase TaskFlow code smells in action.

This script:
1. Calls daily report for a seeded project (demonstrates long if-elif chain)
2. Triggers both duplicate reminder functions
3. Prints execution trace showing touched functions

Usage:
    python -m taskflow.scripts.quick_demo
"""

import sys
from datetime import datetime, timedelta
from contextlib import contextmanager

from taskflow.models.base import get_db, init_db
from taskflow.services.report_service import ReportService
from taskflow.services.notification_service import NotificationService
from taskflow.services.task_service import TaskService
from taskflow.services.project_service import ProjectService
from taskflow.services.user_service import UserService
from taskflow.utils.logger import get_logger

logger = get_logger(__name__)


# Execution trace for code smell demonstration
EXECUTION_TRACE = []


@contextmanager
def trace_execution(function_path: str, description: str = ""):
    """Context manager to trace function execution."""
    print(f"\n🔍 Entering: {function_path}")
    if description:
        print(f"   ℹ️  {description}")
    EXECUTION_TRACE.append({
        "function": function_path,
        "description": description,
        "timestamp": datetime.utcnow()
    })
    yield
    print(f"✅ Completed: {function_path}")


def print_header(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_code_smell(smell_name: str, details: str):
    """Print information about a code smell being demonstrated."""
    print(f"\n⚠️  CODE SMELL: {smell_name}")
    print(f"   {details}")


def demo_daily_report():
    """Demonstrate the daily report generation with long if-elif chain."""
    print_header("DEMO 1: Daily Report Generation")
    print_code_smell(
        "Long If-Elif Chain",
        "build_daily_summary() has 155 lines with nested conditionals"
    )

    with get_db() as db:
        project_service = ProjectService(db)
        report_service = ReportService(db)

        # Get first project from seeded data
        with trace_execution(
            "taskflow.services.project_service.ProjectService.get_all()",
            "Fetching all projects"
        ):
            projects = project_service.project_repo.get_all()

        if not projects:
            print("❌ No projects found. Please run: make seed")
            return None

        project = projects[0]
        print(f"\n📊 Generating report for project: '{project.name}' (ID: {project.id})")

        # Generate daily summary - this triggers the long if-elif chain!
        with trace_execution(
            "taskflow.services.report_service.ReportService.build_daily_summary()",
            "⚠️  LONG IF-ELIF CHAIN (155 lines): Checks status, priority, assignee, overdue, comments"
        ):
            text_summary = report_service.build_daily_summary(
                project_id=project.id,
                include_overdue=True,
                include_assignees=True,
                compact=False
            )

        # Also generate metrics report
        with trace_execution(
            "taskflow.services.report_service.ReportService.generate_project_report()",
            "Uses asyncio.run() unnecessarily for sync calculation"
        ):
            metrics = report_service.generate_project_report(project.id)

        print("\n📝 Daily Summary Preview (first 500 chars):")
        print("-" * 80)
        print(text_summary[:500])
        if len(text_summary) > 500:
            print("... (truncated)")
        print("-" * 80)

        if metrics:
            print(f"\n📈 Metrics:")
            print(f"   Total Tasks: {metrics['total_tasks']}")
            print(f"   Completed: {metrics['done_count']} ({metrics['completion_rate']:.1f}%)")
            print(f"   In Progress: {metrics['in_progress_count']}")
            print(f"   Todo: {metrics['todo_count']}")
            print(f"   Blocked: {metrics['blocked_count']}")

        return project.id


def demo_duplicate_reminders():
    """Demonstrate the duplicate reminder functions."""
    print_header("DEMO 2: Duplicate Reminder Functions")
    print_code_smell(
        "Near-Duplicate Functions",
        "send_task_reminder() and remind_task_due() do the same thing differently"
    )

    with get_db() as db:
        task_service = TaskService(db)
        user_service = UserService(db)
        notification_service = NotificationService(db)

        # Get first task and user from seeded data
        with trace_execution(
            "taskflow.services.task_service.TaskService.get_all()",
            "Fetching tasks"
        ):
            tasks = task_service.task_repo.get_all()

        with trace_execution(
            "taskflow.services.user_service.UserService.get_all()",
            "Fetching users"
        ):
            users = user_service.user_repo.get_all()

        if not tasks or not users:
            print("❌ No tasks or users found. Please run: make seed")
            return

        task = tasks[0]
        user = users[0]

        print(f"\n📧 Sending reminders for task: '{task.title}' to user: '{user.name}'")

        # Call FIRST duplicate function
        with trace_execution(
            "taskflow.services.notification_service.NotificationService.send_task_reminder()",
            "Version 1: Uses (task, user) params, format_datetime(), subject='Reminder:'"
        ):
            print(f"\n   🔔 Calling send_task_reminder(task, user)")
            print(f"      - Parameter names: task, user")
            print(f"      - Date formatting: format_datetime()")
            print(f"      - Subject: 'Reminder: {task.title}'")
            print(f"      - Greeting: 'Hello {user.name}'")

            # Note: email_client may not be configured, so this might fail
            try:
                result1 = notification_service.send_task_reminder(task, user)
                print(f"      ✅ Result: {result1}")
            except Exception as e:
                print(f"      ⚠️  Email not sent (no SMTP configured): {type(e).__name__}")

        # Call SECOND duplicate function
        with trace_execution(
            "taskflow.services.notification_service.NotificationService.remind_task_due()",
            "Version 2: Uses (task_obj, user_obj, urgent) params, format_date_pretty(), subject='Task Reminder:'"
        ):
            print(f"\n   🔔 Calling remind_task_due(task_obj, user_obj, urgent=True)")
            print(f"      - Parameter names: task_obj, user_obj, urgent")
            print(f"      - Date formatting: format_date_pretty()")
            print(f"      - Subject: 'URGENT: Task Reminder: {task.title}'")
            print(f"      - Greeting: 'Hi {user.name}'")
            print(f"      - Priority display: {task.priority.upper()}")

            try:
                result2 = notification_service.remind_task_due(task, user, urgent=True)
                print(f"      ✅ Result: {result2}")
            except Exception as e:
                print(f"      ⚠️  Email not sent (no SMTP configured): {type(e).__name__}")

        print("\n   💡 These functions do the SAME THING with minor differences!")
        print("      Recommendation: Consolidate into single function")


def demo_duplicate_date_formatting():
    """Demonstrate duplicate date formatting functions."""
    print_header("DEMO 3: Duplicate Date Formatting")
    print_code_smell(
        "Scattered Date Formatting",
        "7 different functions across 2 modules produce different formats"
    )

    from taskflow.utils import date_utils, helpers

    test_date = datetime(2025, 10, 22, 14, 30, 45)
    print(f"\n📅 Formatting date: {test_date}")

    print("\n   From date_utils.py:")
    with trace_execution("taskflow.utils.date_utils.format_datetime()", "Format 1"):
        print(f"      format_datetime():        '{date_utils.format_datetime(test_date)}'")

    with trace_execution("taskflow.utils.date_utils.format_date_pretty()", "Format 2"):
        print(f"      format_date_pretty():     '{date_utils.format_date_pretty(test_date)}'")

    with trace_execution("taskflow.utils.date_utils.format_time()", "Format 3"):
        print(f"      format_time():            '{date_utils.format_time(test_date)}'")

    print("\n   From helpers.py:")
    with trace_execution("taskflow.utils.helpers.format_date()", "Format 4"):
        print(f"      format_date():            '{helpers.format_date(test_date)}'")

    with trace_execution("taskflow.utils.helpers.format_date_simple()", "Format 5"):
        print(f"      format_date_simple():     '{helpers.format_date_simple(test_date)}'")

    with trace_execution("taskflow.utils.helpers.format_datetime_readable()", "Format 6"):
        print(f"      format_datetime_readable(): '{helpers.format_datetime_readable(test_date)}'")

    print("\n   💡 7 different functions, 6+ different formats!")
    print("      Recommendation: Create unified DateFormatter class")


def demo_raw_sql():
    """Demonstrate raw SQL usage bypassing ORM."""
    print_header("DEMO 4: Raw SQL Query")
    print_code_smell(
        "Raw SQL Bypassing ORM",
        "project_service.get_project_stats() uses text() with raw SELECT"
    )

    with get_db() as db:
        project_service = ProjectService(db)
        projects = project_service.project_repo.get_all()

        if not projects:
            print("❌ No projects found. Please run: make seed")
            return

        project = projects[0]

        with trace_execution(
            "taskflow.services.project_service.ProjectService.get_project_stats()",
            "⚠️  RAW SQL: Uses Session.execute(text(...)) instead of SQLAlchemy ORM"
        ):
            stats = project_service.get_project_stats(project.id)

        if stats:
            print(f"\n📊 Project Stats (from RAW SQL):")
            print(f"   Project: {stats['project_name']}")
            print(f"   Total Tasks: {stats['total_tasks']}")
            print(f"   Completed: {stats['completed_tasks']}")
            print(f"   In Progress: {stats['in_progress_tasks']}")

        print("\n   💡 This uses raw SQL instead of repository pattern!")
        print("      See: taskflow/services/project_service.py:104-126")
        print("      TODO comment: 'This should use SQLAlchemy instead of raw SQL'")


def demo_urgency_duplication():
    """Demonstrate duplicate urgency calculation functions."""
    print_header("DEMO 5: Duplicate Urgency Calculation")
    print_code_smell(
        "Duplicate Business Logic",
        "compute_urgency_label() vs calculate_task_urgency() with different thresholds"
    )

    from taskflow.services.task_service import compute_urgency_label
    from taskflow.services.report_service import calculate_task_urgency

    with get_db() as db:
        task_service = TaskService(db)
        tasks = task_service.task_repo.get_all()

        if not tasks:
            print("❌ No tasks found. Please run: make seed")
            return

        # Find tasks with different scenarios
        overdue_task = None
        soon_task = None
        normal_task = None

        for task in tasks:
            if task.due_date:
                time_diff = task.due_date - datetime.utcnow()
                if time_diff.total_seconds() < 0 and not overdue_task:
                    overdue_task = task
                elif 0 < time_diff.total_seconds() < 86400 and not soon_task:  # < 24h
                    soon_task = task
                elif time_diff.days > 3 and not normal_task:
                    normal_task = task

        print("\n📋 Testing urgency calculations on different tasks:")

        for task in [t for t in [overdue_task, soon_task, normal_task] if t]:
            if task.due_date:
                time_diff = task.due_date - datetime.utcnow()
                hours_diff = time_diff.total_seconds() / 3600

                print(f"\n   Task: '{task.title[:40]}...'")
                print(f"   Due: {task.due_date.strftime('%Y-%m-%d %H:%M')} ({hours_diff:.1f}h from now)")

                with trace_execution(
                    "taskflow.services.task_service.compute_urgency_label()",
                    "Version 1: Threshold 24h, returns 'urgent'/'soon'/'upcoming'/'normal'"
                ):
                    urgency1 = compute_urgency_label(task)
                    print(f"      compute_urgency_label():    '{urgency1}'")

                with trace_execution(
                    "taskflow.services.report_service.calculate_task_urgency()",
                    "Version 2: Threshold 12h, returns 'critical-urgent'/'due-soon'/'upcoming'/'normal'"
                ):
                    urgency2 = calculate_task_urgency(task)
                    print(f"      calculate_task_urgency():   '{urgency2}'")

                if urgency1 != urgency2:
                    print(f"      ⚠️  DIFFERENT RESULTS! Same task, different logic")

    print("\n   💡 Two functions with different thresholds and return values!")
    print("      task_service: 24h threshold, returns 'urgent'")
    print("      report_service: 12h threshold, returns 'critical-urgent'")
    print("      Recommendation: Consolidate into single source of truth")


def print_execution_summary():
    """Print summary of execution trace."""
    print_header("EXECUTION TRACE SUMMARY")

    print(f"\n📍 Total functions traced: {len(EXECUTION_TRACE)}")
    print("\nExecution path:")

    for i, trace in enumerate(EXECUTION_TRACE, 1):
        print(f"\n{i}. {trace['function']}")
        if trace['description']:
            print(f"   └─ {trace['description']}")

    print("\n" + "=" * 80)
    print("Functions touched (grouped by file):")
    print("=" * 80)

    # Group by module
    by_module = {}
    for trace in EXECUTION_TRACE:
        module = '.'.join(trace['function'].split('.')[:3])  # taskflow.services.xxx
        if module not in by_module:
            by_module[module] = []
        by_module[module].append(trace['function'])

    for module in sorted(by_module.keys()):
        print(f"\n📁 {module}")
        for func in by_module[module]:
            func_name = func.split('.')[-1]
            print(f"   • {func_name}()")


def main():
    """Run all demos."""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                      TaskFlow Quick Demo                                   ║
║                   Showcasing Code Smells in Action                         ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)

    # Initialize database
    print("\n🗄️  Initializing database...")
    init_db()

    # Check if database is seeded
    with get_db() as db:
        from taskflow.models.repository import UserRepository
        from taskflow.models.user import User
        user_repo = UserRepository(User, db)
        user_count = user_repo.count()

    if user_count == 0:
        print("\n⚠️  Database is empty!")
        print("   Please run: make seed")
        print("   Then run this demo again.")
        sys.exit(1)

    print(f"   ✅ Found {user_count} users in database")

    # Run demos
    try:
        demo_daily_report()
        demo_duplicate_reminders()
        demo_duplicate_date_formatting()
        demo_raw_sql()
        demo_urgency_duplication()

        # Print execution summary
        print_execution_summary()

        print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                            Demo Complete! ✨                                ║
║                                                                            ║
║  All 5 demos executed successfully, showcasing:                           ║
║  ✅ Long if-elif chain (155 lines)                                        ║
║  ✅ Duplicate reminder functions                                          ║
║  ✅ Scattered date formatting (7 functions)                               ║
║  ✅ Raw SQL bypassing ORM                                                 ║
║  ✅ Duplicate urgency calculations                                        ║
║                                                                            ║
║  See scripts/demo_walkthrough.md for more code smell examples!            ║
╚════════════════════════════════════════════════════════════════════════════╝
        """)

    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
