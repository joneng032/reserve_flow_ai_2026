from backend.database import Database


def test_update_media_file_creates_audit(monkeypatch):
    from backend.tests.conftest import FakeClient, uuid4_str
    from backend.models import MediaFileUpdate

    pid = uuid4_str()
    mid = uuid4_str()

    client = FakeClient(table_data={
        "projects": [{"id": pid, "profile_id": "profile-1"}],
        "media_files": [{"id": mid, "project_id": pid, "projects": {"profile_id": "profile-1"}, "file_name": "old.jpg"}],
    })

    db = Database()
    db.client = client

    called = {}

    def fake_audit(a):
        called["ok"] = True
        return None

    monkeypatch.setattr(db, "create_audit_log", fake_audit)

    mu = MediaFileUpdate(file_name="new.jpg", file_path="mock/path.jpg", file_type="image", mime_type="image/jpeg", file_size=0)
    updated = db.update_media_file(mid, mu, profile_id="profile-1")
    assert updated is not None
    assert called.get("ok")


def test_delete_media_file_returns_bool(monkeypatch):
    from backend.tests.conftest import FakeClient, uuid4_str

    pid = uuid4_str()
    mid = uuid4_str()

    client = FakeClient(table_data={
        "media_files": [{"id": mid, "project_id": pid, "projects": {"profile_id": "profile-1"}, "file_name": "old.jpg"}],
    })

    db = Database()
    db.client = client

    deleted = db.delete_media_file(mid, "profile-1")
    assert isinstance(deleted, bool)
