import pytest
from backend import database
from backend.tests.conftest import FakeClient, uuid4_str
from backend.models import Communication


def test_get_project_communications_client_none():
    database.db.client = None
    res = database.db.get_project_communications(uuid4_str(), uuid4_str())
    assert isinstance(res, list) and res == []


def test_get_project_communications_ownership_negative():
    database.db.client = FakeClient({"projects": []})
    res = database.db.get_project_communications(uuid4_str(), uuid4_str())
    assert res == []


def test_get_project_communications_success_filters_and_pagination():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    comms = [
        {"id": uuid4_str(), "project_id": proj_id, "communication_type": "email", "status": "completed"},
        {"id": uuid4_str(), "project_id": proj_id, "communication_type": "phone", "status": "pending"},
    ]
    client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "communications": comms})
    database.db.client = client

    res_all = database.db.get_project_communications(proj_id, profile_id)
    assert all(isinstance(x, Communication) for x in res_all)

    res_filtered = database.db.get_project_communications(proj_id, profile_id, communication_type="email")
    assert all(getattr(x, "communication_type", None) == "email" for x in res_filtered)

    res_status = database.db.get_project_communications(proj_id, profile_id, status="pending")
    assert all(getattr(x, "status", None) == "pending" for x in res_status)


def test_get_project_communications_data_error():
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
            if name == "communications":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    res = database.db.get_project_communications(uuid4_str(), uuid4_str())
    assert res == []


def test_get_project_communications_unexpected_exception_raises_database_error():
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
            if name == "communications":
                return ExplodingQuery()
            if name == "projects":
                return FakeClient({"projects": [{"id": project_id, "profile_id": profile_id}]}).table(name)
            return FakeClient({}).table(name)

    database.db.client = ExplodingClient({})
    with pytest.raises(database.DatabaseError):
        database.db.get_project_communications(project_id, profile_id)
