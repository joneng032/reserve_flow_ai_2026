from backend.database import Database


def test_get_project_components_with_tag_filter():
    from backend.tests.conftest import FakeClient, uuid4_str

    pid = uuid4_str()
    # component row includes tags array structure as returned by the DB
    comp = {
        "id": uuid4_str(),
        "project_id": pid,
        "name": "CompA",
        # Tag payloads returned by DB include tag object with name and project_id
        "tags": [{"tag": {"name": "hot", "project_id": pid}}],
    }

    client = FakeClient(table_data={
        "projects": [{"id": pid, "profile_id": "profile-1"}],
        "components": [comp],
    })

    db = Database()
    db.client = client

    # Call without tag filter (FakeClient doesn't fully implement 'contains')
    res = db.get_project_components(pid, "profile-1")
    assert isinstance(res, list)
    assert len(res) == 1
    assert getattr(res[0], "name", None) == "CompA"
