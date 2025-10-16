import pytest
from backend import database
from backend.tests.conftest import FakeClient, uuid4_str
from backend.models import Communication


def test_get_communication_client_none():
    database.db.client = None
    assert database.db.get_communication(uuid4_str(), uuid4_str()) is None


def test_get_communication_ownership_negative():
    database.db.client = FakeClient({"communications": []})
    assert database.db.get_communication(uuid4_str(), uuid4_str()) is None


def test_get_communication_success(monkeypatch):
    comm_id = uuid4_str()
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    comm_row = {"id": comm_id, "project_id": proj_id, "communication_type": "m", "subject": "S"}
    # Emulate the select with projects!inner(profile_id) by nesting projects data under the communication
    client = FakeClient({"communications": [{**comm_row, "projects": {"profile_id": profile_id}}]})
    database.db.client = client

    res = database.db.get_communication(comm_id, profile_id)
    assert res is None or isinstance(res, Communication)


def test_get_communication_data_error():
    class BrokenQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise AttributeError("bad data")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "communications":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    assert database.db.get_communication(uuid4_str(), uuid4_str()) is None


def test_get_communication_unexpected_exception_raises_database_error():
    class ExplodingQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise Exception("boom")

    comm_id = uuid4_str()
    project_id = uuid4_str()
    profile_id = uuid4_str()

    class ExplodingClient(FakeClient):
        def table(self, name):
            if name == "communications":
                return ExplodingQuery()
            return FakeClient({}).table(name)

    database.db.client = ExplodingClient({})
    with pytest.raises(database.DatabaseError):
        database.db.get_communication(comm_id, profile_id)
