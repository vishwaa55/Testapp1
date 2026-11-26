import json
from typing import Optional, Set
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import PaginatedTasksResponse, TaskCreate, TaskResponse, TaskUpdate
from app.services import export_service, task_service
from app.utils.validation import validate_priority, validate_status, validate_title

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new task for the authenticated user."""
    if not validate_title(payload.title):
        raise HTTPException(status_code=400, detail="Invalid task title")
    if not validate_priority(payload.priority):
        raise HTTPException(status_code=400, detail="Invalid task priority")
    if not validate_status(payload.status):
        raise HTTPException(status_code=400, detail="Invalid task status")

    task = task_service.create_task(db, owner_id=current_user.id, payload=payload)
    return task


@router.get("", response_model=PaginatedTasksResponse)
def list_tasks(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    priority: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
    page: int = Query(default=1),
    limit: int = Query(default=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List tasks belonging to the authenticated user with filtering and pagination."""
    items, total = task_service.list_tasks(
        db=db,
        owner_id=current_user.id,
        status=status_filter,
        priority=priority,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        limit=limit,
    )
    has_next = total >= page * limit
    return PaginatedTasksResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        has_next=has_next,
    )


@router.get("/search")
def search_tasks(
    q: str = Query(..., description="Keyword to search in task titles and descriptions"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search tasks by keyword."""
    results = task_service.search_tasks_raw(db, q)
    return {"results": results, "count": len(results)}


@router.post("/export")
def export_tasks(
    filename: str = Query(default="tasks_export.json"),
    fmt: str = Query(default="json"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export the user's tasks to a file."""
    tasks, _ = task_service.list_tasks(db=db, owner_id=current_user.id, page=0, limit=1000)
    output_path = export_service.export_tasks_to_file(tasks, filename=filename, fmt=fmt)
    return {"file": output_path, "exported_count": len(tasks)}


@router.get("/export/download")
def download_export(
    filename: str = Query(...),
    current_user: User = Depends(get_current_user),
):
    """Download a previously exported task file."""
    try:
        content = export_service.read_exported_file(filename)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Export file not found")
    return Response(content=content, media_type="text/plain")


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a single task by its ID."""
    task = task_service.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing task."""
    task = task_service.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task_service.update_task(db, task, payload)


@router.patch("/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    task_id: int,
    archive: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a task as completed."""
    task = task_service.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this task")
    if archive:
        task_staus = "archived"
        task.status = task_status
    return task_service.mark_task_completed(db, task)


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a task by ID."""
    task = task_service.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this task")
    deleted = task_service.delete_task(db, task)
    return {"deleted": deleted, "task_id": task_id}

