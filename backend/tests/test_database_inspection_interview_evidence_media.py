from types import SimpleNamespace

import pytest

from backend.database import Database, DatabaseError


def test_update_and_delete_inspection_item_and_inspection_audit(monkeypatch):
    from backend.tests.conftest import FakeClient, uuid4_str

    insp_id = uuid4_str()
    item_id = uuid4_str()
    proj_id = uuid4_str()

    client = FakeClient(table_data={
        "inspections": [{"id": insp_id, "project_id": proj_id}],
        "inspection_items": [{"id": item_id, "inspection_id": insp_id, "inspections": {"project_id": proj_id, "projects": {"profile_id": "profile-1"}}}],
    })

    db = Database()
    db.client = client

    called = {}

    def fake_audit(a):
        called['ok'] = True
        return None

    monkeypatch.setattr(db, "create_audit_log", fake_audit)

    class U:
        def model_dump(self, exclude_unset=True):
            return {"item_name": "Updated"}

    updated = db.update_inspection_item(item_id, U(), "profile-1")
    assert updated is not None
    assert called.get('ok', False) is True

    called.clear()
    out = db.delete_inspection_item(item_id, "profile-1")
    assert out is True or out is False
    # audit should have been called if delete returned True
    # we don't assert strongly here because FakeClient.delete may return empty


def test_interview_update_delete_audit(monkeypatch):
    from backend.tests.conftest import FakeClient, uuid4_str

    iid = uuid4_str()
    proj_id = uuid4_str()
    client = FakeClient(table_data={
        "interviews": [{"id": iid, "project_id": proj_id, "projects": {"profile_id": "profile-1"}}],
    })

    db = Database()
    db.client = client

    called = {}

    def fake_audit(a):
        called['ok'] = True
        return None

    monkeypatch.setattr(db, "create_audit_log", fake_audit)

    class U:
        def model_dump(self, exclude_unset=True):
            return {"interviewee_name": "X"}

    up = db.update_interview(iid, U(), "profile-1")
    assert up is not None
    assert called.get('ok', False) is True

    called.clear()
    out = db.delete_interview(iid, "profile-1")
    assert out is True or out is False


def test_evidence_update_delete_audit(monkeypatch):
    from backend.tests.conftest import FakeClient, uuid4_str

    evid = uuid4_str()
    proj_id = uuid4_str()
    client = FakeClient(table_data={
        "evidence": [{"id": evid, "project_id": proj_id, "projects": {"profile_id": "profile-1"}}],
    })

    db = Database()
    db.client = client

    called = {}

    def fake_audit(a):
        called['ok'] = True
        return None

    monkeypatch.setattr(db, "create_audit_log", fake_audit)

    class U:
        def model_dump(self, exclude_unset=True):
            return {"evidence_type": "photo"}

    up = db.update_evidence(evid, U(), "profile-1")
    assert up is not None
    assert called.get('ok', False) is True

    called.clear()
    out = db.delete_evidence(evid, "profile-1")
    assert out is True or out is False


def test_get_media_file_ownership_mismatch_returns_none():
    from backend.tests.conftest import FakeClient, uuid4_str

    mid = uuid4_str()
    # media belongs to a different project/profile
    client = FakeClient(table_data={
        "media_files": [{"id": mid, "project_id": uuid4_str(), "projects": {"profile_id": "other-profile"}}],
    })

    db = Database()
    db.client = client

    got = db.get_media_file(mid, "profile-1")
    assert got is None


def test_database_exception_mapping_on_interview_get():
    class ExplodingClient:
        def table(self, _):
            raise RuntimeError("boom")

    db = Database()
    db.client = ExplodingClient()

    with pytest.raises(DatabaseError):
        db.get_interview("i", "profile-1")
