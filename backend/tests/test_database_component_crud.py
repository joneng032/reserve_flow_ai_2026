from backend import database
from backend.models import ComponentCreate, ComponentUpdate
from backend.tests.conftest import FakeClient, uuid4_str


def test_create_component_with_client_inserts_and_returns_component():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    # client has a project owned by profile_id
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "components": []})

    comp_data = ComponentCreate(project_id=proj_id, name="Bench", category="park", base_cost=50, useful_life=5)
    comp = database.db.create_component(comp_data, profile_id)
    assert comp is not None
    # Component.project_id may be a UUID object; compare as string
    assert str(comp.project_id) == proj_id


def test_update_component_owner_mismatch_returns_none():
    comp_id = uuid4_str()
    proj_id = uuid4_str()
    # component exists but project owned by other profile
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": uuid4_str()}], "components": [{"id": comp_id, "project_id": proj_id}]})

    updated = database.db.update_component(comp_id, ComponentUpdate(name="New"), profile_id=uuid4_str())
    assert updated is None


def test_delete_component_returns_true_when_owner():
    comp_id = uuid4_str()
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "components": [{"id": comp_id, "project_id": proj_id}]})

    ok = database.db.delete_component(comp_id, profile_id)
    assert ok is True
