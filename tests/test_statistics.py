from datetime import datetime, timedelta


def test_statistics_empty_database(client, auth_headers):
    resp = client.get("/statistics", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_tasks"] == 0
    assert data["completion_rate"] == 0.0


def test_statistics_scoped_to_current_user(client, auth_headers, second_user_headers):
    client.post("/tasks", headers=auth_headers, json={"title": "Alice task 1"})
    client.post("/tasks", headers=second_user_headers, json={"title": "Bob task 1"})
    client.post("/tasks", headers=second_user_headers, json={"title": "Bob task 2"})

    resp = client.get("/statistics", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["total_tasks"] == 1


def test_statistics_overdue_excludes_completed(client, auth_headers):
    past = (datetime.utcnow() - timedelta(days=3)).isoformat()
    future = (datetime.utcnow() + timedelta(days=3)).isoformat()

    client.post("/tasks", headers=auth_headers, json={"title": "Late open", "due_date": past, "status": "todo"})
    client.post("/tasks", headers=auth_headers, json={"title": "Late done", "due_date": past, "status": "completed"})
    client.post("/tasks", headers=auth_headers, json={"title": "Future open", "due_date": future, "status": "todo"})

    resp = client.get("/statistics", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["overdue_tasks"] == 1

