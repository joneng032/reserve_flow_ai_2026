from backend import database
from backend.models import MeetingCreate, MeetingUpdate, MediaFileCreate, MediaFileUpdate, EvidenceCreate, EvidenceUpdate
from backend.tests.conftest import FakeClient, uuid4_str
import types


def test_create_meeting_creates_audit_and_returns_meeting(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "meetings": []})

    called = {}

    def fake_audit(audit):
        called['audit'] = audit

    # Patch the concrete db instance to ensure the call is captured regardless of test ordering
    monkeypatch.setattr(database.db, "create_audit_log", lambda a: fake_audit(a))

    m = database.db.create_meeting(MeetingCreate(project_id=proj_id, title="T", meeting_type="site", meeting_date="2024-01-01T00:00:00Z"), profile_id)
    assert m is not None
    assert 'audit' in called


def test_get_project_meetings_filters_by_type():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    meetings = [{"id": uuid4_str(), "project_id": proj_id, "meeting_type": "site", "meeting_date": "2024-01-01T00:00:00Z", "title": "Site"}, {"id": uuid4_str(), "project_id": proj_id, "meeting_type": "desk", "meeting_date": "2024-01-02T00:00:00Z", "title": "Desk"}]
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "meetings": meetings})

    res = database.db.get_project_meetings(proj_id, profile_id, meeting_type="site")
    assert len(res) == 1
    assert res[0].meeting_type == "site"


def test_get_meeting_ownership():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    mid = uuid4_str()
    database.db.client = FakeClient({"meetings": [{"id": mid, "project_id": proj_id, "meeting_type": "mock", "meeting_date": "2024-01-01T00:00:00Z", "title": "M"}], "projects": [{"id": proj_id, "profile_id": profile_id}]})

    m = database.db.get_meeting(mid, profile_id)
    # May return Meeting Pydantic model or None; assert successful path
    assert m is not None


def test_media_create_get_delete_audit(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "media_files": []})

    audits = []
    monkeypatch.setattr(database.db, "create_audit_log", lambda a: audits.append(a))

    mf = database.db.create_media_file(MediaFileCreate(project_id=proj_id, file_name="f.jpg", file_type="image", file_path="/tmp/f.jpg", mime_type="image/jpeg", file_size=123), profile_id)
    assert mf is not None
    assert audits

    # fetch via get_media_file returns same media via FakeClient when shaped
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "media_files": [{"id": str(mf.id), "project_id": proj_id, "file_name": "f.jpg", "file_type": "image"}]})
    got = database.db.get_media_file(str(mf.id), profile_id)
    assert got is not None

    ok = database.db.delete_media_file(str(mf.id), profile_id)
    assert ok is True
    assert len(audits) >= 2


def test_create_and_update_evidence_creates_and_updates_and_audits(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "evidence": []})

    audits = []
    monkeypatch.setattr(database.db, "create_audit_log", lambda a: audits.append(a))

    ev = database.db.create_evidence(EvidenceCreate(project_id=proj_id, evidence_type="photo"), profile_id)
    assert ev is not None
    assert audits

    # prepare client state to update
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "evidence": [{"id": str(ev.id), "project_id": proj_id, "evidence_type": "photo"}]})
    updated = database.db.update_evidence(str(ev.id), EvidenceUpdate(evidence_type="document"), profile_id)
    assert updated is not None
    assert len(audits) >= 2
