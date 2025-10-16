from backend import database
from backend.tests.conftest import FakeClient, uuid4_str
from backend.models import MediaFileUpdate
import types


def test_get_project_media_files_filters_and_returns_rows():
    proj_id = uuid4_str()
    mf1 = {"id": uuid4_str(), "project_id": proj_id, "file_type": "image", "file_name": "a.jpg"}
    mf2 = {"id": uuid4_str(), "project_id": proj_id, "file_type": "doc", "file_name": "b.doc"}

    profile_id = uuid4_str()
    database.db.client = FakeClient({"media_files": [mf1, mf2], "projects": [{"id": proj_id, "profile_id": profile_id}]})

    rows = database.db.get_project_media_files(proj_id, profile_id=profile_id, file_type="image")

    assert isinstance(rows, list)
    assert any(str(getattr(r, "id", None)) == mf1["id"] for r in rows)
    # ensure filter worked
    assert all(getattr(r, "file_type", None) == "image" for r in rows)


def test_get_media_file_returns_media_when_exists():
    proj_id = uuid4_str()
    mf = {"id": uuid4_str(), "project_id": proj_id, "file_type": "image", "file_name": "img.jpg"}
    profile_id = uuid4_str()
    database.db.client = FakeClient({"media_files": [mf], "projects": [{"id": proj_id, "profile_id": profile_id}]})

    got = database.db.get_media_file(mf["id"], profile_id=profile_id)

    assert got is not None
    assert str(getattr(got, "id", None)) == mf["id"]


def test_update_media_file_creates_audit_and_returns_updated(monkeypatch):
    proj_id = uuid4_str()
    mf_id = uuid4_str()
    mf = {"id": mf_id, "project_id": proj_id, "file_type": "image", "file_name": "old.jpg", "file_path": "p.jpg", "mime_type": "image/jpeg", "file_size": 10}
    profile_id = uuid4_str()
    database.db.client = FakeClient({"media_files": [mf], "projects": [{"id": proj_id, "profile_id": profile_id}]})
    captured = {}

    def _cap(audit):
        captured["audit"] = audit
        return types.SimpleNamespace(id=uuid4_str())

    monkeypatch.setattr(database.db, "create_audit_log", _cap)

    mf_update = MediaFileUpdate(file_name="new.jpg", file_path="new.jpg", file_type="image", mime_type="image/jpeg", file_size=10)
    updated = database.db.update_media_file(mf_id, mf_update, profile_id=profile_id)

    assert updated is not None
    # updated is a MediaFile model; check attribute
    assert getattr(updated, "file_path", None) == "new.jpg"
    assert "audit" in captured


def test_delete_media_file_creates_audit_and_returns_true(monkeypatch):
    proj_id = uuid4_str()
    mf_id = uuid4_str()
    mf = {"id": mf_id, "project_id": proj_id}
    profile_id = uuid4_str()
    database.db.client = FakeClient({"media_files": [mf], "projects": [{"id": proj_id, "profile_id": profile_id}]})
    captured = {}

    def _cap(audit):
        captured["audit"] = audit
        return types.SimpleNamespace(id=uuid4_str())

    monkeypatch.setattr(database.db, "create_audit_log", _cap)

    ok = database.db.delete_media_file(mf_id, profile_id=profile_id)

    assert ok is True
    assert "audit" in captured
