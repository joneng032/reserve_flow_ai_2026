"""Focused tests for Database project-related methods.

Tests exercise mock-mode behavior (client None), fake client responses,
and exception mapping.
"""
import pytest

from backend.database import Database, DatabaseError


def test_create_project_mock_mode_returns_project():
    db = Database()
    db.client = None

    class P:
        def __init__(self):
            self.profile_id = "550e8400-e29b-41d4-a716-446655440010"
            self.name = "Proj"
            self.client_name = "Client"
            self.address = "Addr"
            self.current_reserve_balance = 0.0
            self.custom_fields = {}

    proj = db.create_project(P())
    assert proj is not None
    assert proj.name == "Proj"


def test_get_projects_mock_mode_returns_list():
    db = Database()
    db.client = None

    projects = db.get_projects("profile-1", 0, 10)
    assert isinstance(projects, list)


def test_update_project_mock_mode_returns_project():
    db = Database()
    db.client = None

    class U:
        def model_dump(self, exclude_unset=True):
            return {"name": "Updated"}

    proj = db.update_project("pid", "profile-1", U())
    assert proj is not None
    assert proj.name == "Updated"


def test_delete_project_mock_mode_returns_bool():
    db = Database()
    db.client = None

    result = db.delete_project("pid", "profile-1")
    assert result is True or result is False


def test_create_project_client_exception_maps_to_database_error():
    class ExplodingClient:
        def table(self, _):
            raise RuntimeError("boom")

    db = Database()
    db.client = ExplodingClient()

    class FakeProjectData:
        def model_dump(self):
            return {"name": "x", "profile_id": "550e8400-e29b-41d4-a716-446655440020"}

    with pytest.raises(DatabaseError):
        db.create_project(FakeProjectData())
