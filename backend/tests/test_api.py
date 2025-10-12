"""
Unit tests for Reserve Flow AI backend
"""
import os
import sys
from typing import Generator

import pytest
from fastapi.testclient import TestClient

# Ensure backend package root is on sys.path for imports when running tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from uuid import uuid4

from main import app, create_jwt_token


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Test client fixture"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.unit
class TestHealthEndpoint:
    """Test health endpoint functionality"""

    def test_health_endpoint_returns_200(self, client: TestClient) -> None:
        """Test that health endpoint returns 200 status"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_returns_json(self, client: TestClient) -> None:
        """Test that health endpoint returns JSON"""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"

    def test_health_endpoint_has_status_field(self, client: TestClient) -> None:
        """Test that health response contains status field"""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


@pytest.mark.unit
class TestRootEndpoint:
    """Test root endpoint functionality"""

    def test_root_endpoint_returns_200(self, client: TestClient) -> None:
        """Test that root endpoint returns 200 status"""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_endpoint_returns_welcome_message(self, client: TestClient) -> None:
        """Test that root endpoint returns welcome message"""
        response = client.get("/")
        data = response.json()
        assert "message" in data
        # Accept either the English welcome text or the Spanish message
        msg = data["message"]
        assert ("Reserve Flow AI" in msg) or ("Autenticación" in msg)


@pytest.mark.api
class TestAPIEndpoints:
    """Test API endpoint structure"""

    def test_api_projects_endpoint_exists(self, client: TestClient) -> None:
        """Test that projects endpoint exists"""
        # Unauthenticated request should be rejected
        response = client.get("/api/projects")
        # Standardized preference: missing credentials -> 401 Unauthorized
        assert response.status_code in [401, 422, 403]

        # Authenticated request should return 200 or 200-like response
        # Use create_jwt_token which defers heavy imports inside; safe to call here.
        token = create_jwt_token("123", "diegof.e3@gmail.com", "diegof.e3")
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/projects", headers=headers)
        assert response.status_code in [200, 404, 422]

    def test_openapi_docs_available(self, client: TestClient) -> None:
        """Test that OpenAPI docs are available"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    def test_create_project_authenticated_returns_project(
        self, client: TestClient
    ) -> None:
        """Integration-style test: POST /api/projects with a valid token should create a project in mock-mode"""
        user_id = str(uuid4())
        token = create_jwt_token(user_id, "test@example.com", "tester")
        headers = {"Authorization": f"Bearer {token}"}

        payload = {
            "name": "Integration Test Project",
            "client_name": "Integration Client",
            "address": "1 Test Plaza",
            # profile_id intentionally omitted to exercise the endpoint's behavior
            "current_reserve_balance": 0.0,
            "custom_fields": {},
        }

        resp = client.post("/api/projects", json=payload, headers=headers)
        # (previously printed debug output here during development)
        # In mock-mode the DB should accept the create and return a Project object
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("name") == "Integration Test Project"
        assert "id" in data
