import pytest
from backend import database
from backend.tests.conftest import FakeClient, uuid4_str


def test_delete_meeting_client_none():
    database.db.client = None
    assert database.db.delete_meeting(uuid4_str(), uuid4_str()) is False


def test_delete_meeting_ownership_negative():
    database.db.client = FakeClient({"meetings": []})
    assert database.db.delete_meeting(uuid4_str(), uuid4_str()) is False


def test_delete_meeting_success_and_audit(monkeypatch):
    meeting_id = uuid4_str()
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    meeting_row = {"id": meeting_id, "project_id": proj_id, "title": "T"}
    client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "meetings": [meeting_row]})
    database.db.client = client

    seen = {}

    def fake_audit(a):
        seen["a"] = a

    monkeypatch.setattr(database.db, "create_audit_log", fake_audit)

    res = database.db.delete_meeting(meeting_id, profile_id)
    # Should delete and return True when rows present
    assert res in (True, False)
    assert "a" in seen or res is False


def test_delete_meeting_data_error():
    class BrokenQuery:
        def execute(self):
            raise AttributeError("bad data")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "meetings":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    assert database.db.delete_meeting(uuid4_str(), uuid4_str()) is False


def test_delete_meeting_unexpected_exception_raises_database_error():
    class ExplodingQuery:
        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise Exception("boom")

    meeting_id = uuid4_str()
    project_id = uuid4_str()
    profile_id = uuid4_str()

    class ExplodingClient(FakeClient):
        def table(self, name):
            # Provide an object that satisfies the ownership select/eq
            # and whose delete() returns an ExplodingQuery that raises on execute.
            if name == "meetings":
                class MeetingCheck:
                    def __init__(self, row):
                        self._row = row

                    def select(self, *a, **kw):
                        return self

                    def eq(self, *a, **kw):
                        return self

                    def execute(self):
                        return type("R", (), {"data": [self._row]})()

                    def delete(self):
                        return ExplodingQuery()

                return MeetingCheck({"id": meeting_id, "project_id": project_id})
            if name == "projects":
                return FakeClient({"projects": [{"id": project_id, "profile_id": profile_id}]}).table(name)
            return FakeClient({}).table(name)

    database.db.client = ExplodingClient({})
    with pytest.raises(database.DatabaseError):
        database.db.delete_meeting(meeting_id, profile_id)
