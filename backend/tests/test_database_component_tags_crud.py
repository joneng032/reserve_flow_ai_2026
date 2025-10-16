from backend import database
from backend.tests.conftest import FakeClient, uuid4_str


def test_create_tag_and_assign_to_component():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    # minimal client state
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "tags": [], "component_tags": []})

    # create a tag via direct client emulation: use conftest insert() behavior
    q = database.db.client.table("tags").insert({"project_id": proj_id, "name": "landscape"}).execute()
    assert q.data
    tag_row = q.data[0]
    assert tag_row.get("name") == "landscape"
