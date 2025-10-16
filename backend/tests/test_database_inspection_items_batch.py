from backend import database
from backend.models import InspectionItemCreate, InspectionItemUpdate
from backend.tests.conftest import FakeClient, uuid4_str


def test_create_inspection_item_and_audit(monkeypatch):
    proj_id = uuid4_str()
    insp_id = uuid4_str()
    profile_id = uuid4_str()

    database.db.client = FakeClient({
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "inspections": [{"id": insp_id, "project_id": proj_id}],
        "inspection_items": [],
    })

    audits = []
    monkeypatch.setattr(database.db, "create_audit_log", lambda a: audits.append(a))

    it = database.db.create_inspection_item(InspectionItemCreate(inspection_id=insp_id, item_type="check", item_name="I1"), profile_id)
    assert it is not None
    assert audits


def test_get_inspection_items_filters_and_ownership():
    proj_id = uuid4_str()
    insp_id = uuid4_str()
    profile = uuid4_str()

    row1 = {"id": uuid4_str(), "inspection_id": insp_id, "item_type": "check", "item_name": "A"}
    row2 = {"id": uuid4_str(), "inspection_id": insp_id, "item_type": "measure", "item_name": "B"}

    # positive ownership
    database.db.client = FakeClient({
        "projects": [{"id": proj_id, "profile_id": profile}],
        "inspections": [{"id": insp_id, "project_id": proj_id}],
        "inspection_items": [row1, row2],
    })

    res = database.db.get_inspection_items(insp_id, profile, item_type="check")
    assert isinstance(res, list)
    assert len(res) == 1

    # negative ownership -> empty
    database.db.client = FakeClient({"projects": [], "inspections": [], "inspection_items": [row1]})
    res2 = database.db.get_inspection_items(insp_id, profile)
    assert res2 == []
