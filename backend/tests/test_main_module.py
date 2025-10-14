# imports for test runtime are minimal; conftest sets env and path

from fastapi.testclient import TestClient

import backend.main as main

# sys.path manipulation moved to conftest.py


def test_protected_endpoint_requires_auth():
    with TestClient(main.app) as c:
        r = c.get("/api/protected")
        assert r.status_code == 401
        assert r.headers.get("WWW-Authenticate") == "Bearer"


def test_login_and_protected_with_token():
    # Use the in-app create_jwt_token helper (selects simple JWT in tests)
    token = main.create_jwt_token("u1", "t@example.com", "tester")
    with TestClient(main.app) as c:
        r = c.get("/api/protected", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        data = r.json()
        assert "user_info" in data
