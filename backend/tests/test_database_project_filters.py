from backend import database
from backend.tests.conftest import FakeClient, uuid4_str


def test_get_project_components_mock_mode_returns_list():
    db = database.Database()
    comps = db.get_project_components("pid", "profile-1")
    assert isinstance(comps, list)


def test_get_project_media_files_file_type_filter():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    media = [
        {"id": uuid4_str(), "project_id": proj_id, "file_type": "image"},
        {"id": uuid4_str(), "project_id": proj_id, "file_type": "pdf"},
    ]
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "media_files": media})

    res = database.db.get_project_media_files(proj_id, profile_id, file_type="image")
    assert len(res) == 1
    assert res[0].file_type == "image"


def test_get_project_evidence_filter():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    ev = [{"id": uuid4_str(), "project_id": proj_id, "evidence_type": "image"}, {"id": uuid4_str(), "project_id": proj_id, "evidence_type": "pdf"}]
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "evidence": ev})
    res = database.db.get_project_evidence(proj_id, profile_id, evidence_type="pdf")
    assert len(res) == 1
    assert res[0].evidence_type == "pdf"
