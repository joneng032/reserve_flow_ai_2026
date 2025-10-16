import types

from backend import database
from backend.tests.conftest import FakeClient, uuid4_str
from backend.models import MeetingCreate


def test_delete_interview_ownership_failure_returns_false():
    interview = {"id": uuid4_str(), "project_id": uuid4_str()}

    # Fake client will return no join match when checking ownership
    table_data = {"interviews": [interview], "projects": [{"id": uuid4_str(), "profile_id": uuid4_str()}]}
    database.db.client = FakeClient(table_data)

    result = database.db.delete_interview(interview["id"], profile_id=uuid4_str())

    assert result is False


def test_delete_inspection_ownership_failure_returns_false():
    inspection = {"id": uuid4_str(), "project_id": uuid4_str()}
    table_data = {"inspections": [inspection], "projects": [{"id": uuid4_str(), "profile_id": uuid4_str()}]}
    database.db.client = FakeClient(table_data)

    result = database.db.delete_inspection(inspection["id"], profile_id=uuid4_str())

    assert result is False


def test_create_meeting_creates_audit_log(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    table_data = {"projects": [{"id": proj_id, "profile_id": profile_id}], "meetings": []}
    database.db.client = FakeClient(table_data)

    captured = {}

    def _cap(audit_data):
        captured["audit"] = audit_data
        return types.SimpleNamespace(id=uuid4_str())

    monkeypatch.setattr(database.db, "create_audit_log", _cap)

    meeting_create = MeetingCreate(project_id=proj_id, title="T", meeting_date="2024-01-01T00:00:00Z", meeting_type="mock")
    created = database.db.create_meeting(meeting_create, profile_id)

    assert created is not None
    assert "audit" in captured
