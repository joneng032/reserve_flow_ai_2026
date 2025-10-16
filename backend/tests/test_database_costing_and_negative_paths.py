from backend import database
from backend.tests.conftest import FakeClient, uuid4_str


def test_get_cost_analysis_mock_mode_defaults():
    # mock mode (no client) should return zeros
    database.db.client = None
    res = database.db.get_cost_analysis("no-project", "p1")
    assert res.total_components == 0
    assert res.total_value == 0


def test_get_reserve_analysis_no_project_returns_defaults():
    pid = uuid4_str()
    # seed empty client (no project row)
    database.db.client = FakeClient({"projects": [], "components": []})
    res = database.db.get_reserve_analysis(pid, "p1")
    assert res.percent_funded == 0
    assert res.total_reserve_balance == 0


def test_create_component_ownership_failure_returns_none():
    pid = uuid4_str()
    # projects table doesn't include project for profile 'p1'
    database.db.client = FakeClient({"projects": [{"id": pid, "profile_id": "other"}], "components": []})
    comp = database.db.create_component(type("X", (), {"project_id": pid, "name": "C"})(), "p1")
    # when ownership check fails, create_component should return None
    assert comp is None


def test_delete_project_mock_mode_returns_false():
    # when client is None (mock mode), delete_project should return False
    database.db.client = None
    ok = database.db.delete_project("nonexistent", "p1")
    assert ok is False
