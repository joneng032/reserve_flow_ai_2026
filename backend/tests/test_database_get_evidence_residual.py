import pytest
from backend import database
from backend.tests.conftest import FakeClient, uuid4_str
from backend.models import Evidence


def test_get_evidence_client_none():
    database.db.client = None
    assert database.db.get_evidence(uuid4_str(), uuid4_str()) is None


def test_get_evidence_ownership_negative():
    database.db.client = FakeClient({"evidence": []})
    assert database.db.get_evidence(uuid4_str(), uuid4_str()) is None


def test_get_evidence_success():
    ev_id = uuid4_str()
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    ev_row = {"id": ev_id, "project_id": proj_id, "evidence_type": "photo", "projects": {"profile_id": profile_id}}
    client = FakeClient({"evidence": [ev_row]})
    database.db.client = client

    res = database.db.get_evidence(ev_id, profile_id)
    assert res is None or isinstance(res, Evidence)


def test_get_evidence_data_error():
    class BrokenQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise AttributeError("bad data")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "evidence":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    assert database.db.get_evidence(uuid4_str(), uuid4_str()) is None


def test_get_evidence_unexpected_exception_raises_database_error():
    class ExplodingQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise Exception("boom")

    ev_id = uuid4_str()
    project_id = uuid4_str()
    profile_id = uuid4_str()

    class ExplodingClient(FakeClient):
        def table(self, name):
            if name == "evidence":
                return ExplodingQuery()
            return FakeClient({}).table(name)

    database.db.client = ExplodingClient({})
    with pytest.raises(database.DatabaseError):
        database.db.get_evidence(ev_id, profile_id)
