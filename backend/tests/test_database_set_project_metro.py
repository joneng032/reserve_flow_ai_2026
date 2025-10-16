from backend import database
from backend.models import ProjectMetroSettingCreate
from backend.tests.conftest import FakeClient, uuid4_str


def test_set_project_metro_create_and_update():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    # No existing metro setting -> create path
    database.db.client = FakeClient({
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "project_metro_settings": [],
    })

    created = database.db.set_project_metro(
        proj_id, ProjectMetroSettingCreate(metro_area="Area1", project_id=proj_id), profile_id
    )
    assert created is not None
    assert getattr(created, "metro_area", None) in ("Area1", "Area1")

    # Existing metro setting -> update path
    database.db.client = FakeClient({
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "project_metro_settings": [{"id": uuid4_str(), "project_id": proj_id, "metro_area": "Area1"}],
    })

    updated = database.db.set_project_metro(
        proj_id, ProjectMetroSettingCreate(metro_area="Area2", project_id=proj_id), profile_id
    )
    assert updated is not None
    assert getattr(updated, "metro_area", None) in ("Area2", "Area2")
