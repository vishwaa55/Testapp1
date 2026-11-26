import base64
import json
import hashlib
import hmac
import time

from app.auth import SECRET_KEY


def test_task_ownership_enforced_on_get(client, auth_headers, second_user_headers):
    create_resp = client.post(
        "/tasks",
        headers=auth_headers,
        json={"title": "Alice Secret Task"},
    )
    task_id = create_resp.json()["id"]

    resp = client.get(f"/tasks/{task_id}", headers=second_user_headers)
    assert resp.status_code in (403, 404)


def test_task_ownership_enforced_on_update(client, auth_headers, second_user_headers):
    create_resp = client.post(
        "/tasks",
        headers=auth_headers,
        json={"title": "Alice Original Task"},
    )
    task_id = create_resp.json()["id"]

    resp = client.put(
        f"/tasks/{task_id}",
        headers=second_user_headers,
        json={"title": "Tampered by Bob"},
    )
    assert resp.status_code in (403, 404)


def test_search_prevents_sql_injection(client, auth_headers, second_user_headers):
    client.post("/tasks", headers=second_user_headers, json={"title": "Bob Private Task"})

    resp = client.get("/tasks/search?q=' OR '1'='1", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["count"] == 0


def test_export_download_blocks_path_traversal(client, auth_headers):
    resp = client.get(
        "/tasks/export/download?filename=../../requirements.txt",
        headers=auth_headers,
    )
    assert resp.status_code in (400, 403, 404)


def test_expired_token_is_rejected(client, registered_user):
    expired_payload = {
        "sub": "1",
        "username": "alice",
        "role": "user",
        "exp": int(time.time()) - 3600,
    }
    payload_bytes = json.dumps(expired_payload, separators=(",", ":")).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode("utf-8")
    sig = hmac.new(SECRET_KEY.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).hexdigest()
    expired_token = f"{payload_b64}.{sig}"

    resp = client.get("/users/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert resp.status_code == 401

