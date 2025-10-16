import json
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert data.get("service") is not None


@patch("backend.main.TokenService.create_access_token", return_value="mock_access_token")
def test_register_endpoint(mock_create_token):
    payload = {
        "email": "testuser@example.com",
        "password": "password123",
        "username": "testuser",
    }

    resp = client.post("/api/register", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    # TokenService.create_access_token was used
    mock_create_token.assert_called_once()

    # Validate response shape
    assert "access_token" in data
    assert data["access_token"] == "mock_access_token"
    assert data["token_type"] == "bearer"
    assert "user" in data and data["user"]["email"] == payload["email"]


@patch(
    "backend.main.TokenService.verify_token",
    return_value={"sub": "123", "email": "authorized@example.com", "username": "authorized"},
)
def test_protected_endpoint_with_valid_token(mock_verify):
    headers = {"Authorization": "Bearer faketoken"}
    resp = client.get("/api/protected", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "message" in data
    assert "user_info" in data
    assert data["user_info"]["email"] == "authorized@example.com"
    mock_verify.assert_called_once()
