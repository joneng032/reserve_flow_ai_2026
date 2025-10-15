"""Tests for inspection-related methods in backend.database.

Pattern: mock-mode, fake client success response, client exception mapping,
and data-shape error handling where applicable.
"""
import pytest

from backend.database import Database, DatabaseError


def test_create_inspection_mock_mode_returns_namespace():
    db = Database()
    db.client = None

    class Ins:
        def __init__(self):
            self.project_id = "550e8400-e29b-41d4-a716-446655440400"
            self.name = "Inspect"

        def model_dump(self):
            return {"name": "Inspect"}

    res = db.create_inspection(Ins(), "profile-1")
    assert res is not None
    # The Inspection mock returns `inspection_type` (not `name`) so assert that
    assert getattr(res, "inspection_type", None) == "mock" or getattr(res, "inspection_type", None) == "Inspect"


def test_create_inspection_client_exception_maps_to_database_error():
    class ExplodingClient:
        def table(self, _):
            raise RuntimeError("boom")

    db = Database()
    db.client = ExplodingClient()

    class Ins:
        def __init__(self):
            self.project_id = "p"

        def model_dump(self):
            return {"name": "N"}

    with pytest.raises(DatabaseError):
        db.create_inspection(Ins(), "profile-1")

