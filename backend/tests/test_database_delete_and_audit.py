import types

from backend import database
from backend.tests.conftest import FakeClient, uuid4_str
from backend.models import MeetingCreate


def test_delete_interview_ownership_failure_returns_false():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    interview_id = uuid4_str()

    table_data = {
        "projects": [{"id": proj_id, "profile_id": uuid4_str()}],
        "interviews": [{"id": interview_id, "project_id": proj_id}],
    }

    database.db.client = FakeClient(table_data)

    ok = database.db.delete_interview(interview_id, profile_id)
    assert ok is False


def test_delete_inspection_ownership_failure_returns_false():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    insp_id = uuid4_str()

    table_data = {
        "projects": [{"id": proj_id, "profile_id": uuid4_str()}],
        "inspections": [{"id": insp_id, "project_id": proj_id}],
    }

    database.db.client = FakeClient(table_data)

    ok = database.db.delete_inspection(insp_id, profile_id)
    assert ok is False


def test_create_meeting_creates_audit(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    table_data = {"projects": [{"id": proj_id, "profile_id": profile_id}], "meetings": []}
    database.db.client = FakeClient(table_data)

    captured = {}

    def _cap(audit_data):
        captured["audit"] = audit_data
        return types.SimpleNamespace(id="a")

    monkeypatch.setattr(database.db, "create_audit_log", _cap)

    m = MeetingCreate(project_id=proj_id, title="T", meeting_date="2024-01-01T00:00:00Z", meeting_type="mock")
    created = database.db.create_meeting(m, profile_id)

    assert created is not None
    assert "audit" in captured
