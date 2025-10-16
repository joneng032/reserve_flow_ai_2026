from backend import database
from backend.tests.conftest import FakeClient, uuid4_str
import builtins


def test_delete_communication_success_and_audit(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    comm_id = uuid4_str()

    # Setup client with a communication owned by profile_id
    client = FakeClient({
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "communications": [{"id": comm_id, "project_id": proj_id, "profile_id": profile_id, "content": "x"}],
    })

    database.db.client = client

    # Capture audit calls by monkeypatching the DB instance method
    called = {}

    def fake_audit(audit):
        called["audit"] = audit

    monkeypatch.setattr(database.db, "create_audit_log", fake_audit)

    # Perform delete
    res = database.db.delete_communication(comm_id, profile_id)
    # delete_communication should return the deleted communication model (or None on failure)
    assert res is not None
    # Ensure audit was invoked
    assert "audit" in called


def test_delete_communication_not_owner_returns_none():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    other_profile = uuid4_str()
    comm_id = uuid4_str()

    # Communication belongs to other_profile
    database.db.client = FakeClient({
        "projects": [{"id": proj_id, "profile_id": other_profile}],
        "communications": [{"id": comm_id, "project_id": proj_id, "profile_id": other_profile, "content": "x"}],
    })

    res = database.db.delete_communication(comm_id, profile_id)
    assert res is False


def test_delete_communication_update_missing_response():
    # Simulate a case where the delete call returns an empty response list
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    comm_id = uuid4_str()

    base = {
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "communications": [{"id": comm_id, "project_id": proj_id, "profile_id": profile_id, "content": "x"}],
    }
    client = FakeClient(base)

    # Override the table for communications to produce an empty _data on delete
    q = client.table("communications")

    def delete_noop(self):
        # do not change _data (simulate no returned rows)
        self._data = []
        return self

    q.delete = delete_noop.__get__(q, type(q))
    client.table = lambda name: q if name == "communications" else FakeClient(base).table(name)

    database.db.client = client
    res = database.db.delete_communication(comm_id, profile_id)
    assert res is False
from backend import database
from backend.tests.conftest import FakeClient, uuid4_str


def test_delete_communication_success_and_failure(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    comm_id = uuid4_str()

    # Setup: communication exists and project owned
    database.db.client = FakeClient({
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "communications": [{"id": comm_id, "project_id": proj_id, "communication_type": "email"}],
    })

    called = []
    monkeypatch.setattr(database.db, "create_audit_log", lambda a: called.append(a))

    ok = database.db.delete_communication(comm_id, profile_id)
    assert ok is True
    assert called

    # Failure: communication not found or not owned
    database.db.client = FakeClient({"projects": [], "communications": []})
    ok2 = database.db.delete_communication(comm_id, profile_id)
    assert ok2 is False
