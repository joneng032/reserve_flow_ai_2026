from backend import database
from backend.tests.conftest import FakeClient, uuid4_str


def test_delete_category_requires_ownership_and_returns_true():
    cat_id = "cat-1"
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    # project owned by profile_id
    database.db.client = FakeClient({
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "categories": [{"id": cat_id, "project_id": proj_id}],
    })

    ok = database.db.delete_category(cat_id, profile_id)
    assert ok is True


def test_delete_category_fails_when_not_owner():
    cat_id = "cat-2"
    proj_id = uuid4_str()
    database.db.client = FakeClient({
        "projects": [{"id": proj_id, "profile_id": uuid4_str()}],
        "categories": [{"id": cat_id, "project_id": proj_id}],
    })

    ok = database.db.delete_category(cat_id, "some-other-profile")
    assert ok is False
