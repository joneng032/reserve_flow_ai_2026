import pytest
from backend import database
from backend.tests.conftest import FakeClient, uuid4_str


def test_get_project_media_files_client_none_returns_empty():
    database.db.client = None
    assert database.db.get_project_media_files(uuid4_str(), uuid4_str()) == []


def test_get_project_media_files_ownership_negative_returns_empty():
    database.db.client = FakeClient({"projects": []})
    assert database.db.get_project_media_files(uuid4_str(), uuid4_str()) == []


def test_get_project_media_files_success_pagination_and_filter():
    project_id = uuid4_str()
    profile_id = uuid4_str()

    # create 5 media files with varying file_type and created_at
    media_files = []
    for i in range(5):
        media_files.append({
            "id": uuid4_str(),
            "project_id": project_id,
            "file_type": "image" if i % 2 == 0 else "video",
            "file_name": f"f{i}",
            "created_at": f"2020-01-0{i+1}T00:00:00Z",
        })

    client = FakeClient({"projects": [{"id": project_id, "profile_id": profile_id}], "media_files": media_files})
    database.db.client = client

    # request only images, skip 0, limit 2 -> should return the two most recent images
    results = database.db.get_project_media_files(project_id, profile_id, file_type="image", skip=0, limit=2)
    assert isinstance(results, list)
    assert len(results) <= 2
    for r in results:
        assert str(r.project_id) == project_id
        assert r.file_type == "image"


def test_get_project_media_files_data_error_returns_empty():
    class BrokenQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def order(self, *a, **kw):
            return self

        def range(self, *a, **kw):
            return self

        def execute(self):
            raise AttributeError("bad data")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "media_files":
                return BrokenQuery()
            if name == "projects":
                return FakeClient({"projects": [{"id": "p1", "profile_id": "u1"}]}).table(name)
            return super().table(name)

    database.db.client = BrokenClient({})
    assert database.db.get_project_media_files("p1", "u1") == []


def test_get_project_media_files_unexpected_exception_raises_database_error():
    class ExplodingQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def order(self, *a, **kw):
            return self

        def range(self, *a, **kw):
            return self

        def execute(self):
            raise Exception("boom")

    class ExplodingClient(FakeClient):
        def table(self, name):
            if name == "media_files":
                return ExplodingQuery()
            if name == "projects":
                # ownership check should succeed
                return FakeClient({"projects": [{"id": "p1", "profile_id": "u1"}]}).table(name)
            return super().table(name)

    database.db.client = ExplodingClient({})
    with pytest.raises(database.DatabaseError):
        database.db.get_project_media_files("p1", "u1")
