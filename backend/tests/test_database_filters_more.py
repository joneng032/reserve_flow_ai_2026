from backend import database
from backend.tests.conftest import FakeClient, uuid4_str


def test_get_project_components_filters_by_category_and_tag():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    # components: two components, one with tag 'pool' embedded in tags structure
    comp1 = {"id": uuid4_str(), "project_id": proj_id, "name": "A", "category": "roof"}
    comp2 = {
        "id": uuid4_str(),
        "project_id": proj_id,
        "name": "B",
        "category": "pool",
        # Tag objects need a project_id to satisfy the Tag model
        "tags": [{"tag": {"name": "water", "project_id": proj_id}}],
    }

    table_data = {"projects": [{"id": proj_id, "profile_id": profile_id}], "components": [comp1, comp2]}
    database.db.client = FakeClient(table_data)

    res_cat = database.db.get_project_components(proj_id, profile_id, category="pool")
    assert len(res_cat) == 1
    assert res_cat[0].category == "pool"

    # Tag filter: using tag name should match component with nested tag
    res_tag = database.db.get_project_components(proj_id, profile_id, tag="water")
    assert len(res_tag) == 1
    # tags are Pydantic Tag models; access via attribute
    assert any(getattr(t, "name", None) == "water" for t in res_tag[0].tags)


def test_get_project_media_files_filters_and_ownership():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    m1 = {"id": uuid4_str(), "project_id": proj_id, "file_name": "a.jpg", "file_type": "image"}
    m2 = {"id": uuid4_str(), "project_id": proj_id, "file_name": "b.pdf", "file_type": "document"}

    table_data = {"projects": [{"id": proj_id, "profile_id": profile_id}], "media_files": [m1, m2]}
    database.db.client = FakeClient(table_data)

    imgs = database.db.get_project_media_files(proj_id, profile_id, file_type="image")
    assert len(imgs) == 1
    assert imgs[0].file_type == "image"

    # ownership failure: wrong profile should return empty
    other_profile = uuid4_str()
    empty = database.db.get_project_media_files(proj_id, other_profile)
    assert empty == []


def test_get_project_evidence_filters_and_ownership():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    e1 = {"id": uuid4_str(), "project_id": proj_id, "evidence_type": "photo"}
    e2 = {"id": uuid4_str(), "project_id": proj_id, "evidence_type": "video"}

    table_data = {"projects": [{"id": proj_id, "profile_id": profile_id}], "evidence": [e1, e2]}
    database.db.client = FakeClient(table_data)

    photos = database.db.get_project_evidence(proj_id, profile_id, evidence_type="photo")
    assert len(photos) == 1
    assert photos[0].evidence_type == "photo"
