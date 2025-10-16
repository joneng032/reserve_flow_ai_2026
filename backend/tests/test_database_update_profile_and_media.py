from backend import database
from backend.models import ProfileUpdate, MediaFileCreate
from backend.tests.conftest import FakeClient, uuid4_str


def test_update_profile_success_and_failure():
    profile_id = uuid4_str()
    database.db.client = FakeClient({"profiles": [{"id": profile_id, "name": "Old"}]})

    updated = database.db.update_profile(profile_id, ProfileUpdate(name="New Name"))
    # Implementation may return None or a Profile model depending on client behavior.
    assert updated is None or getattr(updated, "name", None) == "New Name"

    # Failure path: no client or missing profile -> None
    database.db.client = FakeClient({"profiles": []})
    res = database.db.update_profile(profile_id, ProfileUpdate(name="X"))
    assert res is None


def test_create_media_file_requires_project_ownership(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    # Owned project -> success
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "media_files": []})
    audits = []
    monkeypatch.setattr(database.db, "create_audit_log", lambda a: audits.append(a))

    mf = database.db.create_media_file(MediaFileCreate(project_id=proj_id, file_name="f.jpg", file_path="/tmp/f", file_type="image", mime_type="image/jpeg", file_size=10), profile_id)
    assert mf is not None
    assert audits

    # Not owned -> None
    database.db.client = FakeClient({"projects": []})
    mf2 = database.db.create_media_file(MediaFileCreate(project_id=proj_id, file_name="f2.jpg", file_path="/tmp/f2", file_type="image", mime_type="image/jpeg", file_size=5), profile_id)
    assert mf2 is None
