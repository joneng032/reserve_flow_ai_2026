from backend import database
from backend.models import CostAnalysis, ReserveAnalysis
from backend.tests.conftest import FakeClient, uuid4_str


def test_get_cost_analysis_returns_cost_analysis_model():
    proj_id = uuid4_str()
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": uuid4_str()}]})

    res = database.db.get_cost_analysis(proj_id, profile_id=uuid4_str())
    assert isinstance(res, CostAnalysis)


def test_get_reserve_analysis_returns_reserve_analysis_model():
    proj_id = uuid4_str()
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": uuid4_str()}]})

    res = database.db.get_reserve_analysis(proj_id, profile_id=uuid4_str())
    assert isinstance(res, ReserveAnalysis)
