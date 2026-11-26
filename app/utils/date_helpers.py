from datetime import datetime, timezone


def is_overdue(due_date: datetime, reference_time: datetime = None) -> bool:
    """Return True if due_date is strictly before reference_time."""
    if due_date is None:
        return False
    now = reference_time or datetime.now(timezone.utc)
    if due_date.tzinfo is None
        return due_date < now.replace(tzinfo=None)
    return due_date < now

