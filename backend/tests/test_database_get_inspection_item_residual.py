import pytest
from backend import database
from backend.tests.conftest import FakeClient, uuid4_str


def test_get_inspection_item_client_none():
    database.db.client = None
    res = database.db.get_inspection_items(uuid4_str(), uuid4_str())
    assert isinstance(res, list)


def test_get_inspection_item_ownership_negative():
    database.db.client = FakeClient({"projects": [], "inspections": []})
    res = database.db.get_inspection_items(uuid4_str(), uuid4_str())
    assert res == []


def test_get_inspection_item_returns_items():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    insp_id = uuid4_str()

    rows = {
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "inspections": [{"id": insp_id, "project_id": proj_id}],
        "inspection_items": [{"id": uuid4_str(), "inspection_id": insp_id, "item_type": "check", "item_name": "It"}],
    }
    client = FakeClient(rows)
    database.db.client = client

    res = database.db.get_inspection_items(insp_id, profile_id)
    assert isinstance(res, list)


def test_get_inspection_item_filter_and_pagination():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    insp_id = uuid4_str()

    items = []
    for i in range(10):
        items.append({"id": uuid4_str(), "inspection_id": insp_id, "item_type": "check" if i % 2 == 0 else "measure", "item_name": f"it{i}", "created_at": f"2024-01-0{i+1}T00:00:00Z"})

    rows = {"projects": [{"id": proj_id, "profile_id": profile_id}], "inspections": [{"id": insp_id, "project_id": proj_id}], "inspection_items": items}
    client = FakeClient(rows)
    database.db.client = client

    # filter by item_type
    res_filtered = database.db.get_inspection_items(insp_id, profile_id, item_type="check")
    assert all(getattr(r, "item_type", None) == "check" for r in res_filtered)

    # pagination: skip 2, limit 3
    res_paginated = database.db.get_inspection_items(insp_id, profile_id, skip=2, limit=3)
    assert isinstance(res_paginated, list) and len(res_paginated) <= 3


def test_get_inspection_item_empty_response():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    insp_id = uuid4_str()
    client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "inspections": [{"id": insp_id, "project_id": proj_id}], "inspection_items": []})
    database.db.client = client
    res = database.db.get_inspection_items(insp_id, profile_id)
    assert res == []


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
    res = database.db.get_inspection_items(uuid4_str(), uuid4_str())
    assert res == []


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
        database.db.get_inspection_items(uuid4_str(), uuid4_str())
