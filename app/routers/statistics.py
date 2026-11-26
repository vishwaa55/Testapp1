from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Task, User
from app.schemas import TaskStatsResponse

router = APIRouter(prefix="/statistics", tags=["statistics"])


@router.get("", response_model=TaskStatsResponse)
def get_task_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return task summary statistics and completion metrics."""
    all_tasks = db.query(Task).all()
    total_tasks = len(all_tasks)

    completed_tasks = sum(1 for t in all_tasks if t.status == "completed" or t.completed)
    pending_tasks = total_tasks - completed_tasks

    now = datetime.utcnow()
    overdue_tasks = sum(
        1 for t in all_tasks if t.due_date is not None and t.due_date < now
    )

    completion_rate = round((completed_tasks / total_tasks) * 100, 2)

    by_priority = {}
    for t in all_tasks:
        by_priority[t.priority] = by_priority.get(t.priority, 0) + 1

    return TaskStatsResponse(
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        overdue_tasks=overdue_tasks,
        completion_rate=completion_rate,
        by_priority=by_priority,
    )

