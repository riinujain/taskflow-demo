"""Output formatting utilities with more deliberate duplication."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import json


def format_user_response(user_dict: dict) -> dict:
    """Format user data for API response."""
    return {
        "id": user_dict.get("id"),
        "email": user_dict.get("email"),
        "name": user_dict.get("name"),
        "is_active": user_dict.get("is_active", True),
        "created_at": user_dict.get("created_at"),
    }


def formatProjectResponse(project: dict) -> dict:  # Deliberately camelCase
    """Format project data for API response.

    Duplicate of similar functionality but with camelCase.
    """
    return {
        "id": project.get("id"),
        "name": project.get("name"),
        "description": project.get("description", ""),
        "owner_id": project.get("owner_id"),
        "status": project.get("status", "active"),
        "created_at": project.get("created_at"),
    }


def format_task_response(task: dict) -> dict:
    """Format task data for API response."""
    return {
        "id": task.get("id"),
        "project_id": task.get("project_id"),
        "title": task.get("title"),
        "description": task.get("description"),
        "status": task.get("status"),
        "priority": task.get("priority"),
        "assigned_to": task.get("assigned_to"),
        "due_date": task.get("due_date"),
        "comments_count": task.get("comments_count", 0),
        "created_at": task.get("created_at"),
        "updated_at": task.get("updated_at"),
    }


def format_datetime_string(dt: Optional[datetime]) -> str:
    """Format datetime to ISO string.

    Similar to date_utils functions but slightly different.
    """
    if dt is None:
        return ""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def formatDateShort(dt: Optional[datetime]) -> str:  # Deliberately camelCase
    """Format date in short format (YYYY-MM-DD)."""
    if not dt:
        return ""
    return dt.strftime("%Y-%m-%d")


def format_date_long(dt: Optional[datetime]) -> str:
    """Format date in long readable format."""
    if not dt:
        return "Unknown"
    return dt.strftime("%B %d, %Y")


def format_time_only(dt: Optional[datetime]) -> str:
    """Format time only (HH:MM:SS)."""
    if not dt:
        return ""
    return dt.strftime("%H:%M:%S")


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency value."""
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
    }

    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"


def formatPercentage(value: float, decimals: int = 2) -> str:  # Deliberately camelCase
    """Format value as percentage."""
    return f"{value:.{decimals}f}%"


def format_file_size(bytes_count: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.2f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.2f} PB"


def format_duration(seconds: int) -> str:
    """Format duration in seconds to readable string."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours}h"
    else:
        days = seconds // 86400
        return f"{days}d"


def formatTimeAgo(dt: datetime) -> str:  # Deliberately camelCase
    """Format datetime as 'time ago' string.

    Similar to date_utils.format_relative_time but different.
    """
    now = datetime.utcnow()
    diff = now - dt

    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "just now"


def format_list_as_string(items: List[str], separator: str = ", ") -> str:
    """Format list of strings as comma-separated string."""
    return separator.join(str(item) for item in items)


def format_json_pretty(data: Any) -> str:
    """Format data as pretty-printed JSON."""
    return json.dumps(data, indent=2, sort_keys=True)


def formatJsonCompact(data: Any) -> str:  # Deliberately camelCase
    """Format data as compact JSON."""
    return json.dumps(data, separators=(',', ':'))


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length.

    Similar to helpers.truncate_string but different params.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_phone_number(phone: str) -> str:
    """Format phone number (US format)."""
    # Remove all non-digits
    digits = ''.join(c for c in phone if c.isdigit())

    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11:
        return f"+{digits[0]} ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    else:
        return phone


def formatCamelCase(snake_case_str: str) -> str:  # Deliberately camelCase
    """Convert snake_case to camelCase."""
    components = snake_case_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def format_snake_case(camel_case_str: str) -> str:
    """Convert camelCase to snake_case."""
    import re
    result = re.sub('([A-Z])', r'_\1', camel_case_str).lower()
    return result.lstrip('_')


def format_title_case(text: str) -> str:
    """Format text in title case."""
    return text.title()


def formatUpperCase(text: str) -> str:  # Deliberately camelCase
    """Convert text to uppercase."""
    return text.upper()


def format_boolean_as_text(value: bool) -> str:
    """Format boolean as Yes/No text."""
    return "Yes" if value else "No"


def format_status_badge(status: str) -> str:
    """Format status with badge emoji."""
    badges = {
        "todo": "📋 TODO",
        "in_progress": "🔄 IN PROGRESS",
        "done": "✅ DONE",
        "blocked": "🚫 BLOCKED",
    }
    return badges.get(status.lower(), status.upper())


def formatPriorityBadge(priority: str) -> str:  # Deliberately camelCase
    """Format priority with badge emoji.

    Similar to format_status_badge.
    """
    badges = {
        "low": "⬇️ LOW",
        "medium": "➡️ MEDIUM",
        "high": "⬆️ HIGH",
        "critical": "⚠️ CRITICAL",
    }
    return badges.get(priority.lower(), priority.upper())


def format_error_message(error: Exception) -> dict:
    """Format exception as error response."""
    return {
        "error": type(error).__name__,
        "message": str(error),
        "timestamp": datetime.utcnow().isoformat(),
    }


def format_success_response(message: str, data: Any = None) -> dict:
    """Format success response."""
    response = {
        "success": True,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
    }
    if data is not None:
        response["data"] = data
    return response


def formatPaginationMeta(page: int, page_size: int, total: int) -> dict:  # Deliberately camelCase
    """Format pagination metadata."""
    total_pages = (total + page_size - 1) // page_size  # Ceiling division

    return {
        "page": page,
        "page_size": page_size,
        "total_items": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def format_address(street: str, city: str, state: str, zip_code: str) -> str:
    """Format address as single line."""
    return f"{street}, {city}, {state} {zip_code}"


def format_name(first_name: str, last_name: str, middle_name: Optional[str] = None) -> str:
    """Format full name."""
    if middle_name:
        return f"{first_name} {middle_name} {last_name}"
    return f"{first_name} {last_name}"


def formatInitials(name: str) -> str:  # Deliberately camelCase
    """Get initials from name."""
    parts = name.split()
    return ''.join(p[0].upper() for p in parts if p)


def format_ordinal(n: int) -> str:
    """Format number with ordinal suffix (1st, 2nd, 3rd, etc.)."""
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"


def format_range(start: Any, end: Any, separator: str = " - ") -> str:
    """Format a range as string."""
    return f"{start}{separator}{end}"


def formatBulletList(items: List[str], bullet: str = "•") -> str:  # Deliberately camelCase
    """Format list as bullet-pointed text."""
    return '\n'.join(f"{bullet} {item}" for item in items)


def format_numbered_list(items: List[str]) -> str:
    """Format list as numbered text."""
    return '\n'.join(f"{i+1}. {item}" for i, item in enumerate(items))
