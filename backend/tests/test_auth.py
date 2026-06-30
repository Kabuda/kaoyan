import os

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["JWT_SECRET"] = "test-secret-for-kaoyan-auth"
os.environ["INITIAL_ADMIN_USERNAME"] = "admin"
os.environ["INITIAL_ADMIN_PASSWORD"] = "change-me-now"

from fastapi.testclient import TestClient

from app.main import app


def test_health_check() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login_and_read_current_user() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "change-me-now"},
        )
        assert login_response.status_code == 200

        token = login_response.json()["access_token"]
        me_response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert me_response.status_code == 200
    assert me_response.json()["username"] == "admin"


def test_protected_endpoint_requires_token() -> None:
    with TestClient(app) as client:
        response = client.get("/api/auth/me")

    assert response.status_code == 401


def test_login_rejects_bad_password() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "bad-password"},
        )

    assert response.status_code == 401

