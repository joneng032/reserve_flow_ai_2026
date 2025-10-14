# imports for test runtime are minimal; conftest sets env and path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from backend import database
from backend.main import app, create_jwt_token

# Ensure backend package root is on sys.path for imports when running tests
# sys.path manipulation moved to conftest.py


@pytest.fixture(name="client")
def client_fixture():
    with TestClient(app) as c:
        yield c


def _auth_headers():
    token = create_jwt_token("123", "test@example.com", "tester")
    return {"Authorization": f"Bearer {token}"}


def test_get_meeting_returns_404_on_project_mismatch(monkeypatch, client):
    # db.get_meeting should return a resource whose project_id does not match
    monkeypatch.setattr(
        database.db,
        "get_meeting",
        lambda meeting_id, profile_id: SimpleNamespace(
            project_id="other-project", id=meeting_id
        ),
    )

    resp = client.get(
        "/api/projects/my-project/meetings/meeting-1", headers=_auth_headers()
    )
    assert resp.status_code == 404
    assert "Meeting not found" in resp.json().get("detail", "")


def test_get_media_file_returns_404_on_project_mismatch(monkeypatch, client):
    monkeypatch.setattr(
        database.db,
        "get_media_file",
        lambda media_id, profile_id: SimpleNamespace(project_id="other", id=media_id),
    )

    resp = client.get(
        "/api/projects/my-project/media-files/media-1", headers=_auth_headers()
    )
    assert resp.status_code == 404
    assert "Media file not found" in resp.json().get("detail", "")


def test_get_evidence_returns_404_on_project_mismatch(monkeypatch, client):
    monkeypatch.setattr(
        database.db,
        "get_evidence",
        lambda evidence_id, profile_id: SimpleNamespace(
            project_id="different", id=evidence_id
        ),
    )

    resp = client.get("/api/projects/my-project/evidence/e-1", headers=_auth_headers())
    assert resp.status_code == 404
    assert "Evidence not found" in resp.json().get("detail", "")
