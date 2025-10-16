from backend import database
from backend.tests.conftest import FakeClient, uuid4_str
from backend.models import InterviewCreate, InterviewUpdate
import types


def test_create_interview_creates_audit(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "interviews": []})

    cap = {}
    def _cap(a):
        cap["audit"] = a
        return types.SimpleNamespace(id=uuid4_str())

    monkeypatch.setattr(database.db, "create_audit_log", _cap)

    ic = InterviewCreate(project_id=proj_id, interviewee_name="Bob", interview_type="mock")
    created = database.db.create_interview(ic, profile_id)

    assert created is not None
    assert "audit" in cap


def test_update_interview_creates_audit(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    ii = uuid4_str()
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "interviews": [{"id": ii, "project_id": proj_id}]})

    cap = {}
    monkeypatch.setattr(database.db, "create_audit_log", lambda a: cap.setdefault("audit", a) or types.SimpleNamespace(id=uuid4_str()))

    iu = InterviewUpdate(interviewee_name="Alice", interview_type="mock")
    res = database.db.update_interview(ii, iu, profile_id)

    assert res is not None
    assert "audit" in cap


def test_delete_interview_creates_audit(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    ii = uuid4_str()
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "interviews": [{"id": ii, "project_id": proj_id}]})

    cap = {}
    monkeypatch.setattr(database.db, "create_audit_log", lambda a: cap.setdefault("audit", a) or types.SimpleNamespace(id=uuid4_str()))

    ok = database.db.delete_interview(ii, profile_id)
    assert ok is True or ok is not None
    assert "audit" in cap
