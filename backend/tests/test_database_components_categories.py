import types

from backend import database
from backend.tests.conftest import FakeClient, uuid4_str
from backend.models import ComponentCreate, ComponentUpdate, CategoryUpdate


def test_create_component_verifies_project_and_creates_audit(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    table_data = {
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "components": [],
    }

    database.db.client = FakeClient(table_data)

    captured = {}

    def _cap(audit_data):
        captured["audit"] = audit_data
        return types.SimpleNamespace(id="a")

    monkeypatch.setattr(database.db, "create_audit_log", _cap)

    comp = ComponentCreate(project_id=proj_id, name="X", category="C")
    created = database.db.create_component(comp, profile_id)

    assert created is not None
    assert "audit" in captured


def test_update_component_requires_ownership_and_creates_audit(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    comp_id = uuid4_str()

    table_data = {
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        # component_check expects components with nested projects link; keep project_id
        "components": [{"id": comp_id, "project_id": proj_id}],
    }

    database.db.client = FakeClient(table_data)

    captured = {}

    def _cap(audit_data):
        captured["audit"] = audit_data
        return None

    monkeypatch.setattr(database.db, "create_audit_log", _cap)

    upd = ComponentUpdate(name="Updated")
    res = database.db.update_component(comp_id, upd, profile_id)

    assert res is not None
    assert "audit" in captured


def test_delete_component_requires_ownership_and_returns_true(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    comp_id = uuid4_str()

    table_data = {
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "components": [{"id": comp_id, "project_id": proj_id, "name": "N"}],
    }

    database.db.client = FakeClient(table_data)

    called = []

    def _cap(audit_data):
        called.append(audit_data)
        return None

    monkeypatch.setattr(database.db, "create_audit_log", _cap)

    ok = database.db.delete_component(comp_id, profile_id)

    assert ok is True
    assert len(called) == 1


def test_update_category_requires_ownership_and_returns_category():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    cat_id = uuid4_str()

    table_data = {
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "categories": [{"id": cat_id, "project_id": proj_id, "name": "old"}],
    }

    database.db.client = FakeClient(table_data)

    upd = CategoryUpdate(name="new", parent_id=None)
    res = database.db.update_category(cat_id, upd, profile_id)

    # FakeClient.update returns merged dict; the db.update_category returns a Category
    assert res is not None
    assert getattr(res, "name", None) == "new"


def test_delete_category_requires_ownership_and_returns_true():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    cat_id = uuid4_str()

    table_data = {
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "categories": [{"id": cat_id, "project_id": proj_id, "name": "old"}],
    }

    database.db.client = FakeClient(table_data)

    ok = database.db.delete_category(cat_id, profile_id)

    assert ok is True
