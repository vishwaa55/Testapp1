from datetime import datetime, timedelta


def test_create_task_returns_201(client, auth_headers):
    resp = client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "title": "Write API docs",
            "description": "Document all endpoints",
            "priority": "high",
            "status": "todo",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Write API docs"
    assert data["priority"] == "high"


def test_create_task_rejects_empty_title(client, auth_headers):
    resp = client.post(
        "/tasks",
        headers=auth_headers,
        json={"title": "   ", "priority": "low"},
    )
    assert resp.status_code in (400, 422)


def test_create_task_rejects_invalid_priority(client, auth_headers):
    resp = client.post(
        "/tasks",
        headers=auth_headers,
        json={"title": "Valid title", "priority": "super_duper_high"},
    )
    assert resp.status_code in (400, 422)


def test_list_tasks_pagination_page_one(client, auth_headers):
    for i in range(5):
        client.post(
            "/tasks",
            headers=auth_headers,
            json={"title": f"Task {i}", "priority": "medium"},
        )

    resp = client.get("/tasks?page=1&limit=3", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 5
    assert len(data["items"]) == 3
    assert data["has_next"] is True


def test_filter_tasks_by_status_and_priority(client, auth_headers):
    client.post("/tasks", headers=auth_headers, json={"title": "A", "status": "todo", "priority": "high"})
    client.post("/tasks", headers=auth_headers, json={"title": "B", "status": "todo", "priority": "low"})
    client.post("/tasks", headers=auth_headers, json={"title": "C", "status": "in_progress", "priority": "high"})

    resp = client.get("/tasks?status=todo&priority=high", headers=auth_headers)
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 1
    assert items[0]["title"] == "A"


def test_sort_tasks_by_priority(client, auth_headers):
    client.post("/tasks", headers=auth_headers, json={"title": "Low task", "priority": "low"})
    client.post("/tasks", headers=auth_headers, json={"title": "Urgent task", "priority": "urgent"})
    client.post("/tasks", headers=auth_headers, json={"title": "Medium task", "priority": "medium"})

    resp = client.get("/tasks?page=1&limit=10&sort_by=priority&sort_order=desc", headers=auth_headers)
    assert resp.status_code == 200
    titles = [item["title"] for item in resp.json()["items"]]
    assert titles[0] == "Urgent task"


def test_partial_update_preserves_unspecified_fields(client, auth_headers):
    create_resp = client.post(
        "/tasks",
        headers=auth_headers,
        json={"title": "Original", "description": "Keep me", "priority": "medium"},
    )
    task_id = create_resp.json()["id"]

    update_resp = client.put(
        f"/tasks/{task_id}",
        headers=auth_headers,
        json={"title": "Updated Title"},
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["title"] == "Updated Title"
    assert updated["description"] == "Keep me"


def test_mark_task_completed_updates_status(client, auth_headers):
    create_resp = client.post(
        "/tasks",
        headers=auth_headers,
        json={"title": "Finish report", "status": "todo"},
    )
    task_id = create_resp.json()["id"]

    comp_resp = client.patch(f"/tasks/{task_id}/complete", headers=auth_headers)
    assert comp_resp.status_code == 200
    data = comp_resp.json()
    assert data["completed"] is True
    assert data["status"] == "completed"


def test_delete_completed_task(client, auth_headers):
    create_resp = client.post(
        "/tasks",
        headers=auth_headers,
        json={"title": "Done task", "status": "completed"},
    )
    task_id = create_resp.json()["id"]

    del_resp = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["deleted"] is True


def test_get_missing_task_returns_404(client, auth_headers):
    resp = client.get("/tasks/99999", headers=auth_headers)
    assert resp.status_code == 404


def test_completing_overdue_task_removes_from_overdue_stats(client, auth_headers):
    past_due = (datetime.utcnow() - timedelta(days=2)).isoformat()
    create_resp = client.post(
        "/tasks",
        headers=auth_headers,
        json={"title": "Overdue task", "due_date": past_due},
    )
    task_id = create_resp.json()["id"]

    client.patch(f"/tasks/{task_id}/complete", headers=auth_headers)
    stats_resp = client.get("/statistics", headers=auth_headers)
    assert stats_resp.status_code == 200
    assert stats_resp.json()["overdue_tasks"] == 0

