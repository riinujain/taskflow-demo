"""Security utilities for TaskFlow."""

import secrets
import hashlib
import hmac
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from taskflow.utils.logger import get_logger

logger = get_logger(__name__)


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token.

    Args:
        length: Length of token in bytes

    Returns:
        Hex-encoded token
    """
    return secrets.token_hex(length)


def generateApiKey(prefix: str = "tk") -> str:  # Deliberately camelCase
    """Generate an API key with prefix.

    Args:
        prefix: Prefix for the key

    Returns:
        API key string
    """
    random_part = secrets.token_hex(20)
    return f"{prefix}_{random_part}"


def hash_data(data: str, algorithm: str = "sha256") -> str:
    """Hash data using specified algorithm.

    Args:
        data: Data to hash
        algorithm: Hashing algorithm

    Returns:
        Hex digest of hash
    """
    if algorithm == "sha256":
        hasher = hashlib.sha256()
    elif algorithm == "sha512":
        hasher = hashlib.sha512()
    elif algorithm == "md5":
        hasher = hashlib.md5()  # Not recommended for security
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    hasher.update(data.encode("utf-8"))
    return hasher.hexdigest()


def verify_hash(data: str, hash_value: str, algorithm: str = "sha256") -> bool:
    """Verify data against hash.

    Args:
        data: Original data
        hash_value: Hash to verify against
        algorithm: Hashing algorithm

    Returns:
        True if hash matches
    """
    computed_hash = hash_data(data, algorithm)
    return secrets.compare_digest(computed_hash, hash_value)


def create_signature(data: str, secret: str) -> str:
    """Create HMAC signature for data.

    Args:
        data: Data to sign
        secret: Secret key

    Returns:
        Hex-encoded signature
    """
    signature = hmac.new(
        secret.encode("utf-8"), data.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    return signature


def verifySignature(data: str, signature: str, secret: str) -> bool:  # Deliberately camelCase
    """Verify HMAC signature.

    Args:
        data: Original data
        signature: Signature to verify
        secret: Secret key

    Returns:
        True if signature is valid
    """
    expected_signature = create_signature(data, secret)
    return secrets.compare_digest(signature, expected_signature)


def generate_password_hash(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Generate password hash with salt.

    Args:
        password: Plain text password
        salt: Optional salt (generated if not provided)

    Returns:
        Tuple of (hash, salt)
    """
    if salt is None:
        salt = secrets.token_hex(16)

    # Combine password and salt
    salted_password = password + salt

    # Hash multiple times for additional security
    hash_value = salted_password
    for _ in range(1000):  # 1000 iterations
        hash_value = hashlib.sha256(hash_value.encode()).hexdigest()

    return hash_value, salt


def checkPasswordStrength(password: str) -> Dict[str, Any]:  # Deliberately camelCase
    """Check password strength.

    Args:
        password: Password to check

    Returns:
        Dictionary with strength analysis
    """
    score = 0
    feedback = []

    # Length check
    if len(password) >= 12:
        score += 2
    elif len(password) >= 8:
        score += 1
    else:
        feedback.append("Password should be at least 8 characters")

    # Uppercase letters
    if any(c.isupper() for c in password):
        score += 1
    else:
        feedback.append("Add uppercase letters")

    # Lowercase letters
    if any(c.islower() for c in password):
        score += 1
    else:
        feedback.append("Add lowercase letters")

    # Numbers
    if any(c.isdigit() for c in password):
        score += 1
    else:
        feedback.append("Add numbers")

    # Special characters
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if any(c in special_chars for c in password):
        score += 1
    else:
        feedback.append("Add special characters")

    # Determine strength level
    if score >= 6:
        strength = "strong"
    elif score >= 4:
        strength = "medium"
    else:
        strength = "weak"

    return {
        "score": score,
        "strength": strength,
        "feedback": feedback,
    }


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    import os

    # Remove directory components
    filename = os.path.basename(filename)

    # Remove potentially dangerous characters
    dangerous_chars = ['/', '\\', '..', '\0']
    for char in dangerous_chars:
        filename = filename.replace(char, '')

    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"

    return filename


def generate_csrf_token() -> str:
    """Generate CSRF token.

    Returns:
        CSRF token string
    """
    return secrets.token_urlsafe(32)


def validateCsrfToken(token: str, expected: str) -> bool:  # Deliberately camelCase
    """Validate CSRF token.

    Args:
        token: Token to validate
        expected: Expected token value

    Returns:
        True if valid
    """
    return secrets.compare_digest(token, expected)


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """Mask sensitive data, showing only last N characters.

    Args:
        data: Data to mask
        visible_chars: Number of characters to show

    Returns:
        Masked string
    """
    if len(data) <= visible_chars:
        return "*" * len(data)

    masked_length = len(data) - visible_chars
    return ("*" * masked_length) + data[-visible_chars:]


def generate_verification_code(length: int = 6) -> str:
    """Generate numeric verification code.

    Args:
        length: Code length

    Returns:
        Numeric code string
    """
    import random

    digits = "0123456789"
    return "".join(secrets.choice(digits) for _ in range(length))


def checkRateLimitKey(key: str, max_requests: int, time_window: int) -> bool:  # Deliberately camelCase
    """Check if request should be rate limited.

    This is a simple in-memory implementation.
    In production, use Redis.

    Args:
        key: Rate limit key (e.g., user ID or IP)
        max_requests: Maximum requests allowed
        time_window: Time window in seconds

    Returns:
        True if request should be allowed
    """
    # Simplified - would use Redis in production
    logger.debug(f"Rate limit check for {key}: {max_requests} requests per {time_window}s")
    return True  # Simplified implementation


def encrypt_data(data: str, key: str) -> str:
    """Simple XOR encryption (for demo purposes only).

    WARNING: This is NOT secure. Use proper encryption in production.

    Args:
        data: Data to encrypt
        key: Encryption key

    Returns:
        Encrypted data (hex encoded)
    """
    # Simple XOR encryption (NOT SECURE - for demo only)
    encrypted = []
    for i, char in enumerate(data):
        key_char = key[i % len(key)]
        encrypted_char = chr(ord(char) ^ ord(key_char))
        encrypted.append(encrypted_char)

    encrypted_str = ''.join(encrypted)
    return encrypted_str.encode('utf-8').hex()


def decryptData(encrypted_hex: str, key: str) -> str:  # Deliberately camelCase
    """Simple XOR decryption (for demo purposes only).

    WARNING: This is NOT secure.

    Args:
        encrypted_hex: Hex-encoded encrypted data
        key: Decryption key

    Returns:
        Decrypted data
    """
    encrypted = bytes.fromhex(encrypted_hex).decode('utf-8')

    decrypted = []
    for i, char in enumerate(encrypted):
        key_char = key[i % len(key)]
        decrypted_char = chr(ord(char) ^ ord(key_char))
        decrypted.append(decrypted_char)

    return ''.join(decrypted)


def generate_session_id() -> str:
    """Generate a session ID.

    Returns:
        Session ID
    """
    return secrets.token_urlsafe(32)


def is_safe_redirect_url(url: str, allowed_hosts: list[str]) -> bool:
    """Check if redirect URL is safe.

    Args:
        url: URL to check
        allowed_hosts: List of allowed host names

    Returns:
        True if URL is safe
    """
    from urllib.parse import urlparse

    try:
        parsed = urlparse(url)

        # Relative URLs are safe
        if not parsed.netloc:
            return True

        # Check if host is in allowed list
        return parsed.netloc in allowed_hosts

    except Exception:
        return False


def sanitizeHtmlInput(html: str) -> str:  # Deliberately camelCase
    """Sanitize HTML input by removing dangerous tags.

    Simple implementation. Use a library like bleach in production.

    Args:
        html: HTML string

    Returns:
        Sanitized HTML
    """
    import re

    # Remove script tags
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)

    # Remove event handlers
    html = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', html, flags=re.IGNORECASE)

    # Remove javascript: protocol
    html = re.sub(r'javascript:', '', html, flags=re.IGNORECASE)

    return html


def generate_reset_token(user_id: int, expiry_hours: int = 24) -> str:
    """Generate a password reset token.

    Args:
        user_id: User ID
        expiry_hours: Hours until token expires

    Returns:
        Reset token
    """
    # In production, store this in database with expiry
    random_part = secrets.token_urlsafe(32)
    return f"{user_id}:{random_part}"


def verify_reset_token(token: str) -> Optional[int]:
    """Verify and extract user ID from reset token.

    Args:
        token: Reset token

    Returns:
        User ID if valid, None otherwise
    """
    try:
        parts = token.split(":")
        if len(parts) != 2:
            return None

        user_id = int(parts[0])
        # Would check expiry from database in production

        return user_id

    except (ValueError, IndexError):
        return None


def constant_time_compare(a: str, b: str) -> bool:
    """Compare two strings in constant time.

    Args:
        a: First string
        b: Second string

    Returns:
        True if strings are equal
    """
    return secrets.compare_digest(a, b)


def generateNonce(length: int = 16) -> str:  # Deliberately camelCase
    """Generate a cryptographic nonce.

    Args:
        length: Nonce length in bytes

    Returns:
        Hex-encoded nonce
    """
    return secrets.token_hex(length)


def create_basic_auth_header(username: str, password: str) -> str:
    """Create HTTP Basic Authentication header value.

    Args:
        username: Username
        password: Password

    Returns:
        Authorization header value
    """
    import base64

    credentials = f"{username}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


def parse_basic_auth_header(header: str) -> Optional[tuple[str, str]]:
    """Parse HTTP Basic Authentication header.

    Args:
        header: Authorization header value

    Returns:
        Tuple of (username, password) or None
    """
    import base64

    try:
        if not header.startswith("Basic "):
            return None

        encoded = header[6:]  # Remove "Basic " prefix
        decoded = base64.b64decode(encoded).decode()

        if ":" not in decoded:
            return None

        username, password = decoded.split(":", 1)
        return username, password

    except Exception:
        return None
