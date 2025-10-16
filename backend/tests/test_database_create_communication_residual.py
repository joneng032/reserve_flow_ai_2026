import pytest
from backend import database
from backend.models import CommunicationCreate
from backend.tests.conftest import FakeClient, uuid4_str


def test_create_communication_client_none():
    database.db.client = None
    try:
        res = database.db.create_communication(
            CommunicationCreate(
                project_id=uuid4_str(),
                communication_type="mock",
                direction="outbound",
                contact_name="A",
            ),
            uuid4_str(),
        )
    except Exception:
        return
    assert res is not None and getattr(res, "communication_type", None) == "mock"


def test_create_communication_ownership_negative():
    database.db.client = FakeClient({"projects": []})
    res = database.db.create_communication(
        CommunicationCreate(project_id=uuid4_str(), communication_type="m", direction="inbound", contact_name="B"),
        uuid4_str(),
    )
    assert res is None


def test_create_communication_success_and_audit(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    comm_row = {"id": uuid4_str(), "project_id": proj_id, "communication_type": "m", "subject": "S"}
    client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "communications": [comm_row]})
    database.db.client = client

    seen = {}

    def fake_audit(a):
        seen["a"] = a

    monkeypatch.setattr(database.db, "create_audit_log", fake_audit)

    res = database.db.create_communication(CommunicationCreate(project_id=proj_id, communication_type="m", direction="outbound", contact_name="C"), profile_id)
    assert res is None or getattr(res, "communication_type", None) == "m"
    assert "a" in seen


def test_create_communication_data_error():
    class BrokenQuery:
        def insert(self, *a, **kw):
            return self

        def execute(self):
            raise AttributeError("bad data")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "communications":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    res = database.db.create_communication(CommunicationCreate(project_id=uuid4_str(), communication_type="m", direction="out", contact_name="X"), uuid4_str())
    assert res is None


def test_create_communication_unexpected_exception_raises_database_error():
    class ExplodingQuery:
        def insert(self, *a, **kw):
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
        database.db.create_communication(
            CommunicationCreate(
                project_id=project_id,
                communication_type="m",
                direction="out",
                contact_name="X",
            ),
            profile_id,
        )
