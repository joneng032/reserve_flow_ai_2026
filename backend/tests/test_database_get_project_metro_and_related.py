from backend import database
from backend.tests.conftest import FakeClient, uuid4_str
from backend.models import ProjectMetroSettingCreate


def test_get_project_metro_none_when_no_project():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    database.db.client = FakeClient({"projects": []})
    res = database.db.get_project_metro(proj_id, profile_id)
    assert res is None


def test_get_project_metro_present():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    database.db.client = FakeClient({
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "project_metro_settings": [{"id": uuid4_str(), "project_id": proj_id, "metro_area": "X"}],
    })
    res = database.db.get_project_metro(proj_id, profile_id)
    assert res is not None
    assert getattr(res, "metro_area", None) == "X"
