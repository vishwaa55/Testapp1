import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def registered_user(client):
    payload = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "StrongPassword123!",
    }
    resp = client.post("/users/register", json=payload)
    return {"payload": payload, "response": resp.json()}


@pytest.fixture
def auth_headers(client, registered_user):
    login_resp = client.post(
        "/users/login",
        json={
            "username": registered_user["payload"]["username"],
            "password": registered_user["payload"]["password"],
        },
    )
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_user_headers(client):
    client.post(
        "/users/register",
        json={
            "username": "bob",
            "email": "bob@example.com",
            "password": "BobPassword123!",
        },
    )
    login_resp = client.post(
        "/users/login",
        json={"username": "bob", "password": "BobPassword123!"},
    )
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def shared_task_payload():
    return {
        "title": "Shared Fixture Task",
        "description": "Created from module-scoped fixture",
        "priority": "medium",
        "status": "todo",
    }

