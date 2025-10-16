import pytest
from backend import database
from backend.models import CommunicationUpdate
from backend.tests.conftest import FakeClient, uuid4_str


def test_update_communication_client_none(monkeypatch):
    class DummyComm:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    monkeypatch.setattr(database, "Communication", DummyComm, raising=False)

    database.db.client = None
    res = database.db.update_communication(uuid4_str(), CommunicationUpdate(communication_type="email", direction="outbound", contact_name="A"), uuid4_str())
    assert res is None or hasattr(res, "id")


def test_update_communication_ownership_negative():
    database.db.client = FakeClient({"projects": [], "communications": []})
    res = database.db.update_communication(uuid4_str(), CommunicationUpdate(communication_type="email", direction="outbound", contact_name="A"), uuid4_str())
    assert res is None


def test_update_communication_success_and_audit(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    comm_id = uuid4_str()

    rows = {
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "communications": [{"id": comm_id, "project_id": proj_id, "communication_type": "email", "direction": "outbound", "contact_name": "A"}],
    }
    client = FakeClient(rows)
    database.db.client = client

    captured = {}

    def fake_audit(audit):
        captured['audit'] = audit

    monkeypatch.setattr(database.db, "create_audit_log", fake_audit, raising=False)

    res = database.db.update_communication(comm_id, CommunicationUpdate(communication_type="email", direction="outbound", contact_name="B"), profile_id)
    assert res is not None
    assert 'audit' in captured


def test_update_communication_data_error():
    class BrokenQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            raise AttributeError("bad data")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "communications":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    res = database.db.update_communication(uuid4_str(), CommunicationUpdate(communication_type="email", direction="outbound", contact_name="A"), uuid4_str())
    assert res is None


def test_update_communication_unexpected_exception_raises_database_error():
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
        database.db.update_communication(uuid4_str(), CommunicationUpdate(communication_type="email", direction="outbound", contact_name="A"), uuid4_str())
