import pytest

from backend import database
from backend.tests.conftest import FakeClient, uuid4_str


def test_delete_component_ownership_failure_returns_false():
    # component exists but project ownership does not match
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    comp_id = uuid4_str()

    table_data = {
        # project exists but with different profile_id
        "projects": [{"id": proj_id, "profile_id": uuid4_str()}],
        "components": [{"id": comp_id, "project_id": proj_id, "name": "N"}],
    }

    database.db.client = FakeClient(table_data)

    ok = database.db.delete_component(comp_id, profile_id)
    assert ok is False


def test_delete_inspection_item_ownership_failure_returns_false():
    insp_id = uuid4_str()
    profile_id = uuid4_str()
    item_id = uuid4_str()

    table_data = {
        "inspections": [{"id": insp_id, "project_id": uuid4_str(), "profile_id": uuid4_str()}],
        "inspection_items": [{"id": item_id, "inspection_id": insp_id}],
    }

    database.db.client = FakeClient(table_data)

    ok = database.db.delete_inspection_item(item_id, profile_id)
    assert ok is False


def test_delete_evidence_ownership_failure_returns_false():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    ev_id = uuid4_str()

    table_data = {
        "projects": [{"id": proj_id, "profile_id": uuid4_str()}],
        "evidence": [{"id": ev_id, "project_id": proj_id}],
    }

    database.db.client = FakeClient(table_data)

    ok = database.db.delete_evidence(ev_id, profile_id)
    assert ok is False


def test_client_exception_wrapped_as_databaseerror():
    # Simulate client.execute raising an exception for get_project
    class BadClient(FakeClient):
        class BadQuery:
            def select(self, *a, **kw):
                return self

            def eq(self, *a, **kw):
                return self

            def range(self, *a, **kw):
                return self

            def order(self, *a, **kw):
                return self

            def execute(self):
                raise RuntimeError("client failure")

        def table(self, name):
            return BadClient.BadQuery()

    # Replace client temporarily and ensure we restore the original client
    orig_client = getattr(database.db, "client", None)
    try:
        database.db.client = BadClient({})

        with pytest.raises(database.DatabaseError):
            # get_projects calls .execute internally and should raise DatabaseError
            database.db.get_projects(uuid4_str())
    finally:
        database.db.client = orig_client
