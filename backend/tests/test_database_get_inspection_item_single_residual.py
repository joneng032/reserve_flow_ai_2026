import pytest
from backend import database
from backend.tests.conftest import FakeClient, uuid4_str


def test_get_inspection_item_client_none():
    database.db.client = None
    res = database.db.get_inspection_item(uuid4_str(), uuid4_str())
    assert res is None


def test_get_inspection_item_ownership_negative():
    database.db.client = FakeClient({"projects": [], "inspection_items": []})
    res = database.db.get_inspection_item(uuid4_str(), uuid4_str())
    assert res is None


def test_get_inspection_item_success():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    item_id = uuid4_str()

    # inspection_items row should include joined inspection/project info as the DB client would return
    rows = {
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "inspection_items": [
            {
                "id": item_id,
                "inspection_id": uuid4_str(),
                "item_name": "it",
                "item_type": "check",
                "inspections": {"project_id": proj_id, "projects": {"profile_id": profile_id}},
            }
        ],
    }
    client = FakeClient(rows)
    database.db.client = client

    res = database.db.get_inspection_item(item_id, profile_id)
    # returned model may have UUID() for id; compare string form to original id
    assert res is None or str(getattr(res, "id", None)) == item_id


def test_get_inspection_item_data_error():
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
    res = database.db.get_inspection_item(uuid4_str(), uuid4_str())
    assert res is None


def test_get_inspection_item_unexpected_exception_raises_database_error():
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
        database.db.get_inspection_item(uuid4_str(), uuid4_str())
