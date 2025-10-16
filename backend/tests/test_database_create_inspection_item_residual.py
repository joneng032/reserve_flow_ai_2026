import pytest
from backend import database
from backend.models import InspectionItemCreate
from backend.tests.conftest import FakeClient, uuid4_str


def test_create_inspection_item_client_none():
    # Mock-mode: when no client, database should return an object or None gracefully
    database.db.client = None
    res = database.db.create_inspection_item(InspectionItemCreate(inspection_id=uuid4_str(), item_type="check", item_name="Item"), uuid4_str())
    # Mock implementation returns a simple object or None depending on code; ensure no exception
    assert res is None or hasattr(res, "id")


def test_create_inspection_item_ownership_negative():
    # If project/inspection ownership not verified, should return None
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    client = FakeClient({"projects": [], "inspections": []})
    database.db.client = client

    res = database.db.create_inspection_item(InspectionItemCreate(inspection_id=uuid4_str(), item_type="check", item_name="Item"), profile_id)
    assert res is None


def test_create_inspection_item_success_and_audit(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    insp_id = uuid4_str()

    rows = {"projects": [{"id": proj_id, "profile_id": profile_id}], "inspections": [{"id": insp_id, "project_id": proj_id}], "inspection_items": []}
    client = FakeClient(rows)
    database.db.client = client

    captured = {}

    def fake_create_audit(audit):
        captured['audit'] = audit

    # Patch the instance method on the database.db object for reliability
    monkeypatch.setattr(database.db, "create_audit_log", fake_create_audit, raising=False)

    res = database.db.create_inspection_item(InspectionItemCreate(inspection_id=insp_id, item_type="check", item_name="Item1"), profile_id)
    assert res is not None
    # Audit was created
    assert 'audit' in captured


def test_create_inspection_item_data_error(monkeypatch):
    # Simulate AttributeError during operations -> should return None
    class BrokenQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            raise AttributeError("simulated")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "projects":
                return FakeClient({}).table(name)
            return BrokenQuery()

    database.db.client = BrokenClient({})
    res = database.db.create_inspection_item(InspectionItemCreate(inspection_id=uuid4_str(), item_type="check", item_name="Item"), uuid4_str())
    assert res is None


def test_create_inspection_item_unexpected_exception_raises_database_error():
    # Simulate unexpected Exception from DB client -> DatabaseError
    class ExplodingQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise Exception("boom")

    class ExplodingClient(FakeClient):
        def table(self, name):
            if name == "projects":
                return FakeClient({"projects": [{"id": uuid4_str(), "profile_id": uuid4_str()}]}).table(name)
            return ExplodingQuery()

    database.db.client = ExplodingClient({})
    with pytest.raises(database.DatabaseError):
        database.db.create_inspection_item(InspectionItemCreate(inspection_id=uuid4_str(), item_type="check", item_name="Item"), uuid4_str())
