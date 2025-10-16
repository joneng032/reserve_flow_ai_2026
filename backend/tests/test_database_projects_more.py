from types import SimpleNamespace

import pytest

from backend.database import Database, DatabaseError


def test_get_profile_client_exception_maps_to_database_error():
    class ExplodingClient:
        def table(self, _):
            raise RuntimeError("boom")

    db = Database()
    db.client = ExplodingClient()

    with pytest.raises(DatabaseError):
        db.get_profile("p1")


def test_create_and_update_profile_mock_mode():
    from backend.tests.conftest import uuid4_str

    db = Database()
    db.client = None

    class PC:
        def __init__(self):
            self.name = "Alice"
            self.email = "alice@example.com"

    prof = db.create_profile(PC())
    assert prof is not None
    assert getattr(prof, "name", None) == "Alice"

    class U:
        def model_dump(self, exclude_unset=True):
            return {"name": "Alice Updated"}

    updated = db.update_profile(uuid4_str(), U())
    assert updated is not None
    assert getattr(updated, "name", None) == "Alice Updated"


def test_get_projects_calculates_counts_and_totals():
    from backend.tests.conftest import FakeClient, uuid4_str

    pid = uuid4_str()

    from backend.tests.conftest import uuid4_str as _uuid
    profile = _uuid()

    # project row contains nested components and categories as expected by get_projects
    project_row = {
        "id": pid,
        "profile_id": profile,
        "name": "Proj",
        "components": [{"base_cost": 100}, {"base_cost": 200}],
        "categories": [{"id": _uuid(), "name": "Cat1", "project_id": pid}],
    }

    client = FakeClient(table_data={
        "projects": [project_row],
    })

    db = Database()
    db.client = client

    projs = db.get_projects(profile)
    assert isinstance(projs, list)
    assert len(projs) == 1
    p = projs[0]
    assert getattr(p, "components_count", None) == 2
    assert getattr(p, "total_value", None) == 300


def test_get_cost_analysis_computes_breakdown():
    from backend.tests.conftest import FakeClient, uuid4_str

    proj_id = uuid4_str()

    client = FakeClient(table_data={
        "projects": [{"id": proj_id, "profile_id": "profile-1"}],
        "components": [
            {"project_id": proj_id, "base_cost": 100, "category": "A"},
            {"project_id": proj_id, "base_cost": 50, "category": "B"},
            {"project_id": proj_id, "base_cost": 50, "category": "A"},
        ],
    })

    db = Database()
    db.client = client

    analysis = db.get_cost_analysis(proj_id, "profile-1")
    assert getattr(analysis, "total_components", None) == 3
    assert getattr(analysis, "total_value", None) == 200
    # average_cost may be a float
    # average_cost may be Decimal; coerce to float for comparison
    assert abs(float(getattr(analysis, "average_cost", 0)) - (200 / 3)) < 0.001
    br = getattr(analysis, "categories_breakdown", {})
    assert br.get("A", {}).get("count") == 2
    assert br.get("A", {}).get("total_value") == 150
