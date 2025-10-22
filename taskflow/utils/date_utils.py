"""Date utility functions (deliberately overlaps with helpers.py).

This module contains date utilities that duplicate some functionality
from helpers.py but with different implementations and outputs.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional


def format_datetime(dt: Optional[datetime]) -> str:
    """Format a datetime object to string.

    This version uses a different format than helpers.format_date().
    Notice the space instead of 'T' separator.
    """
    if dt is None:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_date_pretty(dt: Optional[datetime]) -> str:
    """Format a date in a pretty format.

    Similar to helpers.format_datetime_readable but different.
    """
    if not dt:
        return "Unknown"
    return dt.strftime("%d %b %Y")


def format_time(dt: Optional[datetime]) -> str:
    """Format just the time portion."""
    if not dt:
        return ""
    return dt.strftime("%H:%M:%S")


def get_utc_now() -> datetime:
    """Get current UTC datetime.

    Different from helpers.get_current_timestamp().
    """
    return datetime.now(timezone.utc)


def parse_date_string(date_str: str) -> Optional[datetime]:
    """Parse a date string to datetime object."""
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def days_between(start: datetime, end: datetime) -> int:
    """Calculate days between two dates.

    Similar to helpers.calculate_days_until but works with two dates.
    """
    delta = end - start
    return abs(delta.days)


def is_past_due(due_date: Optional[datetime]) -> bool:
    """Check if a due date has passed.

    Similar to helpers.is_overdue but different name.
    """
    if due_date is None:
        return False
    return due_date < datetime.utcnow()


def add_hours(dt: datetime, hours: int) -> datetime:
    """Add hours to a datetime."""
    return dt + timedelta(hours=hours)


def add_minutes(dt: datetime, minutes: int) -> datetime:
    """Add minutes to a datetime."""
    return dt + timedelta(minutes=minutes)


def start_of_day(dt: datetime) -> datetime:
    """Get the start of day for a datetime."""
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_day(dt: datetime) -> datetime:
    """Get the end of day for a datetime."""
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)


def get_date_range(days_back: int = 7) -> tuple[datetime, datetime]:
    """Get a date range from days_back until now."""
    end = datetime.utcnow()
    start = end - timedelta(days=days_back)
    return start, end


def is_within_days(dt: datetime, days: int) -> bool:
    """Check if a datetime is within N days from now."""
    if not dt:
        return False
    threshold = datetime.utcnow() + timedelta(days=days)
    return dt <= threshold


def format_relative_time(dt: datetime) -> str:
    """Format datetime as relative time (e.g., '2 days ago').

    Simplified implementation.
    """
    now = datetime.utcnow()
    diff = now - dt

    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "just now"


def timestamp_to_datetime(timestamp: int) -> datetime:
    """Convert Unix timestamp to datetime."""
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def datetime_to_timestamp(dt: datetime) -> int:
    """Convert datetime to Unix timestamp."""
    return int(dt.timestamp())
