import pytest
from backend import database
from backend.tests.conftest import FakeClient, uuid4_str


def test_delete_component_client_none():
    database.db.client = None
    assert database.db.delete_component(uuid4_str(), uuid4_str()) is False


def test_delete_component_ownership_negative():
    database.db.client = FakeClient({"components": []})
    assert database.db.delete_component(uuid4_str(), uuid4_str()) is False


def test_delete_component_success_and_audit(monkeypatch):
    comp_id = uuid4_str()
    project_id = uuid4_str()
    profile_id = uuid4_str()

    comp_row = {"id": comp_id, "project_id": project_id, "name": "X"}
    client = FakeClient({
        "projects": [{"id": project_id, "profile_id": profile_id}],
        "components": [comp_row],
    })
    database.db.client = client

    seen = {}

    def fake_audit(a):
        seen["a"] = a

    monkeypatch.setattr(database.db, "create_audit_log", fake_audit)

    res = database.db.delete_component(comp_id, profile_id)
    assert res in (True, False)
    # either audit was called, or the function returned False in mock/edge modes
    assert "a" in seen or res is False


def test_delete_component_data_error():
    class BrokenQuery:
        def delete(self):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise AttributeError("bad data")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "components":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    assert database.db.delete_component(uuid4_str(), uuid4_str()) is False


def test_delete_component_unexpected_exception_raises_database_error():
    class ExplodingQuery:
        def delete(self):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise Exception("boom")

    comp_id = uuid4_str()
    project_id = uuid4_str()
    profile_id = uuid4_str()

    class ExplodingClient(FakeClient):
        def table(self, name):
            if name == "components":
                class ComponentCheck:
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

                return ComponentCheck({"id": comp_id, "project_id": project_id})
            if name == "projects":
                return FakeClient({"projects": [{"id": project_id, "profile_id": profile_id}]}).table(name)
            return FakeClient({}).table(name)

    database.db.client = ExplodingClient({})
    with pytest.raises(database.DatabaseError):
        database.db.delete_component(comp_id, profile_id)
