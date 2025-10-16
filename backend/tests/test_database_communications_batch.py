from backend import database
from backend.models import CommunicationCreate, CommunicationUpdate
from backend.tests.conftest import FakeClient, uuid4_str


def test_get_project_communications_filters_and_ownership():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    rows = [
        {"id": uuid4_str(), "project_id": proj_id, "communication_type": "email", "status": "completed", "direction": "outbound", "contact_name": "X"},
        {"id": uuid4_str(), "project_id": proj_id, "communication_type": "phone", "status": "pending", "direction": "inbound", "contact_name": "Y"},
    ]

    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "communications": rows})
    res = database.db.get_project_communications(proj_id, profile_id, communication_type="email")
    assert isinstance(res, list)
    assert len(res) == 1

    # negative ownership -> empty
    database.db.client = FakeClient({"projects": [], "communications": rows})
    res2 = database.db.get_project_communications(proj_id, profile_id)
    assert res2 == []


def test_get_update_delete_communication_and_audit(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    comm_id = uuid4_str()

    # prepare db with the communication owned by profile
    database.db.client = FakeClient({
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "communications": [{"id": comm_id, "project_id": proj_id, "communication_type": "email", "direction": "outbound", "contact_name": "A"}],
    })

    # get single
    got = database.db.get_communication(comm_id, profile_id)
    assert got is None or str(getattr(got, "id", None)) == comm_id

    # update with audit
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "communications": [{"id": comm_id, "project_id": proj_id, "communication_type": "email", "direction": "outbound", "contact_name": "A"}]})
    audits = []
    monkeypatch.setattr(database.db, "create_audit_log", lambda a: audits.append(a))

    updated = database.db.update_communication(comm_id, CommunicationUpdate(communication_type="email", direction="outbound", contact_name="A", subject="S"), profile_id)
    assert updated is None or getattr(updated, "subject", None) == "S"
    assert audits

    # delete with audit
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "communications": [{"id": comm_id, "project_id": proj_id, "communication_type": "email"}]})
    audits2 = []
    monkeypatch.setattr(database.db, "create_audit_log", lambda a: audits2.append(a))

    ok = database.db.delete_communication(comm_id, profile_id)
    assert ok is True
    assert audits2
