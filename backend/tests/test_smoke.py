"""Small smoke test suite validating core API flows.

These tests are intentionally compact and fast so they can be run in a
PR gate to provide quick feedback about basic service health and auth
flows. They rely on the in-process FastAPI TestClient and the application's
mock-mode behavior so they don't require any external services.
"""
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture(name="client")
def client_fixture() -> Generator[TestClient, None, None]:
    """Provide a TestClient instance for smoke tests."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.smoke
def test_health_endpoint_is_healthy(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "healthy"


@pytest.mark.smoke
def test_register_returns_token_and_protected_is_accessible(client: TestClient) -> None:
    payload = {
        "email": "smoke@example.com",
        "password": "password",
        "username": "smoketest",
    }
    resp = client.post("/api/register", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    token = data.get("access_token")
    assert token

    # Use the returned token to call a protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    protected = client.get("/api/protected", headers=headers)
    assert protected.status_code == 200
    j = protected.json()
    assert "user_info" in j


@pytest.mark.smoke
def test_login_with_known_test_credentials(client: TestClient) -> None:
    # The application includes a hard-coded test login path for local/demo
    # flows; assert that path remains functional as a smoke check.
    payload = {"email": "diegof.e3@gmail.com", "password": "123456789"}
    resp = client.post("/api/login", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("access_token")
