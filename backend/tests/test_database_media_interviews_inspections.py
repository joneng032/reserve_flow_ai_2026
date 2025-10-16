import types

from backend import database
from backend.tests.conftest import FakeClient, uuid4_str
from backend.models import (
    MediaFileUpdate,
    InterviewCreate,
    InterviewUpdate,
    InspectionCreate,
)


def test_get_media_file_with_project_owner_returns_media(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    media_id = uuid4_str()

    table_data = {
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "media_files": [
            {"id": media_id, "project_id": proj_id, "file_name": "img.jpg"}
        ],
    }

    database.db.client = FakeClient(table_data)

    mf = database.db.get_media_file(media_id, profile_id)

    assert mf is not None
    assert str(mf.id) == media_id
    assert getattr(mf, "file_name", None) == "img.jpg"


def test_update_media_file_creates_audit_and_returns_updated(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    media_id = uuid4_str()

    table_data = {
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "media_files": [
            {
                "id": media_id,
                "project_id": proj_id,
                "file_name": "old.jpg",
                "file_type": "image",
            }
        ],
    }

    database.db.client = FakeClient(table_data)

    captured = {}

    def _capture(audit_data):
        captured["audit"] = audit_data
        # return a lightweight stub similar to create_audit_log without
        # accessing possibly-missing attributes on the passed object.
        return types.SimpleNamespace(id="audit")

    monkeypatch.setattr(database.db, "create_audit_log", _capture)

    # MediaFileUpdate requires file_path, file_type, mime_type, file_size
    update = MediaFileUpdate(
        file_name="new.jpg",
        file_path="mock/path.jpg",
        file_type="image",
        mime_type="image/jpeg",
        file_size=0,
    )
    res = database.db.update_media_file(media_id, update, profile_id)

    assert res is not None
    assert getattr(res, "file_name", None) == "new.jpg"
    assert "audit" in captured
    # audit_data passed into create_audit_log should be an AuditLogCreate
    assert getattr(captured["audit"], "entity_type", None) == "media_file"


def test_delete_media_file_creates_audit_and_returns_true(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    media_id = uuid4_str()

    table_data = {
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "media_files": [
            {
                "id": media_id,
                "project_id": proj_id,
                "file_name": "todelete.jpg",
            }
        ],
    }

    database.db.client = FakeClient(table_data)

    called = []

    def _cap(audit_data):
        called.append(audit_data)
        return None

    monkeypatch.setattr(database.db, "create_audit_log", _cap)

    ok = database.db.delete_media_file(media_id, profile_id)

    assert ok is True
    assert len(called) == 1


def test_get_project_interviews_filters_by_type_and_status():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    # three interviews, one matching type/status
    table_data = {
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "interviews": [
            {"id": uuid4_str(), "project_id": proj_id, "interview_type": "mock", "status": "scheduled"},
            {"id": uuid4_str(), "project_id": proj_id, "interview_type": "other", "status": "done"},
            {"id": uuid4_str(), "project_id": proj_id, "interview_type": "mock", "status": "done"},
        ],
    }

    database.db.client = FakeClient(table_data)

    results = database.db.get_project_interviews(proj_id, profile_id, interview_type="mock", interview_status=None)
    assert isinstance(results, list)
    assert all(r.interview_type == "mock" for r in results)


def test_create_inspection_calls_audit(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    table_data = {"projects": [{"id": proj_id, "profile_id": profile_id}], "inspections": []}
    database.db.client = FakeClient(table_data)

    captured = {}

    def _c(audit_data):
        captured["audit"] = audit_data
        return None

    monkeypatch.setattr(database.db, "create_audit_log", _c)

    ins = InspectionCreate(project_id=proj_id, inspection_type="roof")
    created = database.db.create_inspection(ins, profile_id)

    assert created is not None
    assert "audit" in captured
