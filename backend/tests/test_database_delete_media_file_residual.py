import pytest
from backend import database
from backend.tests.conftest import FakeClient, uuid4_str


def test_delete_media_file_client_none():
    database.db.client = None
    assert database.db.delete_media_file(uuid4_str(), uuid4_str()) is False


def test_delete_media_file_ownership_negative():
    database.db.client = FakeClient({"media_files": []})
    assert database.db.delete_media_file(uuid4_str(), uuid4_str()) is False


def test_delete_media_file_success_and_audit(monkeypatch):
    mf_id = uuid4_str()
    project_id = uuid4_str()
    profile_id = uuid4_str()

    # media_files row includes joined projects.profile_id via FakeClient emulation
    mf_row = {"id": mf_id, "project_id": project_id, "file_name": "f.jpg", "projects": {"profile_id": profile_id}}
    client = FakeClient({"media_files": [mf_row]})
    database.db.client = client

    seen = {}

    def fake_audit(a):
        seen["a"] = a

    monkeypatch.setattr(database.db, "create_audit_log", fake_audit)

    res = database.db.delete_media_file(mf_id, profile_id)
    assert res is True
    assert "a" in seen


def test_delete_media_file_data_error():
    class BrokenQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            raise AttributeError("bad data")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "media_files":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    assert database.db.delete_media_file(uuid4_str(), uuid4_str()) is False


def test_delete_media_file_unexpected_exception_raises_database_error():
    class ExplodingQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise Exception("boom")

    class ExplodingClient(FakeClient):
        def table(self, name):
            if name == "media_files":
                return ExplodingQuery()
            return FakeClient({}).table(name)

    database.db.client = ExplodingClient({})
    with pytest.raises(database.DatabaseError):
        database.db.delete_media_file(uuid4_str(), uuid4_str())
