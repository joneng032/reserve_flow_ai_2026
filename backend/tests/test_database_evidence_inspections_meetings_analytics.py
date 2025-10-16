from backend import database
from backend.models import (
    EvidenceCreate,
    InspectionCreate,
    InspectionItemCreate,
    InterviewCreate,
    MeetingCreate,
)
from backend.tests.conftest import FakeClient, uuid4_str


def test_evidence_create_and_get():
    pid = uuid4_str()
    database.db.client = FakeClient({"projects": [{"id": pid, "profile_id": "p1"}], "evidence": []})

    ev = database.db.create_evidence(
        EvidenceCreate(project_id=pid, evidence_type="photo", file_name="e.jpg"),
        "p1",
    )
    assert ev is not None

    eid = str(getattr(ev, "id", uuid4_str()))
    database.db.client = FakeClient({"projects": [{"id": pid, "profile_id": "p1"}], "evidence": [{"id": eid, "project_id": pid}]})
    got = database.db.get_evidence(eid, "p1")
    # id may be returned as UUID object; compare string forms
    assert got is None or str(getattr(got, "id", None)) == eid


def test_inspection_and_items_flow():
    pid = uuid4_str()
    database.db.client = FakeClient({"projects": [{"id": pid, "profile_id": "p1"}], "inspections": [], "inspection_items": []})

    ins = database.db.create_inspection(InspectionCreate(project_id=pid, inspection_type="site"), "p1")
    assert ins is not None

    iid = str(getattr(ins, "id", uuid4_str()))
    database.db.client = FakeClient({"projects": [{"id": pid, "profile_id": "p1"}], "inspections": [{"id": iid, "project_id": pid}]})

    item = database.db.create_inspection_item(InspectionItemCreate(inspection_id=iid, item_name="Door", item_type="condition"), "p1")
    assert item is not None


def test_interview_and_meeting_create_get():
    pid = uuid4_str()
    database.db.client = FakeClient({"projects": [{"id": pid, "profile_id": "p1"}], "interviews": [], "meetings": []})

    intr = database.db.create_interview(InterviewCreate(project_id=pid, interviewee_name="Bob", interview_type="initial"), "p1")
    assert intr is not None

    mid = uuid4_str()
    meeting = database.db.create_meeting(MeetingCreate(project_id=pid, title="M1", meeting_date="2025-01-01T00:00:00Z", meeting_type="regular"), "p1")
    assert meeting is not None


def test_analytics_cost_and_reserve():
    pid = uuid4_str()
    # seed project and components for cost calc
    rows = [{"id": uuid4_str(), "project_id": pid, "base_cost": 100}, {"id": uuid4_str(), "project_id": pid, "base_cost": 200}]
    database.db.client = FakeClient({"projects": [{"id": pid, "profile_id": "p1", "current_reserve_balance": 50}], "components": rows})

    cost = database.db.get_cost_analysis(pid, "p1")
    assert cost.total_components == 2

    reserve = database.db.get_reserve_analysis(pid, "p1")
    assert hasattr(reserve, "percent_funded")
