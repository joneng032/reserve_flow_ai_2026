from backend import database
from backend.models import ProfileCreate
from backend.tests.conftest import FakeClient, uuid4_str


def test_create_profile_mock_mode_returns_profile():
    pid = uuid4_str()
    database.db.client = FakeClient({"profiles": []})

    profile = database.db.create_profile(ProfileCreate(name="T", email="t@example.com"), mock=True)
    assert profile.name == "T"


def test_get_projects_mock_mode_returns_list():
    # get_projects uses client to join projects table
    proj_id = uuid4_str()
    database.db.client = FakeClient({"projects": [{"id": proj_id, "name": "P"}]})
    projects = database.db.get_projects_for_profile("some-id")
    assert isinstance(projects, list)
    assert any(p.get("id") == proj_id for p in projects)
from backend import database
from backend.models import ProfileCreate, ProjectCreate
from backend.tests.conftest import uuid4_str


def test_create_profile_mock_mode_returns_profile():
    db = database.Database()
    prof = db.create_profile(ProfileCreate(name="P", email="p@example.com"))
    assert prof is not None
    assert hasattr(prof, "id")


def test_get_projects_mock_mode_returns_list():
    db = database.Database()
    res = db.get_projects(profile_id=uuid4_str())
    assert isinstance(res, list)

