import re
from datetime import datetime


def get_timestamp() -> str:
    """Return current UTC-local ISO 8601 timestamp."""
    return datetime.now().isoformat()


def get_date_str() -> str:
    """Return current date as YYYY-MM-DD string for directory naming."""
    return datetime.now().strftime("%Y-%m-%d")


def sanitize_tags(tags: list) -> list:
    """
    Normalize a list of tag strings.
    - Strips whitespace
    - Lowercases
    - Removes empty strings
    - Replaces spaces within tags with hyphens
    """
    cleaned = []
    for tag in tags:
        tag = tag.strip().lower().replace(" ", "-")
        if tag:
            cleaned.append(tag)
    return cleaned


def sanitize_filename(name: str) -> str:
    """
    Sanitize a string for safe use as a filename or directory name.
    - Strips leading/trailing whitespace
    - Replaces spaces with underscores
    - Removes characters that are not alphanumeric, underscores, hyphens, or dots
    - Lowercases the result
    """
    name = name.strip().lower()
    name = name.replace(" ", "_")
    name = re.sub(r"[^\w\-.]", "", name)
    return name


def sanitize_exercise(exercise: str) -> str:
    """
    Sanitize an exercise/engagement label for use in directory paths.
    Wrapper around sanitize_filename with a fallback to 'general'.
    """
    cleaned = sanitize_filename(exercise)
    return cleaned if cleaned else "general"
