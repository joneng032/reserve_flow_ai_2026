from backend import database
from backend.models import ComponentCreate, ComponentUpdate
from backend.tests.conftest import FakeClient, uuid4_str


def make_component_row(cid=None, proj=None, name="Comp", category="Cat", tags=None):
    return {
        "id": cid or uuid4_str(),
        "project_id": proj or uuid4_str(),
        "name": name,
        "category": category,
        "base_cost": 10,
        "useful_life": 5,
        # component_tags join shape: list of dicts with 'tag' key
        "tags": tags or [],
    }


def test_get_project_components_category_and_tag_filters():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    # Create tags and component_tag join rows
    tag_water = {"id": uuid4_str(), "name": "water", "project_id": proj_id}
    tag_safety = {"id": uuid4_str(), "name": "safety", "project_id": proj_id}

    c1 = make_component_row(name="Valve", proj=proj_id, category="Plumbing", tags=[{"tag": tag_water}])
    c2 = make_component_row(name="Gate", proj=proj_id, category="Security", tags=[{"tag": tag_safety}])
    c3 = make_component_row(name="Pipe", proj=proj_id, category="Plumbing", tags=[{"tag": tag_safety}, {"tag": tag_water}])

    fake = FakeClient({
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "components": [c1, c2, c3],
        "tags": [tag_water, tag_safety],
    })
    database.db.client = fake

    # filter by category Plumbing
    plumbing = database.db.get_project_components(project_id=proj_id, profile_id=profile_id, category="Plumbing")
    assert isinstance(plumbing, list)
    assert any(comp.name == "Valve" for comp in plumbing)
    assert any(comp.name == "Pipe" for comp in plumbing)

    # filter by tag 'water'
    water = database.db.get_project_components(project_id=proj_id, profile_id=profile_id, tag="water")
    assert isinstance(water, list)
    names = [c.name for c in water]
    assert "Valve" in names and "Pipe" in names


def test_component_tags_join_shape_and_serialization():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    tag1 = {"id": uuid4_str(), "name": "alpha", "project_id": proj_id}

    comp_row = make_component_row(proj=proj_id, name="Widget", category="Misc", tags=[{"tag": tag1}])
    fake = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "components": [comp_row], "tags": [tag1]})
    database.db.client = fake

    results = database.db.get_project_components(project_id=proj_id, profile_id=profile_id)
    assert len(results) == 1
    cwt = results[0]
    # ComponentWithTags should provide a 'tags' attribute as a list of tag dicts
    assert hasattr(cwt, "tags")
    assert isinstance(cwt.tags, list)
    # tags are returned as Pydantic Tag models; access attribute directly
    assert any(getattr(t, "name", None) == "alpha" for t in cwt.tags)


def test_update_delete_component_ownership_negative():
    proj_id = uuid4_str()
    owner = uuid4_str()
    other = uuid4_str()

    comp_id = uuid4_str()
    comp_row = make_component_row(cid=comp_id, proj=proj_id, name="Bolt", category="Fasteners")
    fake = FakeClient({"projects": [{"id": proj_id, "profile_id": owner}], "components": [comp_row]})
    database.db.client = fake

    # other profile should not be able to update
    res = database.db.update_component(comp_id, ComponentUpdate(name="Bolt V2"), other)
    assert res is None

    # other profile cannot delete either
    ok = database.db.delete_component(comp_id, other)
    assert ok is False
