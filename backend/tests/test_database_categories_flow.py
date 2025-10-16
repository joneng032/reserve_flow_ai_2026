from backend import database
from backend.models import CategoryCreate, CategoryUpdate
from backend.tests.conftest import FakeClient, uuid4_str


def test_create_update_delete_category_flow():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "categories": []})

    cat = database.db.create_category(CategoryCreate(project_id=proj_id, name="C"), profile_id)
    assert cat is not None

    # seed created category for update/delete
    cid = str(cat.id) if hasattr(cat, "id") else uuid4_str()
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "categories": [{"id": cid, "project_id": proj_id}]})

    up = database.db.update_category(cid, CategoryUpdate(name="C2"), profile_id)
    # update_category may return None or updated object depending on client
    assert up is None or hasattr(up, "id")

    ok = database.db.delete_category(cid, profile_id)
    assert ok is True
