from backend.database import Database


def test_create_evidence_mock_mode():
    from backend.models import EvidenceCreate
    from backend.tests.conftest import uuid4_str

    db = Database()
    db.client = None
    pid = uuid4_str()

    e = EvidenceCreate(project_id=pid, evidence_type="photo", file_name="img.jpg")
    created = db.create_evidence(e, profile_id="profile-1")
    assert created is not None
    assert getattr(created, "evidence_type", None) == "photo"


def test_evidence_crud_and_audit(monkeypatch):
    from backend.tests.conftest import FakeClient, uuid4_str
    from backend.models import EvidenceCreate, EvidenceUpdate

    pid = uuid4_str()
    eid = uuid4_str()

    client = FakeClient(table_data={
        "projects": [{"id": pid, "profile_id": "profile-1"}],
        "evidence": [{"id": eid, "project_id": pid, "projects": {"profile_id": "profile-1"}, "evidence_type": "photo"}],
    })

    db = Database()
    db.client = client

    called = {}

    def fake_audit(a):
        called["ok"] = True
        return None

    monkeypatch.setattr(db, "create_audit_log", fake_audit)

    ec = EvidenceCreate(project_id=pid, evidence_type="video", file_name="clip.mp4")
    created = db.create_evidence(ec, profile_id="profile-1")
    assert created is not None

    lst = db.get_project_evidence(pid, "profile-1")
    assert isinstance(lst, list)

    got = db.get_evidence(eid, "profile-1")
    assert got is not None

    eu = EvidenceUpdate(file_name="new.mp4")
    updated = db.update_evidence(eid, eu, profile_id="profile-1")
    assert updated is not None
    assert called.get("ok")

    deleted = db.delete_evidence(eid, "profile-1")
    assert isinstance(deleted, bool)
