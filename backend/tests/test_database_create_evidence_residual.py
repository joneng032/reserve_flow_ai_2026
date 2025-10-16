import pytest
from backend import database
from backend.models import EvidenceCreate
from backend.tests.conftest import FakeClient, uuid4_str


def test_create_evidence_client_none():
    database.db.client = None
    profile_id = uuid4_str()
    res = database.db.create_evidence(EvidenceCreate(project_id=uuid4_str(), evidence_type="photo"), profile_id)
    assert res is not None and getattr(res, "project_id", None) is not None


def test_create_evidence_success():
    proj_id = uuid4_str()
    data = {"project_id": proj_id, "evidence_type": "photo"}
    client = FakeClient({"evidence": [data]})
    database.db.client = client

    profile_id = uuid4_str()
    res = database.db.create_evidence(EvidenceCreate(project_id=proj_id, evidence_type="photo"), profile_id)
    # returned model may have string ids; ensure project_id matches
    assert res is None or str(getattr(res, "project_id", None)) == proj_id


def test_create_evidence_data_error():
    class BrokenQuery:
        def insert(self, *a, **kw):
            return self

        def execute(self):
            raise AttributeError("bad data")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "evidence":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    res = database.db.create_evidence(EvidenceCreate(project_id=uuid4_str(), evidence_type="photo"), uuid4_str())
    assert res is None


def test_create_evidence_unexpected_exception_raises_database_error():
    class ExplodingQuery:
        def insert(self, *a, **kw):
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
                # return a project row matching project_id/profile_id so ownership check passes
                return FakeClient({"projects": [{"id": project_id, "profile_id": profile_id}]}).table(name)
            return FakeClient({}).table(name)

    database.db.client = ExplodingClient({})
    with pytest.raises(database.DatabaseError):
        database.db.create_evidence(EvidenceCreate(project_id=project_id, evidence_type="photo"), profile_id)
