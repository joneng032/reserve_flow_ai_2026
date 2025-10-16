import pytest
from backend import database
from backend.tests.conftest import FakeClient, uuid4_str


def test_get_project_client_none():
    database.db.client = None
    assert database.db.get_project(uuid4_str(), uuid4_str()) is None


def test_get_project_ownership_negative():
    database.db.client = FakeClient({"projects": []})
    assert database.db.get_project(uuid4_str(), uuid4_str()) is None


def test_get_project_success_counts_and_total():
    project_id = uuid4_str()
    profile_id = uuid4_str()

    proj_row = {
        "id": project_id,
        "profile_id": profile_id,
        "name": "P",
        "categories": [{"id": uuid4_str(), "name": "C", "project_id": project_id}],
        "components": [
            {"id": uuid4_str(), "base_cost": 10},
            {"id": uuid4_str(), "base_cost": 15.5},
        ],
    }

    client = FakeClient({"projects": [proj_row]})
    database.db.client = client

    res = database.db.get_project(project_id, profile_id)
    assert res is not None
    assert getattr(res, "components_count", None) == 2
    assert getattr(res, "total_value", None) == pytest.approx(25.5)


def test_get_project_data_error():
    class BrokenQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            raise AttributeError("bad data")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "projects":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    assert database.db.get_project(uuid4_str(), uuid4_str()) is None


def test_get_project_unexpected_exception_raises_database_error():
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
                return ExplodingQuery()
            return FakeClient({}).table(name)

    database.db.client = ExplodingClient({})
    with pytest.raises(database.DatabaseError):
        database.db.get_project(uuid4_str(), uuid4_str())
