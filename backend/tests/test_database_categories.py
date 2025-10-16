import pytest

from backend.database import Database, DatabaseError


def test_get_project_categories_client_mode_returns_list():
    from backend.tests.conftest import FakeClient, uuid4_str

    pid = uuid4_str()
    cat_id = uuid4_str()

    client = FakeClient(table_data={
        "projects": [{"id": pid, "profile_id": "profile-1"}],
        "categories": [{"id": cat_id, "project_id": pid, "name": "C1"}],
    })

    db = Database()
    db.client = client

    cats = db.get_project_categories(pid, "profile-1")
    assert isinstance(cats, list)
    assert len(cats) == 1
    assert getattr(cats[0], "name", None) == "C1"


def test_create_category_client_mode_success():
    from backend.tests.conftest import FakeClient, uuid4_str
    from backend.models import CategoryCreate

    pid = uuid4_str()

    client = FakeClient(table_data={
        "projects": [{"id": pid, "profile_id": "profile-1"}],
        "categories": [],
    })

    db = Database()
    db.client = client

    class CC:
        def __init__(self):
            self.project_id = pid
            self.name = "NewCat"

        def model_dump(self):
            return {"project_id": self.project_id, "name": self.name}

    created = db.create_category(CC(), "profile-1")
    assert created is not None
    assert getattr(created, "name", None) == "NewCat"


def test_get_project_categories_client_exception_maps_to_database_error():
    class ExplodingClient:
        def table(self, _):
            raise RuntimeError("boom")

    db = Database()
    db.client = ExplodingClient()

    with pytest.raises(DatabaseError):
        db.get_project_categories("p", "profile-1")
