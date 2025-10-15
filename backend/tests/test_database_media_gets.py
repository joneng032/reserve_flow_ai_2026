from backend.database import Database


def test_get_project_media_files_with_file_type_filter():
    from backend.tests.conftest import FakeClient, uuid4_str

    pid = uuid4_str()
    m1 = {"id": uuid4_str(), "project_id": pid, "file_type": "image", "file_name": "a.jpg"}
    m2 = {"id": uuid4_str(), "project_id": pid, "file_type": "video", "file_name": "b.mp4"}

    client = FakeClient(table_data={
        "projects": [{"id": pid, "profile_id": "profile-1"}],
        "media_files": [m1, m2],
    })

    db = Database()
    db.client = client

    imgs = db.get_project_media_files(pid, "profile-1", file_type="image")
    assert len(imgs) == 1
    assert getattr(imgs[0], "file_type", None) == "image"


def test_get_media_file_success():
    from backend.tests.conftest import FakeClient, uuid4_str

    mid = uuid4_str()
    pid = uuid4_str()
    client = FakeClient(table_data={
        "media_files": [{"id": mid, "project_id": pid, "file_name": "x.jpg", "projects": {"profile_id": "profile-1"}}],
    })

    db = Database()
    db.client = client

    got = db.get_media_file(mid, "profile-1")
    assert got is not None
    assert getattr(got, "id", None) is not None
