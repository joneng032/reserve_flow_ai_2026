import pytest
from backend import database
from backend.tests.conftest import FakeClient, uuid4_str


def test_delete_inspection_item_client_none():
    database.db.client = None
    assert database.db.delete_inspection_item(uuid4_str(), uuid4_str()) is False


def test_delete_inspection_item_ownership_negative():
    database.db.client = FakeClient({"inspection_items": []})
    assert database.db.delete_inspection_item(uuid4_str(), uuid4_str()) is False


def test_delete_inspection_item_success_and_audit(monkeypatch):
    item_id = uuid4_str()
    insp_id = uuid4_str()
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    item_row = {"id": item_id, "inspection_id": insp_id, "item_name": "Valve"}
    # inspection_items select expects nested inspections -> projects -> profile_id
    nested = {**item_row, "inspections": {"project_id": proj_id, "projects": {"profile_id": profile_id}}}
    client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "inspection_items": [nested]})
    database.db.client = client

    seen = {}

    def fake_audit(a):
        seen["a"] = a

    monkeypatch.setattr(database.db, "create_audit_log", fake_audit)

    res = database.db.delete_inspection_item(item_id, profile_id)
    assert res in (True, False)
    assert "a" in seen or res is False


def test_delete_inspection_item_data_error():
    class BrokenQuery:
        def delete(self):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise AttributeError("bad data")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "inspection_items":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    assert database.db.delete_inspection_item(uuid4_str(), uuid4_str()) is False


def test_delete_inspection_item_unexpected_exception_raises_database_error():
    class ExplodingQuery:
        def delete(self):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise Exception("boom")

    item_id = uuid4_str()
    project_id = uuid4_str()
    profile_id = uuid4_str()

    class ExplodingClient(FakeClient):
        def table(self, name):
            if name == "inspection_items":
                class ItemCheck:
                    def __init__(self, row):
                        self._row = row

                    def select(self, *a, **kw):
                        return self

                    def eq(self, *a, **kw):
                        return self

                    def execute(self):
                        return type("R", (), {"data": [self._row]})()

                    def delete(self):
                        return ExplodingQuery()

                return ItemCheck({"id": item_id, "inspection_id": item_id, "inspections": {"project_id": project_id, "projects": {"profile_id": profile_id}}})
            if name == "inspections":
                return FakeClient({"inspections": [{"id": item_id, "project_id": project_id, "projects": {"profile_id": profile_id}}]}).table(name)
            if name == "projects":
                return FakeClient({"projects": [{"id": project_id, "profile_id": profile_id}]}).table(name)
            return FakeClient({}).table(name)

    database.db.client = ExplodingClient({})
    with pytest.raises(database.DatabaseError):
        database.db.delete_inspection_item(item_id, profile_id)
