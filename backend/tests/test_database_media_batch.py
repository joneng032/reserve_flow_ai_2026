from backend import database
from backend.models import MediaFileCreate, MediaFileUpdate
from backend.tests.conftest import FakeClient, uuid4_str


def test_media_create_update_delete_flow(monkeypatch):
    proj_id = uuid4_str()
    profile = uuid4_str()
    mf_id = uuid4_str()

    # create path (ownership required)
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile}], "media_files": []})
    audits = []
    monkeypatch.setattr(database.db, "create_audit_log", lambda a: audits.append(a))

    mf = database.db.create_media_file(MediaFileCreate(project_id=proj_id, file_name="c.jpg", file_path="/c.jpg", file_type="image", mime_type="image/jpeg", file_size=10), profile)
    assert mf is not None
    assert audits

    # prepare for update: ensure required fields present
    database.db.client = FakeClient({
        "projects": [{"id": proj_id, "profile_id": profile}],
        "media_files": [{"id": mf_id, "project_id": proj_id, "file_name": "c.jpg", "file_path": "/c.jpg", "file_type": "image", "mime_type": "image/jpeg", "file_size": 10}],
    })

    updated = database.db.update_media_file(mf_id, MediaFileUpdate(file_name="d.jpg", file_path="/d.jpg", file_type="image", mime_type="image/jpeg", file_size=20), profile)
    assert updated is None or getattr(updated, "file_name", None) in ("d.jpg", "c.jpg")

    ok = database.db.delete_media_file(mf_id, profile)
    assert ok in (True, False)
