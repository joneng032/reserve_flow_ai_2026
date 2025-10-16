from backend import database
from backend.models import ComponentCreate
from backend.tests.conftest import FakeClient, uuid4_str


def test_create_component_mock_mode_returns_component():
    db = database.Database()
    # In mock mode (no client) create_component returns a Component object
    comp = db.create_component(ComponentCreate(project_id=uuid4_str(), name="X", category="test", base_cost=100, useful_life=10), profile_id=uuid4_str())
    assert comp is not None
    assert hasattr(comp, "id")


def test_get_project_components_filters_by_category_and_tag():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    # components with tags shaped as the client returns
    components = [
        {"id": uuid4_str(), "project_id": proj_id, "category": "pool", "base_cost": 10, "tags": [{"tag": {"id": uuid4_str(), "project_id": proj_id, "name": "water"}}]},
        {"id": uuid4_str(), "project_id": proj_id, "category": "deck", "base_cost": 20, "tags": [{"tag": {"id": uuid4_str(), "project_id": proj_id, "name": "wood"}}]},
    ]
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "components": components})

    res_cat = database.db.get_project_components(proj_id, profile_id, category="pool")
    assert len(res_cat) == 1
    assert res_cat[0].category == "pool"

    res_tag = database.db.get_project_components(proj_id, profile_id, tag="wood")
    assert len(res_tag) == 1
    # Tag may be a pydantic model or a dict depending on FakeClient normalization
    first_tag = res_tag[0].tags[0]
    tag_name = getattr(first_tag, "name", None) or (first_tag.get("name") if isinstance(first_tag, dict) else None)
    assert tag_name == "wood"
