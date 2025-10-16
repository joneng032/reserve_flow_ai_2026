from backend import database
from backend.tests.conftest import FakeClient, uuid4_str
from backend.models import Evidence


def test_get_project_evidence_filter_and_pagination_success():
    proj = uuid4_str()
    profile = uuid4_str()

    # two evidence rows, different types
    e1 = {"id": uuid4_str(), "project_id": proj, "evidence_type": "photo", "file_name": "a.jpg"}
    e2 = {"id": uuid4_str(), "project_id": proj, "evidence_type": "doc", "file_name": "b.pdf"}

    client = FakeClient({"projects": [{"id": proj, "profile_id": profile}], "evidence": [e1, e2]})
    database.db.client = client

    res = database.db.get_project_evidence(proj, profile, evidence_type="photo", skip=0, limit=1)
    assert isinstance(res, list)
    assert all(isinstance(x, Evidence) for x in res)
    assert len(res) <= 1


def test_get_project_evidence_empty_when_no_evidence():
    proj = uuid4_str()
    profile = uuid4_str()
    client = FakeClient({"projects": [{"id": proj, "profile_id": profile}], "evidence": []})
    database.db.client = client
    res = database.db.get_project_evidence(proj, profile)
    assert res == []


def test_get_evidence_success_with_nested_project():
    evid = uuid4_str()
    proj = uuid4_str()
    profile = uuid4_str()

    row = {
        "id": evid,
        "project_id": proj,
        "evidence_type": "photo",
        "file_name": "x.jpg",
        "projects": {"profile_id": profile},
    }
    client = FakeClient({"evidence": [row]})
    database.db.client = client

    res = database.db.get_evidence(evid, profile)
    assert res is not None
    assert isinstance(res, Evidence)


def test_get_evidence_none_when_not_found():
    database.db.client = FakeClient({"evidence": []})
    assert database.db.get_evidence(uuid4_str(), uuid4_str()) is None
