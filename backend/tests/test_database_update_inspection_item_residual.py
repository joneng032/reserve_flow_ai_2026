import pytest
from backend import database
from backend.models import InspectionItemUpdate
from backend.tests.conftest import FakeClient, uuid4_str


def test_update_inspection_item_client_none(monkeypatch):
    class DummyItem:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    monkeypatch.setattr(database, "InspectionItem", DummyItem, raising=False)

    database.db.client = None
    res = database.db.update_inspection_item(
        uuid4_str(),
        InspectionItemUpdate(item_name="x", item_type="measurement"),
        uuid4_str(),
    )
    assert res is None or hasattr(res, "id")


def test_update_inspection_item_ownership_negative():
    database.db.client = FakeClient({"projects": [], "inspection_items": []})
    res = database.db.update_inspection_item(
        uuid4_str(),
        InspectionItemUpdate(item_name="x", item_type="measurement"),
        uuid4_str(),
    )
    assert res is None


def test_update_inspection_item_success_and_audit(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    item_id = uuid4_str()
    insp_id = uuid4_str()

    rows = {
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "inspection_items": [
            {
                "id": item_id,
                "inspection_id": insp_id,
                "item_name": "old",
                "item_type": "check",
                # Emulate joined inspection data returned by the DB client
                "inspections": {"project_id": proj_id, "projects": {"profile_id": profile_id}},
            }
        ],
        "inspections": [{"id": insp_id, "project_id": proj_id}],
    }
    client = FakeClient(rows)
    database.db.client = client

    captured = {}

    def fake_audit(audit):
        captured['audit'] = audit

    monkeypatch.setattr(database.db, "create_audit_log", fake_audit, raising=False)

    res = database.db.update_inspection_item(
        item_id,
        InspectionItemUpdate(item_name="new", item_type="measurement"),
        profile_id,
    )
    assert res is not None
    assert 'audit' in captured


def test_update_inspection_item_data_error():
    class BrokenQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            raise AttributeError("bad data")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "inspection_items":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    res = database.db.update_inspection_item(
        uuid4_str(),
        InspectionItemUpdate(item_name="x", item_type="measurement"),
        uuid4_str(),
    )
    assert res is None


def test_update_inspection_item_unexpected_exception_raises_database_error():
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
        database.db.update_inspection_item(
            uuid4_str(),
            InspectionItemUpdate(item_name="x", item_type="measurement"),
            uuid4_str(),
        )
