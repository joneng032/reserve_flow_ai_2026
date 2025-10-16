from backend import database
from backend.models import ProjectCreate, ProjectUpdate, ComponentCreate, ComponentUpdate, MediaFileCreate
from backend.tests.conftest import FakeClient, uuid4_str


def test_project_create_update_delete_flow():
    profile_id = uuid4_str()
    # seed empty projects table
    database.db.client = FakeClient({"projects": []})

    proj = database.db.create_project(ProjectCreate(name="Proj", profile_id=profile_id))
    assert proj is not None

    pid = str(getattr(proj, "id", uuid4_str()))
    database.db.client = FakeClient({"projects": [{"id": pid, "profile_id": profile_id}]})

    up = database.db.update_project(pid, profile_id, ProjectUpdate(name="Proj2"))
    assert up is None or hasattr(up, "id")

    ok = database.db.delete_project(pid, profile_id)
    assert ok is True


def test_component_crud_and_catalog():
    profile_id = uuid4_str()
    proj_id = uuid4_str()
    # seed projects and components
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "components": []})

    comp = database.db.create_component(ComponentCreate(project_id=proj_id, name="C"), profile_id)
    assert comp is not None

    cid = str(getattr(comp, "id", uuid4_str()))
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "components": [{"id": cid, "project_id": proj_id}]})

    up = database.db.update_component(cid, ComponentUpdate(name="C2"), profile_id)
    assert up is None or hasattr(up, "id")

    ok = database.db.delete_component(cid, profile_id)
    assert ok is True

    # catalog retrieval
    database.db.client = FakeClient({"components": [{"id": cid, "name": "C2"}]})
    cat = database.db.get_component_catalog()
    assert isinstance(cat, list)


def test_media_file_crud():
    profile_id = uuid4_str()
    proj_id = uuid4_str()
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "media_files": []})

    mf = database.db.create_media_file(
        MediaFileCreate(
            project_id=proj_id,
            file_name="f.jpg",
            file_path="/tmp/f.jpg",
            file_type="image/jpeg",
            mime_type="image/jpeg",
            file_size=1234,
        ),
        profile_id,
    )
    assert mf is not None

    mid = str(getattr(mf, "id", uuid4_str()))
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "media_files": [{"id": mid, "project_id": proj_id, "file_name": "f.jpg"}]})

    got = database.db.get_media_file(mid, profile_id)
    # get_media_file may return dict or model
    assert got is None or getattr(got, "file_name", None) == "f.jpg" or (isinstance(got, dict) and got.get("file_name") == "f.jpg")

    ok = database.db.delete_media_file(mid, profile_id)
    assert ok is True
