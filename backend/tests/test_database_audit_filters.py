from backend.database import Database


def test_get_project_audit_logs_with_entity_type_filter():
    from backend.tests.conftest import FakeClient, uuid4_str

    pid = uuid4_str()
    a1 = {"id": uuid4_str(), "project_id": pid, "entity_type": "component", "entity_id": uuid4_str(), "action": "create"}
    a2 = {"id": uuid4_str(), "project_id": pid, "entity_type": "media_file", "entity_id": uuid4_str(), "action": "create"}

    client = FakeClient(table_data={
        "projects": [{"id": pid, "profile_id": "profile-1"}],
        "audit_logs": [a1, a2],
    })

    db = Database()
    db.client = client

    logs = db.get_project_audit_logs(pid, "profile-1", entity_type="media_file")
    assert len(logs) == 1
    assert getattr(logs[0], "entity_type", None) == "media_file"
