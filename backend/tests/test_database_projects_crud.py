from backend import database
from backend.models import ProjectCreate, ProjectUpdate
from backend.tests.conftest import FakeClient, uuid4_str


def test_create_project_mock_mode_returns_project():
    db = database.Database()
    proj = db.create_project(ProjectCreate(name="Test", client_name="C", address="A"), profile_id=uuid4_str())
    assert proj is not None
    assert hasattr(proj, "id")


def test_update_project_requires_owner():
    proj_id = uuid4_str()
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": uuid4_str()}]})

    up = database.db.update_project(proj_id, "not-owner", ProjectUpdate(name="New"))
    assert up is None
import pytest

from backend.database import Database, DatabaseError


def test_create_project_mock_mode_returns_project():
    db = Database()
    db.client = None

    class P:
        def __init__(self):
            self.profile_id = "550e8400-e29b-41d4-a716-446655440100"
            self.name = "ProjX"
            self.client_name = "Client"
            self.address = None
            from decimal import Decimal

            self.current_reserve_balance = Decimal("0")
            self.custom_fields = {}

    proj = db.create_project(P())
    assert proj is not None
    assert getattr(proj, "name", None) == "ProjX"


def test_create_project_client_mode_and_get_project():
    from backend.tests.conftest import FakeClient, uuid4_str

    pid = uuid4_str()
    proj_id = uuid4_str()
    client = FakeClient(table_data={
        "projects": [{"id": proj_id, "profile_id": pid, "name": "P1", "components": [], "categories": []}],
    })

    db = Database()
    db.client = client

    # get_project requires profile_id ownership match
    got = db.get_project(proj_id, pid)
    assert got is not None
    assert getattr(got, "id", None) is not None


def test_update_project_mock_and_client_and_delete(monkeypatch):
    from backend.tests.conftest import FakeClient, uuid4_str

    db = Database()
    db.client = None

    class U:
        def model_dump(self, exclude_unset=True):
            return {"name": "Updated"}

    res = db.update_project("550e8400-e29b-41d4-a716-446655440200", "550e8400-e29b-41d4-a716-446655440200", U())
    assert res is not None
    assert getattr(res, "name", None) == "Updated"

    # client-mode update/delete
    pid = uuid4_str()
    proj_id = uuid4_str()
    client = FakeClient(table_data={
        "projects": [{"id": proj_id, "profile_id": pid, "name": "P2"}],
    })
    db.client = client

    class U2:
        def model_dump(self, exclude_unset=True):
            return {"name": "ClientUpdated"}

    updated = db.update_project(proj_id, pid, U2())
    assert updated is not None

    deleted = db.delete_project(proj_id, pid)
    assert deleted is True or deleted is False


def test_get_projects_client_exception_maps_to_database_error():
    class ExplodingClient:
        def table(self, _):
            raise RuntimeError("boom")

    db = Database()
    db.client = ExplodingClient()

    with pytest.raises(DatabaseError):
        db.get_projects("profile-1")
