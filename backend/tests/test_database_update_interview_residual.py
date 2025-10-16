import pytest
from backend import database
from backend.models import InterviewUpdate
from backend.tests.conftest import FakeClient, uuid4_str


def test_update_interview_client_none(monkeypatch):
    # In mock-mode the function should return a simple object or None
    class DummyInterview:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    monkeypatch.setattr(database, "Interview", DummyInterview, raising=False)

    database.db.client = None
    res = database.db.update_interview(
        uuid4_str(),
        InterviewUpdate(interviewee_name="Tester", interview_type="mock"),
        uuid4_str(),
    )
    assert res is None or hasattr(res, "id")


def test_update_interview_ownership_negative():
    database.db.client = FakeClient({"projects": [], "interviews": []})
    res = database.db.update_interview(
        uuid4_str(),
        InterviewUpdate(interviewee_name="Tester", interview_type="mock"),
        uuid4_str(),
    )
    assert res is None


def test_update_interview_success_and_audit(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    interview_id = uuid4_str()

    rows = {
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "interviews": [{"id": interview_id, "project_id": proj_id, "interview_type": "initial"}],
    }
    client = FakeClient(rows)
    database.db.client = client

    captured = {}

    def fake_audit(audit):
        captured['audit'] = audit

    monkeypatch.setattr(database.db, "create_audit_log", fake_audit, raising=False)

    res = database.db.update_interview(
        interview_id,
        InterviewUpdate(interviewee_name="Tester", interview_type="follow_up"),
        profile_id,
    )
    assert res is not None
    assert 'audit' in captured


def test_update_interview_data_error():
    class BrokenQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            raise AttributeError("bad data")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "interviews":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    res = database.db.update_interview(
        uuid4_str(),
        InterviewUpdate(interviewee_name="Tester", interview_type="x"),
        uuid4_str(),
    )
    assert res is None


def test_update_interview_unexpected_exception_raises_database_error():
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
        database.db.update_interview(
            uuid4_str(),
            InterviewUpdate(interviewee_name="Tester", interview_type="x"),
            uuid4_str(),
        )
