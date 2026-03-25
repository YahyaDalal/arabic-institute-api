import re
import bleach


def sanitize_string(value):
    """Strip HTML tags and dangerous characters from string input."""
    if not isinstance(value, str):
        return value
    # Remove HTML tags
    cleaned = bleach.clean(value, tags=[], strip=True)
    # Strip leading/trailing whitespace
    cleaned = cleaned.strip()
    return cleaned


def sanitize_email(value):
    """Validate and sanitize email input."""
    if not isinstance(value, str):
        return value
    value = value.strip().lower()
    # Basic email pattern check
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, value):
        return value
    return value
