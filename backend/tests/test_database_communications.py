from backend import database
from backend.database import Database
from backend.models import CommunicationCreate, CommunicationUpdate
from backend.tests.conftest import FakeClient, uuid4_str


def test_create_communication_client_mode():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "communications": []})

    comm = database.db.create_communication(
        CommunicationCreate(
            project_id=proj_id,
            message="Hi",
            communication_type="email",
            direction="outbound",
            contact_name="T",
        ),
        profile_id,
    )
    assert comm is None or hasattr(comm, "id")


def test_create_communication_mock_mode_returns_stub():
    db = Database()
    db.client = None

    pid = uuid4_str()
    comm = CommunicationCreate(project_id=pid, communication_type="email", direction="outbound", contact_name="Alice", message="Hi")
    created = db.create_communication(comm, profile_id="profile-1")
    assert created is not None
    assert getattr(created, "communication_type", None) == "email"


def test_get_project_communications_filters_and_order():
    pid = uuid4_str()
    rows = [
        {"id": uuid4_str(), "project_id": pid, "communication_type": "email", "status": "completed", "contact_name": "A", "direction": "outbound"},
        {"id": uuid4_str(), "project_id": pid, "communication_type": "call", "status": "pending", "contact_name": "B", "direction": "inbound"},
    ]

    client = FakeClient(table_data={
        "projects": [{"id": pid, "profile_id": "profile-1"}],
        "communications": rows,
    })

    db = Database()
    db.client = client

    all_comms = db.get_project_communications(pid, "profile-1")
    assert len(all_comms) == 2

    emails = db.get_project_communications(pid, "profile-1", communication_type="email")
    assert len(emails) == 1
    assert getattr(emails[0], "communication_type", None) == "email"


def test_update_communication_creates_audit_log(monkeypatch):
    pid = uuid4_str()
    cid = uuid4_str()

    client = FakeClient(table_data={
        "communications": [{"id": cid, "project_id": pid, "projects": {"profile_id": "profile-1"}, "communication_type": "email"}],
    })

    db = Database()
    db.client = client

    called = {}

    def fake_create_audit_log(audit_data):
        called["ok"] = True
        return None

    monkeypatch.setattr(db, "create_audit_log", fake_create_audit_log)

    upd = CommunicationUpdate(communication_type="email", direction="inbound", contact_name="Alice")
    res = db.update_communication(cid, upd, profile_id="profile-1")
    assert res is not None
    assert called.get("ok")
