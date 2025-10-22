"""General helper functions (deliberately includes some duplicated logic)."""

import hashlib
import random
import string
from datetime import datetime, timedelta
from typing import Optional, Any, Dict


def generate_random_string(length: int = 10) -> str:
    """Generate a random alphanumeric string."""
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def hash_string(value: str) -> str:
    """Hash a string using SHA256."""
    return hashlib.sha256(value.encode()).hexdigest()


# Deliberately duplicate date formatting - version 1
def format_date(dt: datetime) -> str:
    """Format a datetime object to string.

    This version uses ISO format with 'T' separator.
    """
    if not dt:
        return ""
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def format_date_simple(dt: datetime) -> str:
    """Format a datetime to simple date string.

    Another formatting variant.
    """
    if not dt:
        return ""
    return dt.strftime("%Y-%m-%d")


def format_datetime_readable(dt: datetime) -> str:
    """Format datetime in human-readable format.

    Yet another date formatting function with different output.
    """
    if not dt:
        return "N/A"
    return dt.strftime("%B %d, %Y at %I:%M %p")


def calculate_days_until(target_date: datetime) -> int:
    """Calculate days until a target date."""
    if not target_date:
        return -1
    now = datetime.utcnow()
    delta = target_date - now
    return delta.days


def is_overdue(due_date: Optional[datetime]) -> bool:
    """Check if a date is overdue."""
    if not due_date:
        return False
    return due_date < datetime.utcnow()


def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get a value from dictionary with default."""
    return dictionary.get(key, default)


def filterNone(data: Dict[str, Any]) -> Dict[str, Any]:  # Deliberately camelCase
    """Filter out None values from a dictionary.

    Example of inconsistent naming convention.
    """
    return {k: v for k, v in data.items() if v is not None}


def validateEmail(email: str) -> bool:  # Deliberately camelCase
    """Validate email format (basic check).

    Another example of camelCase to show inconsistency.
    """
    return "@" in email and "." in email.split("@")[1]


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate a string to max length with suffix."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def chunk_list(items: list, chunk_size: int):
    """Split a list into chunks of specified size."""
    for i in range(0, len(items), chunk_size):
        yield items[i : i + chunk_size]


def merge_dicts(*dicts):
    """Merge multiple dictionaries.

    Missing type hints deliberately.
    """
    result = {}
    for d in dicts:
        result.update(d)
    return result


def ensure_list(value):  # type: ignore
    """Ensure value is a list.

    Deliberately ignoring types.
    """
    if isinstance(value, list):
        return value
    return [value] if value is not None else []


def calculate_percentage(part: float, whole: float) -> float:
    """Calculate percentage of part to whole."""
    if whole == 0:
        return 0.0
    return (part / whole) * 100


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    try:
        return numerator / denominator
    except ZeroDivisionError:
        return default


def create_slug(text: str) -> str:
    """Create a URL-friendly slug from text."""
    # Simple implementation
    slug = text.lower()
    slug = "".join(c if c.isalnum() or c in " -" else "" for c in slug)
    slug = slug.replace(" ", "-")
    return slug


def get_current_timestamp():
    """Get current UTC timestamp.

    Returns raw datetime instead of formatted string.
    """
    return datetime.utcnow()


def add_days_to_date(date: datetime, days: int) -> datetime:
    """Add days to a date."""
    return date + timedelta(days=days)
