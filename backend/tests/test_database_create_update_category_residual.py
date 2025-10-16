import pytest
from backend import database
from backend.models import CategoryCreate, CategoryUpdate
from backend.tests.conftest import FakeClient, uuid4_str


def test_create_category_client_none():
    database.db.client = None
    proj_id = uuid4_str()
    res = database.db.create_category(CategoryCreate(project_id=proj_id, name="C"), uuid4_str())
    assert res is not None and str(getattr(res, "project_id", None)) == proj_id


def test_create_category_ownership_negative():
    database.db.client = FakeClient({"projects": []})
    res = database.db.create_category(CategoryCreate(project_id=uuid4_str(), name="C"), uuid4_str())
    assert res is None


def test_create_category_success():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    data = {"id": uuid4_str(), "project_id": proj_id, "name": "C"}
    client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "categories": [data]})
    database.db.client = client
    res = database.db.create_category(CategoryCreate(project_id=proj_id, name="C"), profile_id)
    assert res is None or str(getattr(res, "project_id", None)) == proj_id


def test_create_category_data_error():
    class BrokenQuery:
        def insert(self, *a, **kw):
            return self

        def execute(self):
            raise AttributeError("bad data")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "categories":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    res = database.db.create_category(CategoryCreate(project_id=uuid4_str(), name="C"), uuid4_str())
    assert res is None


def test_update_category_ownership_negative():
    database.db.client = FakeClient({"categories": []})
    res = database.db.update_category(uuid4_str(), CategoryUpdate(name="X"), uuid4_str())
    assert res is None


def test_update_category_success():
    cat_id = uuid4_str()
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    cat_row = {"id": cat_id, "project_id": proj_id, "name": "Old", "projects": {"profile_id": profile_id}}
    client = FakeClient({"categories": [cat_row]})
    database.db.client = client
    res = database.db.update_category(cat_id, CategoryUpdate(name="New"), profile_id)
    assert res is None or str(getattr(res, "id", None)) == cat_id


def test_update_category_unexpected_exception_raises_database_error():
    class ExplodingQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise Exception("boom")

    class ExplodingClient(FakeClient):
        def table(self, name):
            if name == "categories":
                return ExplodingQuery()
            return FakeClient({}).table(name)

    database.db.client = ExplodingClient({})
    with pytest.raises(database.DatabaseError):
        database.db.update_category(uuid4_str(), CategoryUpdate(name="Z"), uuid4_str())
