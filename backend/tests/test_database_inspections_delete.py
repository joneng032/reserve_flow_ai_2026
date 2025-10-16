from backend.database import Database


def test_delete_inspection_and_item_success():
    from backend.tests.conftest import FakeClient, uuid4_str

    insp_id = uuid4_str()
    proj_id = uuid4_str()
    client = FakeClient(table_data={
        "inspections": [{"id": insp_id, "project_id": proj_id, "projects": {"profile_id": "profile-1"}}],
        "inspection_items": [{
            "id": uuid4_str(),
            "inspection_id": insp_id,
            "item_name": "it",
            "inspections": {"project_id": proj_id, "projects": {"profile_id": "profile-1"}},
        }],
    })

    db = Database()
    db.client = client

    out = db.delete_inspection(insp_id, "profile-1")
    # FakeQuery.delete returns self and execute() returns existing _data which we normalized
    assert out is True

    item_id = client.table_data["inspection_items"][0]["id"]
    out2 = db.delete_inspection_item(item_id, "profile-1")
    assert out2 is True
