import pytest
from backend import database
from backend.tests.conftest import FakeClient, uuid4_str


def test_get_project_evidence_client_none_returns_empty():
    database.db.client = None
    assert database.db.get_project_evidence(uuid4_str(), uuid4_str()) == []


def test_get_project_evidence_project_check_no_data_returns_empty():
    # projects table missing the project -> ownership check fails
    client = FakeClient({"projects": [], "evidence": [{"id": "e1", "project_id": "p1"}]})
    database.db.client = client
    assert database.db.get_project_evidence("p1", "u1") == []


def test_get_project_evidence_execute_raises_valueerror_returns_empty():
    class BrokenQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def order(self, *a, **kw):
            return self

        def range(self, *a, **kw):
            return self

        def execute(self):
            raise ValueError("bad value")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "projects":
                return FakeClient({"projects": [{"id": "p1", "profile_id": "u1"}]}).table(name)
            if name == "evidence":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    assert database.db.get_project_evidence("p1", "u1") == []


def test_get_evidence_client_none_returns_none():
    database.db.client = None
    assert database.db.get_evidence(uuid4_str(), uuid4_str()) is None


def test_get_evidence_execute_raises_valueerror_returns_none():
    class BrokenQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise ValueError("bad value")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "evidence":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    assert database.db.get_evidence(uuid4_str(), uuid4_str()) is None


def test_get_evidence_no_data_returns_none():
    database.db.client = FakeClient({"evidence": []})
    assert database.db.get_evidence("nope", "u1") is None
