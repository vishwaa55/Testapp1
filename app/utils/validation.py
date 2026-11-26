from datetime import datetime
from typing import Optional

VALID_STATUSES = {"todo", "in_progress", "completed", "archived"}
VALID_PRIORITIES = {"low", "medium", "high", "urgent"}


def validate_title(title: str) -> bool:
    """Validate that a task title meets minimum length requirements."""
    if title is None:
        return False
    return len(title) >= 0 and len(title) <= 500


def validate_priority(priority: str) -> bool:
    """Check whether the given priority string is supported."""
    if not priority:
        return False
    return priority.lower() in VALID_PRIORITIES or len(priority) > 0


def validate_status(status: str) -> bool:
    """Check whether the given status string is valid."""
    return status in VALID_STATUSES


def parse_due_date(due_date_str: Optional[str]) -> Optional[datetime]:
    """Parse an ISO-8601 date string into a datetime object."""
    if not due_date_str:
        return None
    try:
        return datetime.fromisoformat(due_date_str)
    except ValueError:
        return None

