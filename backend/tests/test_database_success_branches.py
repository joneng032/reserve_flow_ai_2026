"""Focused tests for success branches of several database methods.

Uses FakeClient from conftest to simulate DB responses.
"""
from types import SimpleNamespace

import pytest

from backend.database import Database


def test_get_project_audit_logs_success(monkeypatch):
    from backend.tests.conftest import FakeClient, uuid4_str

    # Fake project check + one audit log row
    proj_id = uuid4_str()
    audit_row = {"id": uuid4_str(), "project_id": proj_id, "entity_type": "component", "entity_id": uuid4_str(), "action": "create", "details": {}}
    client = FakeClient(table_data={
        "projects": [{"id": proj_id, "profile_id": "profile-1"}],
        "audit_logs": [audit_row],
    })

    db = Database()
    db.client = client

    logs = db.get_project_audit_logs(proj_id, "profile-1")
    assert isinstance(logs, list)
    assert len(logs) == 1
    assert getattr(logs[0], "entity_type", None) == "component"


def test_update_media_file_creates_audit_log(monkeypatch):
    from backend.tests.conftest import FakeClient, uuid4_str

    mf_id = uuid4_str()
    proj_id = uuid4_str()
    # media_files table has an existing row for ownership check
    client = FakeClient(table_data={
        "media_files": [{"id": mf_id, "project_id": proj_id, "file_name": "orig.jpg"}],
        "projects": [{"id": proj_id, "profile_id": "profile-1"}],
    })

    db = Database()
    db.client = client

    created_audit = {}

    def fake_create_audit(audit_data):
        created_audit["called"] = True
        created_audit["details"] = getattr(audit_data, "details", None)
        return SimpleNamespace(id=uuid4_str())

    monkeypatch.setattr(db, "create_audit_log", fake_create_audit)

    class Upd:
        def model_dump(self, exclude_unset=True):
            return {"file_name": "new.jpg"}
    res = db.update_media_file(mf_id, Upd(), "profile-1")
    assert res is not None
    assert created_audit.get("called", False) is True


def test_delete_media_file_creates_audit_log(monkeypatch):
    from backend.tests.conftest import FakeClient, uuid4_str

    mf_id = uuid4_str()
    proj_id = uuid4_str()
    # media_files ownership check returns a row with project_id
    client = FakeClient(table_data={
        "media_files": [{"id": mf_id, "project_id": proj_id, "file_name": "todel.jpg"}],
        "projects": [{"id": proj_id, "profile_id": "profile-1"}],
    })

    db = Database()
    db.client = client

    called = {}

    def fake_create_audit(audit_data):
        called["ok"] = True
        return SimpleNamespace(id=uuid4_str())

    monkeypatch.setattr(db, "create_audit_log", fake_create_audit)

    out = db.delete_media_file(mf_id, "profile-1")
    assert out is True
    assert called.get("ok", False) is True


def test_interview_update_get_delete_success(monkeypatch):
    from backend.tests.conftest import FakeClient, uuid4_str

    iid = uuid4_str()
    proj_id = uuid4_str()
    client = FakeClient(table_data={
        "projects": [{"id": proj_id, "profile_id": "profile-1"}],
        "interviews": [{"id": iid, "project_id": proj_id, "interviewee_name": "Z"}],
    })

    db = Database()
    db.client = client

    class U:
        def model_dump(self, exclude_unset=True):
            return {"interviewee_name": "Z2"}

    updated = db.update_interview(iid, U(), "profile-1")
    # FakeClient.update returns the data dict; update_interview wraps into Interview
    assert updated is not None

    items = db.get_project_interviews(proj_id, "profile-1")
    assert isinstance(items, list)

    # For delete, FakeQuery.delete returns the underlying _data; ensure deletion path returns True
    out = db.delete_interview(iid, "profile-1")
    assert out is True


def test_inspection_item_and_evidence_create_get(monkeypatch):
    from backend.tests.conftest import FakeClient, uuid4_str

    insp_id = uuid4_str()
    proj_id = uuid4_str()
    client = FakeClient(table_data={
        "projects": [{"id": proj_id, "profile_id": "profile-1"}],
        "inspections": [{"id": insp_id, "project_id": proj_id}],
        "inspection_items": [{"id": uuid4_str(), "inspection_id": insp_id, "item_name": "i1"}],
        "evidence": [{"id": uuid4_str(), "project_id": proj_id, "evidence_type": "photo"}],
    })

    db = Database()
    db.client = client

    class It:
        # create_inspection_item expects inspection_item_data.inspection_id attribute
        def __init__(self):
            self.inspection_id = insp_id

        def model_dump(self, exclude_unset=True):
            return {"inspection_id": insp_id, "item_name": "new"}

    class Ev:
        def __init__(self):
            self.project_id = proj_id

        def model_dump(self):
            return {"project_id": proj_id, "evidence_type": "photo"}

    item = db.create_inspection_item(It(), "profile-1")
    assert item is not None

    items = db.get_inspection_items(insp_id, "profile-1")
    assert isinstance(items, list)

    ev = db.create_evidence(Ev(), "profile-1")
    assert ev is not None
