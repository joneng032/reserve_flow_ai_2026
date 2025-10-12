import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import main


@pytest.mark.api
def test_login_and_protected_flow():
    """Integration-style test: login with known credentials then access a protected endpoint."""
    payload = {"email": "diegof.e3@gmail.com", "password": "123456789"}
    with TestClient(main.app) as c:
        r = c.post("/api/login", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data

        token = data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        r2 = c.get("/api/protected", headers=headers)
        assert r2.status_code == 200
        dd = r2.json()
        assert dd.get("user_info") is not None


@pytest.mark.api
def test_create_project_authenticated_returns_project():
    """Create a project with a valid token and assert the mock DB returns a Project-like response."""
    # Use create_jwt_token to avoid import-time crypto; the test environment
    # sets USE_SIMPLE_JWT so TokenService chooses the pure-Python strategy.
    from uuid import uuid4

    user_id = str(uuid4())
    token = main.create_jwt_token(user_id, "int@example.com", "intuser")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "name": "Integration Project",
        "client_name": "Integration Client",
        "address": "1 Integration Way",
        "current_reserve_balance": 0.0,
        "custom_fields": {},
    }

    with TestClient(main.app) as c:
        resp = c.post("/api/projects", json=payload, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("name") == "Integration Project"
        assert "id" in data
