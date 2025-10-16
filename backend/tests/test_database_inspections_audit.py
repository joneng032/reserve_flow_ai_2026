from backend import database
from backend.tests.conftest import FakeClient, uuid4_str
from backend.models import InspectionCreate, InspectionUpdate
import types


def test_create_inspection_creates_audit(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    table_data = {"projects": [{"id": proj_id, "profile_id": profile_id}], "inspections": []}
    database.db.client = FakeClient(table_data)

    cap = {}

    def _cap(a):
        cap["audit"] = a
        return types.SimpleNamespace(id=uuid4_str())

    monkeypatch.setattr(database.db, "create_audit_log", _cap)

    ins = InspectionCreate(project_id=proj_id, inspection_type="roof")
    created = database.db.create_inspection(ins, profile_id)

    assert created is not None
    assert "audit" in cap


def test_update_inspection_creates_audit(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    insp_id = uuid4_str()
    table_data = {"projects": [{"id": proj_id, "profile_id": profile_id}], "inspections": [{"id": insp_id, "project_id": proj_id}]}
    database.db.client = FakeClient(table_data)

    cap = {}

    def _cap(a):
        cap["audit"] = a
        return types.SimpleNamespace(id=uuid4_str())

    monkeypatch.setattr(database.db, "create_audit_log", _cap)

    upd = InspectionUpdate(inspection_type="deck")
    res = database.db.update_inspection(insp_id, upd, profile_id)

    assert res is not None
    assert "audit" in cap


def test_delete_inspection_creates_audit(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    insp_id = uuid4_str()

    table_data = {"projects": [{"id": proj_id, "profile_id": profile_id}], "inspections": [{"id": insp_id, "project_id": proj_id}], "inspection_items": []}
    database.db.client = FakeClient(table_data)

    cap = {}

    def _cap(a):
        cap["audit"] = a
        return types.SimpleNamespace(id=uuid4_str())

    monkeypatch.setattr(database.db, "create_audit_log", _cap)

    ok = database.db.delete_inspection(insp_id, profile_id)
    assert ok is True or ok is not None
    assert "audit" in cap
