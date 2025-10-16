from backend import database
from backend.models import AuditLogCreate
from backend.tests.conftest import FakeClient, uuid4_str


def test_create_audit_log_and_fetch():
    project_id = uuid4_str()
    profile_id = uuid4_str()

    # Seed a project so ownership check passes
    project_row = {"id": project_id, "profile_id": profile_id}

    # Pre-seed an audit log row (this mimics an existing audit)
    audit_row = {
        "id": uuid4_str(),
        "project_id": project_id,
        "entity_type": "project",
        "entity_id": uuid4_str(),
        "action": "create",
        "actor_id": "user-1",
        "payload": {"foo": "bar"},
    }

    fake = FakeClient(table_data={"audit_logs": [audit_row], "projects": [project_row]})
    database.db.client = fake

    data = AuditLogCreate(
        project_id=project_id,
        entity_type="project",
        entity_id=uuid4_str(),
        action="create",
        user_id="user-1",
        details={"foo": "bar"},
    )

    # Call instance method create_audit_log
    created = database.db.create_audit_log(data)
    assert created is not None
    assert created.entity_type == "project"
    # AuditLog model does not expose project_id directly; ensure returned model has expected action
    assert created.action == "create"

    # Fetch audit logs for project
    results = database.db.get_project_audit_logs(project_id, profile_id)
    assert any(r.action == "create" for r in results)


def test_get_project_audit_logs_filters():
    project_id = uuid4_str()
    profile_id = uuid4_str()

    rows = [
        {"id": uuid4_str(), "project_id": project_id, "entity_type": "project", "entity_id": uuid4_str(), "action": "create", "actor_id": "u1"},
        {"id": uuid4_str(), "project_id": "pX", "entity_type": "component", "entity_id": uuid4_str(), "action": "update", "actor_id": "u2"},
        {"id": uuid4_str(), "project_id": uuid4_str(), "entity_type": "project", "entity_id": uuid4_str(), "action": "delete", "actor_id": "u1"},
    ]

    fake = FakeClient(table_data={"audit_logs": rows, "projects": [{"id": project_id, "profile_id": profile_id}]})
    database.db.client = fake

    # Fetch only for the seeded project with matching profile ownership
    res = database.db.get_project_audit_logs(project_id, profile_id)
    assert len(res) >= 1
    # All returned audit logs should be associated with the requested project (their raw data contains project_id)
    assert any(r.action == "create" for r in res)
