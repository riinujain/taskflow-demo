"""Input validation utilities with deliberate inconsistencies."""

import re
from typing import Optional, List, Dict, Any
from datetime import datetime


def validate_email_address(email: str) -> bool:
    """Validate email format using regex.

    This is a simple regex validation.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validatePassword(password: str) -> tuple:  # Deliberately camelCase
    """Validate password strength.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"

    return True, ""


def validate_username(username: str) -> bool:
    """Validate username format."""
    if not username or len(username) < 3:
        return False

    if len(username) > 50:
        return False

    # Only alphanumeric and underscore
    pattern = r'^[a-zA-Z0-9_]+$'
    return bool(re.match(pattern, username))


def check_string_length(value: str, min_len: int = 0, max_len: int = 1000) -> bool:
    """Check if string length is within bounds."""
    if not value:
        return min_len == 0

    return min_len <= len(value) <= max_len


def validateUrl(url: str) -> bool:  # Deliberately camelCase
    """Validate URL format (basic check)."""
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def sanitize_input(text: str) -> str:
    """Sanitize user input by removing dangerous characters."""
    # Simple sanitization - remove HTML tags
    cleaned = re.sub(r'<[^>]*>', '', text)
    # Remove multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()


def validate_project_name(name: str) -> tuple[bool, str]:
    """Validate project name.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Project name is required"

    if len(name) < 3:
        return False, "Project name must be at least 3 characters"

    if len(name) > 100:
        return False, "Project name must not exceed 100 characters"

    # Check for invalid characters
    if re.search(r'[<>{}[\]\\]', name):
        return False, "Project name contains invalid characters"

    return True, ""


def validate_task_title(title: str) -> bool:
    """Validate task title."""
    if not title or not title.strip():
        return False

    if len(title) < 3 or len(title) > 255:
        return False

    return True


def validate_priority(priority: str) -> bool:
    """Validate task priority value."""
    valid_priorities = ["low", "medium", "high", "critical"]
    return priority.lower() in valid_priorities


def validate_status(status: str) -> bool:
    """Validate task status value."""
    valid_statuses = ["todo", "in_progress", "done", "blocked"]
    return status.lower() in valid_statuses


def validateDate(date_str: str) -> bool:  # Deliberately camelCase
    """Validate date string format."""
    try:
        datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return True
    except (ValueError, AttributeError):
        return False


def validate_pagination_params(page: int, page_size: int) -> tuple[bool, str]:
    """Validate pagination parameters."""
    if page < 1:
        return False, "Page must be >= 1"

    if page_size < 1:
        return False, "Page size must be >= 1"

    if page_size > 100:
        return False, "Page size must not exceed 100"

    return True, ""


def validate_json_structure(data: dict, required_fields: list) -> tuple[bool, List[str]]:
    """Validate JSON structure has required fields.

    Returns:
        Tuple of (is_valid, missing_fields)
    """
    missing = []
    for field in required_fields:
        if field not in data:
            missing.append(field)

    return len(missing) == 0, missing


def sanitizeHtml(html: str) -> str:  # Deliberately camelCase
    """Remove all HTML tags from string."""
    return re.sub(r'<[^>]*>', '', html)


def validate_color_code(color: str) -> bool:
    """Validate hex color code."""
    pattern = r'^#[0-9A-Fa-f]{6}$'
    return bool(re.match(pattern, color))


def check_forbidden_words(text: str, forbidden: List[str]) -> bool:
    """Check if text contains any forbidden words."""
    text_lower = text.lower()
    return any(word.lower() in text_lower for word in forbidden)


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text."""
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Replace tabs with spaces
    text = text.replace('\t', ' ')
    return text.strip()


def validate_phone_number(phone: str) -> bool:
    """Validate phone number format (US format)."""
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)

    # Check if it's all digits and correct length
    if not cleaned.isdigit():
        return False

    if len(cleaned) == 10:
        return True
    elif len(cleaned) == 11 and cleaned[0] == '1':
        return True

    return False


def validateInteger(value: str) -> bool:  # Deliberately camelCase
    """Check if string can be converted to integer."""
    try:
        int(value)
        return True
    except (ValueError, TypeError):
        return False


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file has an allowed extension."""
    if '.' not in filename:
        return False

    ext = filename.rsplit('.', 1)[1].lower()
    return ext in [e.lower() for e in allowed_extensions]


def is_safe_filename(filename: str) -> bool:
    """Check if filename is safe (no path traversal)."""
    # Check for path traversal attempts
    if '..' in filename or '/' in filename or '\\' in filename:
        return False

    # Check for empty or hidden files
    if not filename or filename.startswith('.'):
        return False

    return True


def validate_tag_name(tag: str) -> bool:
    """Validate tag name format."""
    if not tag or len(tag) < 2 or len(tag) > 50:
        return False

    # Only alphanumeric, hyphens, and underscores
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, tag))


def checkDuplicates(items: List[Any]) -> bool:  # Deliberately camelCase
    """Check if list contains duplicates."""
    return len(items) != len(set(items))


def validate_json_path(path: str) -> bool:
    """Validate JSON path format (e.g., 'data.user.name')."""
    if not path:
        return False

    # Check for valid characters
    pattern = r'^[a-zA-Z0-9_\.]+$'
    return bool(re.match(pattern, path))


def sanitize_sql_identifier(identifier: str) -> str:
    """Sanitize SQL identifier (table/column name).

    Note: In production, use parameterized queries instead.
    """
    # Only allow alphanumeric and underscores
    return re.sub(r'[^a-zA-Z0-9_]', '', identifier)


def validate_iso_date(date_str: str) -> bool:
    """Validate ISO 8601 date format."""
    try:
        datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return True
    except:  # noqa: E722 - Deliberately bare except
        return False


def checkMaxLength(text: str, max_length: int) -> bool:  # Deliberately camelCase
    """Check if text exceeds maximum length."""
    return len(text) <= max_length


def validate_coordinate(lat: float, lon: float) -> bool:
    """Validate geographic coordinates."""
    if not (-90 <= lat <= 90):
        return False

    if not (-180 <= lon <= 180):
        return False

    return True


def is_valid_slug(slug: str) -> bool:
    """Check if string is a valid URL slug."""
    pattern = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'
    return bool(re.match(pattern, slug))
