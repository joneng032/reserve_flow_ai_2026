from backend import database
from backend.tests.conftest import FakeClient, uuid4_str


def test_delete_communication_missing_communication_type_still_audited(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    comm_id = uuid4_str()

    # communication row missing 'communication_type'
    client = FakeClient({
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "communications": [{"id": comm_id, "project_id": proj_id, "profile_id": profile_id}],
    })
    database.db.client = client

    called = {}

    def fake_audit(audit):
        called["audit"] = audit

    monkeypatch.setattr(database.db, "create_audit_log", fake_audit)

    res = database.db.delete_communication(comm_id, profile_id)
    assert res is True
    assert "audit" in called


def test_delete_communication_project_join_shape(monkeypatch):
    # Simulate the case where the select used to verify ownership returns
    # nested project info under the 'projects' join key
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    comm_id = uuid4_str()

    # The communication_check should include project_id and an inner projects object
    client = FakeClient({
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "communications": [{"id": comm_id, "project_id": proj_id, "profile_id": profile_id}],
    })

    # Replace the communications table query to return a shaped row
    q = client.table("communications")

    def execute_shaped(self):
        # Return a row shaped like: {'project_id': proj_id, 'projects': {'profile_id': profile_id}}
        return type("R", (), {"data": [{"project_id": proj_id, "projects": {"profile_id": profile_id}}]})()

    q.execute = execute_shaped.__get__(q, type(q))
    client.table = lambda name: q if name == "communications" else FakeClient(client.table_data).table(name)
    database.db.client = client

    called = {}

    def fake_audit(audit):
        called["audit"] = audit

    monkeypatch.setattr(database.db, "create_audit_log", fake_audit)

    res = database.db.delete_communication(comm_id, profile_id)
    assert res is True
    assert "audit" in called
