import pytest
from backend import database
from backend.tests.conftest import FakeClient, uuid4_str
from backend.models import Evidence


def test_get_project_evidence_client_none():
    database.db.client = None
    res = database.db.get_project_evidence(uuid4_str(), uuid4_str())
    assert isinstance(res, list) and res == []


def test_get_project_evidence_ownership_negative():
    database.db.client = FakeClient({"projects": []})
    res = database.db.get_project_evidence(uuid4_str(), uuid4_str())
    assert res == []


def test_get_project_evidence_success_filters_and_pagination():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    evs = [
        {"id": uuid4_str(), "project_id": proj_id, "evidence_type": "photo"},
        {"id": uuid4_str(), "project_id": proj_id, "evidence_type": "doc"},
    ]
    client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "evidence": evs})
    database.db.client = client

    res_all = database.db.get_project_evidence(proj_id, profile_id)
    assert all(isinstance(x, Evidence) for x in res_all)

    res_filtered = database.db.get_project_evidence(proj_id, profile_id, evidence_type="photo")
    assert all(getattr(x, "evidence_type", None) == "photo" for x in res_filtered)

    res_paginated = database.db.get_project_evidence(proj_id, profile_id, skip=0, limit=1)
    # range() should slice results now; limit=1 should yield at most one item
    assert len(res_paginated) <= 1


def test_get_project_evidence_data_error():
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
            raise AttributeError("bad data")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "evidence":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    res = database.db.get_project_evidence(uuid4_str(), uuid4_str())
    assert res == []


def test_get_project_evidence_unexpected_exception_raises_database_error():
    class ExplodingQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def order(self, *a, **kw):
            return self

        def range(self, *a, **kw):
            return self

        def execute(self):
            raise Exception("boom")

    project_id = uuid4_str()
    profile_id = uuid4_str()

    class ExplodingClient(FakeClient):
        def table(self, name):
            if name == "evidence":
                return ExplodingQuery()
            if name == "projects":
                return FakeClient({"projects": [{"id": project_id, "profile_id": profile_id}]}).table(name)
            return FakeClient({}).table(name)

    database.db.client = ExplodingClient({})
    with pytest.raises(database.DatabaseError):
        database.db.get_project_evidence(project_id, profile_id)
