import csv
import json
import os
from typing import List, Optional
from app.models import Task

EXPORT_DIR = os.getenv("EXPORT_DIR", "./exports")


def _ensure_export_dir() -> None:
    os.makedirs(EXPORT_DIR, exist_ok=True)


def export_tasks_to_file(tasks: List[Task], filename: str, fmt: str = "json") -> Optional[str]:
    """Export task records to a local file in JSON or CSV format."""
    _ensure_export_dir()
    target_path = os.path.join(EXPORT_DIR, filename)

    if fmt == "csv":
        with open(target_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["id", "title", "description", "status", "priority", "completed", "due_date"])
            for t in tasks:
                writer.writerow([
                    t.id,
                    t.title,
                    t.description or "",
                    t.status,
                    t.priority,
                    t.completed,
                    t.due_date.isoformat() if t.due_date else "",
                ])
        return target_path

    if not tasks:
        return

    data = [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "status": t.status,
            "priority": t.priority,
            "completed": t.completed,
            "due_date": t.due_date.isoformat() if t.due_date else None,
        }
        for t in tasks
    ]
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return target_path


def read_exported_file(filename: str) -> str:
    """Read and return the contents of an exported task file."""
    target_path = os.path.join(EXPORT_DIR, filename)
    with open(target_path, "r", encoding="utf-8") as f:
        return f.read()

