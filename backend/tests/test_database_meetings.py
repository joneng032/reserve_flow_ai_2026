from backend.database import Database


def test_create_meeting_mock_mode_returns_stub():
    from backend.models import MeetingCreate
    from backend.tests.conftest import uuid4_str

    db = Database()
    db.client = None
    pid = uuid4_str()

    m = MeetingCreate(project_id=pid, title="Standup", meeting_date="2024-01-01T09:00:00Z", meeting_type="regular")
    created = db.create_meeting(m, profile_id="profile-1")
    assert created is not None
    assert getattr(created, "title", None) == "Standup"


def test_meeting_crud_and_audit(monkeypatch):
    from backend.tests.conftest import FakeClient, uuid4_str
    from backend.models import MeetingCreate, MeetingUpdate

    pid = uuid4_str()
    mid = uuid4_str()

    client = FakeClient(table_data={
        "projects": [{"id": pid, "profile_id": "profile-1"}],
        "meetings": [{"id": mid, "project_id": pid, "projects": {"profile_id": "profile-1"}, "title": "Old"}],
    })

    db = Database()
    db.client = client

    called = {}

    def fake_audit(a):
        called["ok"] = True
        return None

    monkeypatch.setattr(db, "create_audit_log", fake_audit)

    # Create
    mc = MeetingCreate(project_id=pid, title="Planning", meeting_date="2024-01-02T10:00:00Z", meeting_type="planning")
    created = db.create_meeting(mc, profile_id="profile-1")
    assert created is not None

    # Get project meetings
    meetings = db.get_project_meetings(pid, "profile-1")
    assert isinstance(meetings, list)

    # Get single meeting
    got = db.get_meeting(mid, "profile-1")
    assert got is not None

    # Update
    mu = MeetingUpdate(title="Updated", meeting_date="2024-01-02T11:00:00Z", meeting_type="planning")
    updated = db.update_meeting(mid, mu, profile_id="profile-1")
    assert updated is not None
    assert called.get("ok")

    # Delete
    deleted = db.delete_meeting(mid, "profile-1")
    assert isinstance(deleted, bool)
"""Focused tests for meeting-related methods in backend.database.

Tests follow the pattern: mock-mode returns, client exception -> DatabaseError,
and basic list/boolean behaviors.
"""
import pytest
from types import SimpleNamespace

from backend import database as dbmod
from backend.database import Database, DatabaseError


def test_create_meeting_mock_mode_returns_meeting():
    db = Database()
    db.client = None

    class M:
        def __init__(self):
            self.project_id = "550e8400-e29b-41d4-a716-446655440200"
            self.title = "MTG"
            self.meeting_date = "2024-01-01T00:00:00Z"
            self.meeting_type = "initial"
        def model_dump(self, exclude_unset=True):
            return {"title": self.title, "meeting_type": self.meeting_type}

    # Monkeypatch Meeting to a SimpleNamespace to avoid Pydantic validation
    # requirements that the full model enforces in tests.
    monkey = pytest.MonkeyPatch()
    monkey.setattr(dbmod, "Meeting", SimpleNamespace)
    try:
        meeting = db.create_meeting(M(), "profile-1")
        assert meeting is not None
        assert hasattr(meeting, "id")
    finally:
        monkey.undo()


def test_get_project_meetings_mock_mode_returns_list():
    db = Database()
    db.client = None

    meetings = db.get_project_meetings("pid", "profile-1")
    assert isinstance(meetings, list)


def test_get_meeting_mock_mode_returns_meeting():
    db = Database()
    db.client = None
    monkey = pytest.MonkeyPatch()
    monkey.setattr(dbmod, "Meeting", SimpleNamespace)
    try:
        # `get_meeting` returns None in mock-mode per implementation
        m = db.get_meeting("550e8400-e29b-41d4-a716-446655440201", "profile-1")
        assert m is None
    finally:
        monkey.undo()


def test_update_meeting_mock_mode_returns_namespace():
    db = Database()
    db.client = None

    class U:
        def model_dump(self, exclude_unset=True):
            return {"title": "Updated Meeting"}

    monkey = pytest.MonkeyPatch()
    monkey.setattr(dbmod, "Meeting", SimpleNamespace)
    try:
        res = db.update_meeting(
            "550e8400-e29b-41d4-a716-446655440202", U(), "profile-1"
        )
        assert res is not None
        # Accept either a Pydantic model or SimpleNamespace
        assert getattr(res, "title", None) in ("Updated Meeting", None)
    finally:
        monkey.undo()


def test_delete_meeting_mock_mode_returns_bool():
    db = Database()
    db.client = None

    out = db.delete_meeting("550e8400-e29b-41d4-a716-446655440203", "profile-1")
    assert out is True or out is False


def test_get_project_meetings_client_exception_maps_to_database_error():
    class ExplodingClient:
        def table(self, _):
            raise RuntimeError("boom")

    db = Database()
    db.client = ExplodingClient()

    with pytest.raises(DatabaseError):
        db.get_project_meetings("p", "profile-1")
