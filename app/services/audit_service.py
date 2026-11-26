import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def log_audit_event(user_id: int, action: str, resource_id: int) -> None:
    """Record an audit log entry for task mutations."""
    timestamp = datetime.utcnow().isoformat()
    logger.info(
        "Audit event: user=%s action=%s resource=%s at=%s",
        user_id,
        action,
        resource_id,
        timestamp
    

