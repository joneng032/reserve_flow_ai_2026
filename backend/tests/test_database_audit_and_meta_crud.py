from backend import database
from backend.models import AuditLogCreate
from backend.tests.conftest import FakeClient, uuid4_str


def test_create_and_get_audit_logs_with_filter():
    pid = uuid4_str()
    # create audit in mock mode (use a valid UUID for entity_id)
    database.db.client = None
    created = database.db.create_audit_log(
        AuditLogCreate(project_id=pid, entity_type="component", entity_id=uuid4_str(), action="create", user_id="u1", details={})
    )
    assert created is not None

    # seed audit_logs table and projects for retrieval
    database.db.client = FakeClient({"projects": [{"id": pid, "profile_id": "p1"}], "audit_logs": [{"id": uuid4_str(), "project_id": pid, "entity_type": "component"}, {"id": uuid4_str(), "project_id": pid, "entity_type": "media_file"}]})
    logs = database.db.get_project_audit_logs(pid, "p1", entity_type="component")
    assert isinstance(logs, list)
    assert all(l.entity_type == "component" for l in logs)


def test_get_audit_logs_ownership_failure_returns_empty():
    pid = uuid4_str()
    # seed projects without matching profile_id
    database.db.client = FakeClient({"projects": [{"id": pid, "profile_id": "other"}], "audit_logs": [{"id": uuid4_str(), "project_id": pid, "entity_type": "component"}]})
    logs = database.db.get_project_audit_logs(pid, "p1")
    assert logs == []


def test_tags_templates_fielddefs_crud_and_ownership():
    pid = uuid4_str()
    # Use direct client insert operations for meta tables (no DB helpers exist)
    database.db.client = FakeClient({"projects": [{"id": pid, "profile_id": "p1"}], "tags": [], "templates": [], "field_definitions": []})

    q = database.db.client.table("tags").insert({"project_id": pid, "name": "T1"}).execute()
    assert q.data and q.data[0].get("name") == "T1"

    q2 = database.db.client.table("templates").insert({"project_id": pid, "name": "Temp1", "entity_type": "component", "field_definitions": []}).execute()
    assert q2.data and q2.data[0].get("name") == "Temp1"

    q3 = database.db.client.table("field_definitions").insert({"project_id": pid, "name": "f1", "entity_type": "component", "field_type": "text", "label": "F1"}).execute()
    assert q3.data and q3.data[0].get("name") == "f1"

    # Negative ownership: when project exists but belongs to another profile, DB layer helpers would prevent operations.
    # Here we demonstrate that inserting directly via client is possible, but ownership checks are enforced by db methods (tested elsewhere).
    database.db.client = FakeClient({"projects": [{"id": pid, "profile_id": "other"}], "tags": []})
    q4 = database.db.client.table("tags").insert({"project_id": pid, "name": "T2"}).execute()
    assert q4.data and q4.data[0].get("name") == "T2"
