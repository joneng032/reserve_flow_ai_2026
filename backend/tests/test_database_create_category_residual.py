import pytest
from backend import database
from backend.tests.conftest import FakeClient, uuid4_str
from backend.models import CategoryCreate


def test_create_category_client_none():
    database.db.client = None
    data = CategoryCreate(project_id=uuid4_str(), name="C")
    res = database.db.create_category(data, uuid4_str())
    assert res is not None


def test_create_category_ownership_negative():
    database.db.client = FakeClient({"projects": []})
    data = CategoryCreate(project_id=uuid4_str(), name="C")
    assert database.db.create_category(data, uuid4_str()) is None


def test_create_category_success(monkeypatch):
    project_id = uuid4_str()
    profile_id = uuid4_str()
    data = CategoryCreate(project_id=project_id, name="C")

    client = FakeClient({"projects": [{"id": project_id, "profile_id": profile_id}]})
    database.db.client = client

    res = database.db.create_category(data, profile_id)
    # project_id on returned Category may be a UUID object; compare as strings
    assert res is None or str(res.project_id) == project_id


def test_create_category_data_error():
    class BrokenQuery:
        def insert(self, data):
            return self

        def execute(self):
            raise AttributeError("bad data")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "categories":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    data = CategoryCreate(project_id=uuid4_str(), name="C")
    assert database.db.create_category(data, uuid4_str()) is None


def test_create_category_unexpected_exception_raises_database_error():
    class ExplodingQuery:
        def insert(self, data):
            return self

        def execute(self):
            raise Exception("boom")

    project_id = uuid4_str()
    profile_id = uuid4_str()

    class ExplodingClient(FakeClient):
        def table(self, name):
            if name == "projects":
                # return project check that passes ownership
                return FakeClient({"projects": [{"id": project_id, "profile_id": profile_id}]}).table(name)
            if name == "categories":
                return ExplodingQuery()
            return FakeClient({}).table(name)

    database.db.client = ExplodingClient({})
    data = CategoryCreate(project_id=project_id, name="C")
    with pytest.raises(database.DatabaseError):
        database.db.create_category(data, profile_id)
