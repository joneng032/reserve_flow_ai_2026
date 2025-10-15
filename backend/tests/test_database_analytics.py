from backend.database import Database


def test_get_cost_analysis_empty_and_with_components():
    from backend.tests.conftest import FakeClient, uuid4_str

    pid = uuid4_str()

    # empty components
    client = FakeClient(table_data={
        "projects": [{"id": pid, "profile_id": "profile-1"}],
        "components": [],
    })
    db = Database()
    db.client = client

    ca = db.get_cost_analysis(pid, "profile-1")
    assert ca.total_components == 0

    # with components
    c1 = {"id": uuid4_str(), "project_id": pid, "base_cost": 100}
    c2 = {"id": uuid4_str(), "project_id": pid, "base_cost": 300}
    client2 = FakeClient(table_data={
        "projects": [{"id": pid, "profile_id": "profile-1"}],
        "components": [c1, c2],
    })
    db2 = Database()
    db2.client = client2
    ca2 = db2.get_cost_analysis(pid, "profile-1")
    assert ca2.total_components == 2
    assert ca2.total_value >= 400


def test_get_reserve_analysis_various():
    from backend.tests.conftest import FakeClient, uuid4_str

    pid = uuid4_str()
    # project with reserve and components
    proj = {"id": pid, "profile_id": "profile-1", "current_reserve_balance": 200}
    c1 = {"id": uuid4_str(), "project_id": pid, "base_cost": 100}
    c2 = {"id": uuid4_str(), "project_id": pid, "base_cost": 300}

    client = FakeClient(table_data={
        "projects": [proj],
        "components": [c1, c2],
    })

    db = Database()
    db.client = client
    ra = db.get_reserve_analysis(pid, "profile-1")
    assert ra.total_reserve_balance >= 0
    assert isinstance(ra.recommendations, list)
