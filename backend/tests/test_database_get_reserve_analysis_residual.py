import pytest
from backend import database
from backend.tests.conftest import FakeClient, uuid4_str


def test_get_reserve_analysis_client_none():
    database.db.client = None
    res = database.db.get_reserve_analysis(uuid4_str(), uuid4_str())
    assert res.total_reserve_balance == 0


def test_get_reserve_analysis_missing_project():
    database.db.client = FakeClient({"projects": []})
    res = database.db.get_reserve_analysis(uuid4_str(), uuid4_str())
    assert res.total_reserve_balance == 0


def test_get_reserve_analysis_normal(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    rows = {"projects": [{"id": proj_id, "profile_id": profile_id, "current_reserve_balance": 500}]}
    database.db.client = FakeClient(rows)

    class CostAnalysis:
        def __init__(self, total_value, total_components):
            self.total_value = total_value
            self.total_components = total_components

    monkeypatch.setattr(database.db, "get_cost_analysis", lambda p, q: CostAnalysis(1000, 5), raising=False)
    res = database.db.get_reserve_analysis(proj_id, profile_id)
    assert res.total_reserve_balance == 500
    assert res.total_liability == 1000


def test_get_reserve_analysis_zero_components(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    rows = {"projects": [{"id": proj_id, "profile_id": profile_id, "current_reserve_balance": 0}]}
    database.db.client = FakeClient(rows)

    class CostAnalysis:
        def __init__(self, total_value, total_components):
            self.total_value = total_value
            self.total_components = total_components

    monkeypatch.setattr(database.db, "get_cost_analysis", lambda p, q: CostAnalysis(0, 0), raising=False)
    res = database.db.get_reserve_analysis(proj_id, profile_id)
    assert "Add components" in " ".join(res.recommendations) or res.total_liability == 0


def test_get_reserve_analysis_data_error(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    rows = {"projects": [{"id": proj_id, "profile_id": profile_id, "current_reserve_balance": "bad"}]}
    database.db.client = FakeClient(rows)

    # cause get_cost_analysis to raise a ValueError
    def bad_cost(p, q):
        raise ValueError("boom")

    monkeypatch.setattr(database.db, "get_cost_analysis", bad_cost, raising=False)
    res = database.db.get_reserve_analysis(proj_id, profile_id)
    assert res.total_reserve_balance == 0 or "Error calculating analysis" in res.recommendations


def test_get_reserve_analysis_unexpected_exception_raises_database_error(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    rows = {"projects": [{"id": proj_id, "profile_id": profile_id, "current_reserve_balance": 0}]}
    database.db.client = FakeClient(rows)

    def explode(p, q):
        raise Exception("boom")

    monkeypatch.setattr(database.db, "get_cost_analysis", explode, raising=False)
    with pytest.raises(database.DatabaseError):
        database.db.get_reserve_analysis(proj_id, profile_id)
