import os
import sys

import pytest

# Ensure backend package root is on sys.path for imports when running tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient

from backend import database
from backend.database import DatabaseError
from backend.main import app, create_jwt_token


@pytest.fixture(name="client")
def client_fixture():
    with TestClient(app) as c:
        yield c


def _auth_headers():
    token = create_jwt_token("123", "test@example.com", "tester")
    return {"Authorization": f"Bearer {token}"}


def test_get_projects_database_error_maps_to_500(monkeypatch, client):
    def raise_db(*args, **kwargs):
        raise DatabaseError("simulated db failure")

    monkeypatch.setattr(database.db, "get_projects", raise_db)

    resp = client.get("/api/projects", headers=_auth_headers())
    assert resp.status_code == 500
    assert "Database error" in resp.json().get("detail", "")


def test_create_project_value_error_maps_to_400(monkeypatch, client):
    def raise_val(*args, **kwargs):
        raise ValueError("invalid project payload")

    monkeypatch.setattr(database.db, "create_project", raise_val)

    payload = {
        "name": "Bad Project",
        "client_name": "Bad",
        "address": "Nowhere",
        "current_reserve_balance": 0.0,
        "custom_fields": {},
    }

    resp = client.post("/api/projects", json=payload, headers=_auth_headers())
    assert resp.status_code == 400


def test_create_project_database_error_maps_to_500(monkeypatch, client):
    def raise_db(*args, **kwargs):
        raise DatabaseError("create failed")

    monkeypatch.setattr(database.db, "create_project", raise_db)

    payload = {
        "name": "Fail Project",
        "client_name": "Fail",
        "address": "Nowhere",
        "current_reserve_balance": 0.0,
        "custom_fields": {},
    }

    resp = client.post("/api/projects", json=payload, headers=_auth_headers())
    assert resp.status_code == 500
    assert "Database error" in resp.json().get("detail", "")
