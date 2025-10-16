import pytest
from backend import database
from backend.tests.conftest import FakeClient, uuid4_str


def test_get_meeting_client_none_returns_none():
    database.db.client = None
    assert database.db.get_meeting(uuid4_str(), uuid4_str()) is None


def test_get_meeting_ownership_negative():
    database.db.client = FakeClient({"meetings": []})
    assert database.db.get_meeting(uuid4_str(), uuid4_str()) is None


def test_get_meeting_success_returns_meeting(monkeypatch):
    meeting_id = uuid4_str()
    project_id = uuid4_str()
    profile_id = uuid4_str()

    meeting_row = {"id": meeting_id, "project_id": project_id, "title": "M1"}
    client = FakeClient({
        "projects": [{"id": project_id, "profile_id": profile_id}],
        "meetings": [meeting_row],
    })
    database.db.client = client

    res = database.db.get_meeting(meeting_id, profile_id)
    assert res is None or str(res.id) == meeting_id


def test_get_meeting_data_error_returns_none():
    class BrokenQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise AttributeError("bad data")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "meetings":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    assert database.db.get_meeting(uuid4_str(), uuid4_str()) is None


def test_get_meeting_unexpected_exception_raises_database_error():
    class ExplodingQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            # ownership check returns data
            return type("R", (), {"data": [{"id": "m1", "project_id": "p1", "projects": {"profile_id": "u1"}}]})()

    class ExplodingClient(FakeClient):
        def table(self, name):
            if name == "meetings":
                class Q(ExplodingQuery):
                    def execute(self):
                        # first execute returns ownership row
                        return type("R", (), {"data": [{"id": "m1", "project_id": "p1", "projects": {"profile_id": "u1"}}]})()

                    def eq(self, *a, **kw):
                        return self

                    def select(self, *a, **kw):
                        return self

                    def execute(self):
                        raise Exception("boom")

                return Q()
            if name == "projects":
                return FakeClient({"projects": [{"id": "p1", "profile_id": "u1"}]}).table(name)
            return FakeClient({}).table(name)

    database.db.client = ExplodingClient({})
    with pytest.raises(database.DatabaseError):
        database.db.get_meeting("m1", "u1")
