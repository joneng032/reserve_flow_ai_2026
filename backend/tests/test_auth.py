import os
import sys

import pytest
from fastapi.testclient import TestClient

# Ensure backend directory is on sys.path so tests can import main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app, create_jwt_token


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_register_and_login(client: TestClient):
    # Test register endpoint
    payload = {
        "email": "test@example.com",
        "password": "pass1234",
        "username": "tester",
    }
    resp = client.post("/api/register", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data

    # Test login with the fixed demo account returns token
    login_payload = {"email": "diegof.e3@gmail.com", "password": "123456789"}
    resp = client.post("/api/login", json=login_payload)
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_protected_endpoint_requires_token(client: TestClient):
    # No token should be rejected
    resp = client.get("/api/protected")
    # Standardized behavior: missing credentials -> 401 Unauthorized
    assert resp.status_code == 401
    # Ensure WWW-Authenticate header is present so clients can react
    assert resp.headers.get("WWW-Authenticate") == "Bearer"

    # Use a valid token
    token = create_jwt_token("123", "diegof.e3@gmail.com", "diegof.e3")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/api/protected", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "user_info" in data


def test_protected_endpoint_invalid_and_expired_tokens(client: TestClient):
    # Invalid token should be rejected and must include WWW-Authenticate
    headers = {"Authorization": "Bearer this.is.not.a.valid.token"}
    resp = client.get("/api/protected", headers=headers)
    assert resp.status_code == 401
    assert resp.headers.get("WWW-Authenticate") == "Bearer"


def test_auth_service_validate_token_propagates_unexpected_errors(monkeypatch, client):
    """Simulate an unexpected error in user repository to ensure it propagates."""
    from app.services.auth_service import AuthService

    svc = AuthService()

    # Monkeypatch token_service to return a username, but user repository to raise
    monkeypatch.setattr(
        svc,
        "token_service",
        type(
            "T", (), {"get_username_from_token": lambda self, t: "nonexistent_user"}
        )(),
    )

    def raise_db_error(username):
        raise RuntimeError("DB connection lost")

    monkeypatch.setattr(svc.user_repository, "get_user_by_username", raise_db_error)

    with pytest.raises(RuntimeError):
        svc.validate_token("some-token")

    # Expired token should be rejected and include WWW-Authenticate
    # Use TokenService to create an explicitly expired token. TokenService
    # will select a pure-Python fallback under tests (see tests/conftest.py)
    # so this does not require importing heavy native crypto libraries.
    from datetime import timedelta

    from app.services.token_service import TokenService

    svc = TokenService()
    expired_token = svc.create_access_token(
        {"sub": "123", "email": "expired@example.com", "username": "expired_user"},
        expires_delta=timedelta(minutes=-5),
    )
    headers = {"Authorization": f"Bearer {expired_token}"}
    resp = client.get("/api/protected", headers=headers)
    assert resp.status_code == 401
    assert resp.headers.get("WWW-Authenticate") == "Bearer"
