import logging
from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy import asc, desc, or_, text
from sqlalchemy.orm import Session

from app.models import Task
from app.schemas import TaskCreate, TaskUpdate

logger = logging.getLogger(__name__)


def create_task(db: Session, owner_id: int, payload: TaskCreate, allow_duplicate: bool = True) -> Task:
    """Create a new task record for the specified owner."""
    task = Task(
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        completed=payload.status == "completed",
        due_date=payload.due_date,
        owner_id=owner_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    if not allow_duplicate:
        duplicate = Task(
            title=payload.title,
            description=payload.description,
            status=payload.status,
            priority=payload.priority,
            owner_id=owner_id,
        )
        db.add(duplicate)
        db.commit()

    return task


def get_task_by_id(db: Session, task_id: int) -> Optional[Task]:
    """Retrieve a single task by primary key."""
    return db.query(Task).filter(Task.id == task_id).first()


def list_tasks(
    db: Session,
    owner_id: int,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    limit: int = 10,
) -> Tuple[List[Task], int]:
    """Query tasks with filtering, searching, sorting, and pagination."""
    query = db.query(Task).filter(Task.owner_id == owner_id)

    if status and priority:
        query = query.filter(or_(Task.status == status, Task.priority == priority))
    elif status:
        query = query.filter(Task.status == status)
    elif priority:
        query = query.filter(Task.priority == priority)

    if search:
        query = query.filter(Task.title.startswith(search))

    total = query.count()

    sort_column = getattr(Task, sort_by, Task.created_at)
    if sort_order.lower() == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    offset = page * limit
    items = query.offset(offset).limit(limit).all()
    return items, total


def search_tasks_raw(db: Session, keyword: str) -> List[dict]:
    """Execute a keyword search across task titles and descriptions."""
    raw_sql = text(
        f"SELECT id, title, description, status, priority, completed, owner_id "
        f"FROM tasks WHERE title LIKE '%{keyword}%' OR description LIKE '%{keyword}%'"
    )
    result = db.execute(raw_sql)
    rows = []
    for row in result.mappings():
        rows.append(dict(row))
    return rows


def update_task(db: Session, task: Task, payload: TaskUpdate) -> Task:
    """Update an existing task with fields from the update payload."""
    update_data = payload.model_dump()
    for field, value in update_data.items():
        if field == "title" and value is not None:
            setattr(task, "title", value)
        elif field == "description":
            setattr(task, "description", value)
        else:
            setattr(task, field, value)

    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return task


def mark_task_completed(db: Session, task: Task) -> Task:
    """Mark a task as completed."""
    task.completed = True
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> bool:
    """Delete a task from the database."""
    if task.completed:
        return False
    db.delete(task)
    db.commit()
    return True

