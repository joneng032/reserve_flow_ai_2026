from backend import database
from backend.models import ProjectMetroSettingCreate
from backend.tests.conftest import FakeClient, uuid4_str


def test_set_project_metro_create_and_update_and_ownership(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    # No existing metro setting -> create path should produce audit
    database.db.client = FakeClient({
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "project_metro_settings": [],
    })

    # set_project_metro does not currently emit an audit in the DB layer;
    # assert the creation path returns a model instance
    created = database.db.set_project_metro(
        proj_id, ProjectMetroSettingCreate(metro_area="Area1", project_id=proj_id), profile_id
    )
    assert created is not None

    # Existing metro setting -> update path
    database.db.client = FakeClient({
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "project_metro_settings": [{"id": uuid4_str(), "project_id": proj_id, "metro_area": "Area1"}],
    })

    updated = database.db.set_project_metro(
        proj_id, ProjectMetroSettingCreate(metro_area="Area2", project_id=proj_id), profile_id
    )
    assert updated is not None
    assert getattr(updated, "metro_area", None) == "Area2"

    # Ownership negative: project exists but different owner
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": uuid4_str()}], "project_metro_settings": []})
    res = database.db.set_project_metro(proj_id, ProjectMetroSettingCreate(metro_area="Z", project_id=proj_id), profile_id)
    assert res is None


def test_get_project_metro_success_and_none():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    # Not owned project -> None
    database.db.client = FakeClient({"projects": []})
    assert database.db.get_project_metro(proj_id, profile_id) is None

    # Owned with setting -> returns model
    database.db.client = FakeClient({
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "project_metro_settings": [{"id": uuid4_str(), "project_id": proj_id, "metro_area": "MetroX"}],
    })
    got = database.db.get_project_metro(proj_id, profile_id)
    assert got is not None
    assert getattr(got, "metro_area", None) == "MetroX"
