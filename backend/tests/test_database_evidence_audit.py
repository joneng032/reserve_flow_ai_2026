from backend import database
from backend.tests.conftest import FakeClient, uuid4_str
from backend.models import EvidenceCreate, EvidenceUpdate
import types


def test_create_evidence_creates_audit(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    table_data = {"projects": [{"id": proj_id, "profile_id": profile_id}], "evidence": []}
    database.db.client = FakeClient(table_data)

    cap = {}

    def _cap(a):
        cap["audit"] = a
        return types.SimpleNamespace(id=uuid4_str())

    monkeypatch.setattr(database.db, "create_audit_log", _cap)

    ev = EvidenceCreate(project_id=proj_id, evidence_type="photo")
    created = database.db.create_evidence(ev, profile_id)

    assert created is not None
    assert "audit" in cap


def test_update_evidence_creates_audit(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    ev_id = uuid4_str()
    table_data = {"projects": [{"id": proj_id, "profile_id": profile_id}], "evidence": [{"id": ev_id, "project_id": proj_id}]}
    database.db.client = FakeClient(table_data)

    cap = {}
    def _cap(a):
        cap["audit"] = a
        return types.SimpleNamespace(id=uuid4_str())

    monkeypatch.setattr(database.db, "create_audit_log", _cap)

    upd = EvidenceUpdate(evidence_type="photo")
    res = database.db.update_evidence(ev_id, upd, profile_id)

    assert res is not None
    assert "audit" in cap


def test_delete_evidence_creates_audit(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    ev_id = uuid4_str()
    table_data = {"projects": [{"id": proj_id, "profile_id": profile_id}], "evidence": [{"id": ev_id, "project_id": proj_id}]}
    database.db.client = FakeClient(table_data)

    cap = {}
    def _cap(a):
        cap["audit"] = a
        return types.SimpleNamespace(id=uuid4_str())

    monkeypatch.setattr(database.db, "create_audit_log", _cap)

    ok = database.db.delete_evidence(ev_id, profile_id)
    assert ok is True or ok is not None
    assert "audit" in cap
from backend import database
from backend.tests.conftest import FakeClient, uuid4_str
from backend.models import EvidenceCreate, EvidenceUpdate
import types


def test_create_evidence_creates_audit(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    table_data = {"projects": [{"id": proj_id, "profile_id": profile_id}], "evidence": []}
    database.db.client = FakeClient(table_data)

    cap = {}

    def _cap(a):
        cap["audit"] = a
        return types.SimpleNamespace(id=uuid4_str())

    monkeypatch.setattr(database.db, "create_audit_log", _cap)

    ev = EvidenceCreate(project_id=proj_id, evidence_type="photo")
    created = database.db.create_evidence(ev, profile_id)

    assert created is not None
    assert "audit" in cap


def test_update_evidence_creates_audit(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    ev_id = uuid4_str()
    table_data = {"projects": [{"id": proj_id, "profile_id": profile_id}], "evidence": [{"id": ev_id, "project_id": proj_id}]}
    database.db.client = FakeClient(table_data)

    cap = {}
    def _cap(a):
        cap["audit"] = a
        return types.SimpleNamespace(id=uuid4_str())

    monkeypatch.setattr(database.db, "create_audit_log", _cap)

    upd = EvidenceUpdate(evidence_type="photo")
    res = database.db.update_evidence(ev_id, upd, profile_id)

    assert res is not None
    assert "audit" in cap


def test_delete_evidence_creates_audit(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    ev_id = uuid4_str()
    table_data = {"projects": [{"id": proj_id, "profile_id": profile_id}], "evidence": [{"id": ev_id, "project_id": proj_id}]}
    database.db.client = FakeClient(table_data)

    cap = {}
    def _cap(a):
        cap["audit"] = a
        return types.SimpleNamespace(id=uuid4_str())

    monkeypatch.setattr(database.db, "create_audit_log", _cap)

    ok = database.db.delete_evidence(ev_id, profile_id)
    assert ok is True or ok is not None
    assert "audit" in cap
