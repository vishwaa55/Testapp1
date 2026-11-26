import base64


def test_register_user_success(client):
    resp = client.post(
        "/users/register",
        json={
            "username": "charlie",
            "email": "charlie@example.com",
            "password": "Password123!",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "charlie"
    assert "hashed_password" not in data


def test_register_duplicate_username_rejected(client, registered_user):
    resp = client.post(
        "/users/register",
        json={
            "username": registered_user["payload"]["username"],
            "email": "other@example.com",
            "password": "AnotherPassword1!",
        },
    )
    assert resp.status_code in (400, 409)


def test_login_and_get_profile(client, registered_user):
    login_resp = client.post(
        "/users/login",
        json={
            "username": registered_user["payload"]["username"],
            "password": registered_user["payload"]["password"],
        },
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    me_resp = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["username"] == "alice"


def test_basic_auth_access(client, registered_user):
    creds = f"{registered_user['payload']['username']}:{registered_user['payload']['password']}"
    encoded = base64.b64encode(creds.encode("utf-8")).decode("utf-8")
    resp = client.get("/users/me", headers={"Authorization": f"Basic {encoded}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "alice@example.com"


def test_login_invalid_credentials(client, registered_user):
    resp = client.post(
        "/users/login",
        json={"username": "alice", "password": "wrong-password"},
    )
    assert resp.status_code == 401

