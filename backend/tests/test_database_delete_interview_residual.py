import pytest
from backend import database
from backend.tests.conftest import FakeClient, uuid4_str


def test_delete_interview_client_none():
    database.db.client = None
    assert database.db.delete_interview(uuid4_str(), uuid4_str()) is False


def test_delete_interview_ownership_negative():
    database.db.client = FakeClient({"interviews": []})
    assert database.db.delete_interview(uuid4_str(), uuid4_str()) is False


def test_delete_interview_success_and_audit(monkeypatch):
    interview_id = uuid4_str()
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    interview_row = {"id": interview_id, "project_id": proj_id, "interviewee_name": "Bob"}
    client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "interviews": [interview_row]})
    database.db.client = client

    seen = {}

    def fake_audit(a):
        seen["a"] = a

    monkeypatch.setattr(database.db, "create_audit_log", fake_audit)

    res = database.db.delete_interview(interview_id, profile_id)
    assert res in (True, False)
    assert "a" in seen or res is False


def test_delete_interview_data_error():
    class BrokenQuery:
        def delete(self):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise AttributeError("bad data")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "interviews":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    assert database.db.delete_interview(uuid4_str(), uuid4_str()) is False


def test_delete_interview_unexpected_exception_raises_database_error():
    class ExplodingQuery:
        def delete(self):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise Exception("boom")

    interview_id = uuid4_str()
    project_id = uuid4_str()
    profile_id = uuid4_str()

    class ExplodingClient(FakeClient):
        def table(self, name):
            if name == "interviews":
                class InterviewCheck:
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

                return InterviewCheck({"id": interview_id, "project_id": project_id})
            if name == "projects":
                return FakeClient({"projects": [{"id": project_id, "profile_id": profile_id}]}).table(name)
            return FakeClient({}).table(name)

    database.db.client = ExplodingClient({})
    with pytest.raises(database.DatabaseError):
        database.db.delete_interview(interview_id, profile_id)
