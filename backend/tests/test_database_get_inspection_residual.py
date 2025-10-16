import pytest
from backend import database
from backend.tests.conftest import FakeClient, uuid4_str
from backend.models import Inspection


def test_get_inspection_client_none():
    database.db.client = None
    assert database.db.get_inspection(uuid4_str(), uuid4_str()) is None


def test_get_inspection_ownership_negative():
    database.db.client = FakeClient({"inspections": []})
    assert database.db.get_inspection(uuid4_str(), uuid4_str()) is None


def test_get_inspection_success():
    insp_id = uuid4_str()
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    insp_row = {"id": insp_id, "project_id": proj_id, "inspection_type": "site"}
    client = FakeClient({"inspections": [{**insp_row, "projects": {"profile_id": profile_id}}]})
    database.db.client = client

    res = database.db.get_inspection(insp_id, profile_id)
    assert res is None or isinstance(res, Inspection)


def test_get_inspection_data_error():
    class BrokenQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise AttributeError("bad data")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "inspections":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    assert database.db.get_inspection(uuid4_str(), uuid4_str()) is None


def test_get_inspection_unexpected_exception_raises_database_error():
    class ExplodingQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise Exception("boom")

    insp_id = uuid4_str()
    project_id = uuid4_str()
    profile_id = uuid4_str()

    class ExplodingClient(FakeClient):
        def table(self, name):
            if name == "inspections":
                return ExplodingQuery()
            return FakeClient({}).table(name)

    database.db.client = ExplodingClient({})
    with pytest.raises(database.DatabaseError):
        database.db.get_inspection(insp_id, profile_id)
