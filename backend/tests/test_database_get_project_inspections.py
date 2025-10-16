from backend import database
from backend.tests.conftest import FakeClient, uuid4_str
from backend.models import InspectionCreate


def test_get_project_inspections_filters_and_ownership():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    # Two inspections: one owned, one owned by another profile
    insp1 = {"id": uuid4_str(), "project_id": proj_id, "profile_id": profile_id, "status": "open", "inspection_type": "site"}
    insp2 = {"id": uuid4_str(), "project_id": proj_id, "profile_id": uuid4_str(), "status": "closed", "inspection_type": "building_exterior"}

    client = FakeClient({
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "inspections": [insp1, insp2],
    })
    database.db.client = client

    # Default call should return both inspections for the project (ownership verified via project)
    res = database.db.get_project_inspections(proj_id, profile_id)
    assert isinstance(res, list)
    assert any(str(r.id) == insp1["id"] for r in res)

    # Filter by status should only return matching ones
    res_open = database.db.get_project_inspections(proj_id, profile_id, inspection_status="open")
    assert len(res_open) >= 1
    assert all(getattr(r, "status", None) == "open" for r in res_open)


def test_get_project_inspections_ownership_negative():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    # Project exists but owned by someone else -> should return empty list
    client = FakeClient({
        "projects": [{"id": proj_id, "profile_id": uuid4_str()}],
        "inspections": [],
    })
    database.db.client = client
    res = database.db.get_project_inspections(proj_id, profile_id)
    assert res == []
from backend import database
from backend.tests.conftest import FakeClient, uuid4_str
from backend.models import InspectionCreate


def test_get_project_inspections_filters_and_returns():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    ins1 = {"id": uuid4_str(), "project_id": proj_id, "inspection_type": "typeA", "status": "open"}
    ins2 = {"id": uuid4_str(), "project_id": proj_id, "inspection_type": "typeB", "status": "closed"}

    database.db.client = FakeClient({
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "inspections": [ins1, ins2],
    })

    res = database.db.get_project_inspections(proj_id, profile_id, inspection_type="typeA")
    assert isinstance(res, list)
    assert len(res) == 1
    assert getattr(res[0], "inspection_type", None) == "typeA"
