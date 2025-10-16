from backend.database import Database


def test_create_component_success_and_audit(monkeypatch):
    from backend.tests.conftest import FakeClient, uuid4_str
    from backend.models import ComponentCreate

    pid = uuid4_str()
    cid = uuid4_str()

    client = FakeClient(table_data={
        "projects": [{"id": pid, "profile_id": "profile-1"}],
        "components": [],
    })

    db = Database()
    db.client = client

    called = {}

    def fake_audit(a):
        called['ok'] = True
        return None

    monkeypatch.setattr(db, "create_audit_log", fake_audit)

    comp_in = ComponentCreate(project_id=pid, name="Pump", base_cost=100)
    created = db.create_component(comp_in, profile_id="profile-1")
    assert created is not None
    assert called.get('ok')


def test_update_component_success_and_audit(monkeypatch):
    from backend.tests.conftest import FakeClient, uuid4_str
    from backend.models import ComponentUpdate

    pid = uuid4_str()
    comp_id = uuid4_str()

    client = FakeClient(table_data={
        "components": [{"id": comp_id, "project_id": pid, "projects": {"profile_id": "profile-1"}, "name": "Old"}],
    })

    db = Database()
    db.client = client

    called = {}

    def fake_audit(a):
        called['ok'] = True
        return None

    monkeypatch.setattr(db, "create_audit_log", fake_audit)

    upd = ComponentUpdate(name="Updated Pump", base_cost=150)
    res = db.update_component(comp_id, upd, profile_id="profile-1")
    assert res is not None
    assert getattr(res, "name", "") == "Updated Pump"
    assert called.get('ok')


def test_delete_component_success_and_audit(monkeypatch):
    from backend.tests.conftest import FakeClient, uuid4_str

    pid = uuid4_str()
    comp_id = uuid4_str()

    client = FakeClient(table_data={
        "components": [{"id": comp_id, "project_id": pid, "projects": {"profile_id": "profile-1"}, "name": "ToDelete"}],
    })

    db = Database()
    db.client = client

    called = {}

    def fake_audit(a):
        called['ok'] = True
        return None

    monkeypatch.setattr(db, "create_audit_log", fake_audit)

    ok = db.delete_component(comp_id, profile_id="profile-1")
    assert ok is True
    assert called.get('ok')
"""Tests for component-related methods in backend.database.

Pattern: mock-mode, fake client success response, client exception mapping,
and data-shape error handling where applicable.
"""
import pytest

from backend.database import Database, DatabaseError


def test_create_component_mock_mode_returns_component():
    db = Database()
    db.client = None

    class C:
        def __init__(self):
            self.project_id = "550e8400-e29b-41d4-a716-446655440100"
            self.name = "Comp"
            self.category = None
            self.base_cost = None
            self.useful_life = None
            self.custom_fields = {}

    comp = db.create_component(C(), "profile-1")
    assert comp is not None
    assert comp.name == "Comp"


def test_get_project_components_mock_mode_returns_list():
    db = Database()
    db.client = None

    comps = db.get_project_components("pid", "profile-1")
    assert isinstance(comps, list)


def test_update_component_mock_mode_returns_namespace():
    db = Database()
    db.client = None

    class U:
        def model_dump(self, exclude_unset=True):
            return {"name": "NewComp", "project_id": "550e8400-e29b-41d4-a716-446655440111"}

    # Use UUID-like strings for ids so Pydantic validation succeeds
    res = db.update_component(
        "550e8400-e29b-41d4-a716-446655440110", U(), "profile-1"
    )
    assert res is not None
    assert getattr(res, "name", None) == "NewComp"


def test_delete_component_mock_mode_returns_bool():
    db = Database()
    db.client = None

    out = db.delete_component("cid", "profile-1")
    assert out is False or out is True


def test_get_project_components_client_exception_maps_to_database_error():
    class ExplodingClient:
        def table(self, _):
            raise RuntimeError("boom")

    db = Database()
    db.client = ExplodingClient()

    with pytest.raises(DatabaseError):
        db.get_project_components("p", "profile-1")
