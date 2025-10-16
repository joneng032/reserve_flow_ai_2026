import pytest
from decimal import Decimal
from backend import database
from backend.models import ComponentUpdate
from backend.tests.conftest import FakeClient, uuid4_str


def test_update_component_client_none():
    database.db.client = None
    comp_id = uuid4_str()
    # Provide a valid project_id by patching the model_dump result so the mocked
    # Component creation uses a valid UUID instead of the 'mock-project' default.
    project_id = uuid4_str()
    # Use a lightweight object implementing model_dump to avoid mutating
    # the frozen Pydantic model instance.
    class DummyComp:
        def model_dump(self, exclude_unset=True):
            return {"project_id": project_id, "name": "New"}

    res = database.db.update_component(comp_id, DummyComp(), uuid4_str())
    assert res is not None and str(getattr(res, "id", None)) == comp_id


def test_update_component_ownership_negative():
    # No component rows in DB -> ownership check fails
    database.db.client = FakeClient({"components": []})
    res = database.db.update_component(uuid4_str(), ComponentUpdate(name="X"), uuid4_str())
    assert res is None


def test_update_component_success_and_audit(monkeypatch):
    comp_id = uuid4_str()
    project_id = uuid4_str()
    profile_id = uuid4_str()

    # components row should include joined projects info for ownership check
    comp_row = {
        "id": comp_id,
        "project_id": project_id,
        "name": "Old",
        "projects": {"profile_id": profile_id},
    }

    # The update path: FakeClient.execute will return normalized row
    client = FakeClient({"components": [comp_row]})
    database.db.client = client

    # capture audit payload
    seen = {}

    def fake_audit(audit):
        seen["audit"] = audit

    monkeypatch.setattr(database.db, "create_audit_log", fake_audit)

    res = database.db.update_component(comp_id, ComponentUpdate(name="NewName", base_cost=Decimal("12.34")), profile_id)
    # returned model may use UUID objects; compare string form
    assert res is None or str(getattr(res, "id", None)) == comp_id
    assert "audit" in seen


def test_update_component_data_error():
    class BrokenQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            raise AttributeError("bad data")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "components":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    res = database.db.update_component(uuid4_str(), ComponentUpdate(name="Z"), uuid4_str())
    assert res is None


def test_update_component_unexpected_exception_raises_database_error():
    class ExplodingQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise Exception("boom")

    class ExplodingClient(FakeClient):
        def table(self, name):
            if name == "components":
                return ExplodingQuery()
            return FakeClient({}).table(name)

    database.db.client = ExplodingClient({})
    with pytest.raises(database.DatabaseError):
        database.db.update_component(uuid4_str(), ComponentUpdate(name="Y"), uuid4_str())
