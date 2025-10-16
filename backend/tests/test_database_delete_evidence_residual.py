import pytest
from backend import database
from backend.tests.conftest import FakeClient, uuid4_str


def test_delete_evidence_client_none():
    database.db.client = None
    res = database.db.delete_evidence(uuid4_str(), uuid4_str())
    assert res is False


def test_delete_evidence_ownership_negative():
    database.db.client = FakeClient({"projects": [], "evidence": []})
    res = database.db.delete_evidence(uuid4_str(), uuid4_str())
    assert res is False


def test_delete_evidence_success_and_audit(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    evidence_id = uuid4_str()

    rows = {
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        # include inspection-like nested project info expected by the audit
        "evidence": [{"id": evidence_id, "project_id": proj_id, "file_name": "a.jpg", "projects": {"profile_id": profile_id}}],
    }
    client = FakeClient(rows)
    database.db.client = client

    captured = {}

    def fake_audit(audit):
        captured['audit'] = audit

    monkeypatch.setattr(database.db, "create_audit_log", fake_audit, raising=False)

    res = database.db.delete_evidence(evidence_id, profile_id)
    assert res is True
    assert 'audit' in captured


def test_delete_evidence_data_error():
    class BrokenQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            raise AttributeError("bad data")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "evidence":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    res = database.db.delete_evidence(uuid4_str(), uuid4_str())
    assert res is False


def test_delete_evidence_unexpected_exception_raises_database_error():
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
        database.db.delete_evidence(uuid4_str(), uuid4_str())
