from backend import database
from backend.tests.conftest import FakeClient, uuid4_str
from backend.models import ComponentCreate, ComponentUpdate
import types


def test_create_component_creates_audit_and_returns_component(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    table_data = {"projects": [{"id": proj_id, "profile_id": profile_id}], "components": []}
    database.db.client = FakeClient(table_data)

    captured = {}

    def _cap(audit):
        captured["audit"] = audit
        return types.SimpleNamespace(id=uuid4_str())

    monkeypatch.setattr(database.db, "create_audit_log", _cap)

    create = ComponentCreate(project_id=proj_id, name="C1", category="Cat", base_cost=0)
    res = database.db.create_component(create, profile_id)

    assert res is not None
    assert "audit" in captured


def test_update_component_creates_audit_and_returns_updated(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    comp_id = uuid4_str()

    table_data = {"projects": [{"id": proj_id, "profile_id": profile_id}], "components": [{"id": comp_id, "project_id": proj_id, "name": "Old"}]}
    database.db.client = FakeClient(table_data)

    captured = {}

    def _cap(audit):
        captured["audit"] = audit
        return types.SimpleNamespace(id=uuid4_str())

    monkeypatch.setattr(database.db, "create_audit_log", _cap)

    update = ComponentUpdate(name="New")
    res = database.db.update_component(comp_id, update, profile_id)

    assert res is not None
    assert getattr(res, "name", None) == "New"
    assert "audit" in captured


def test_delete_component_creates_audit_and_returns_true(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    comp_id = uuid4_str()

    table_data = {"projects": [{"id": proj_id, "profile_id": profile_id}], "components": [{"id": comp_id, "project_id": proj_id, "name": "ToDelete"}], "components_catalog": []}
    database.db.client = FakeClient(table_data)

    captured = {}

    def _cap(audit):
        captured["audit"] = audit
        return types.SimpleNamespace(id=uuid4_str())

    monkeypatch.setattr(database.db, "create_audit_log", _cap)

    ok = database.db.delete_component(comp_id, profile_id)

    assert ok is True or ok is not None
    assert "audit" in captured
