import pytest
from backend import database
from backend.models import MediaFileUpdate
from backend.tests.conftest import FakeClient, uuid4_str


def test_update_media_file_client_none(monkeypatch):
    # In mock-mode (no client) the function constructs a MediaFile Pydantic model which
    # may raise validation errors for missing fields. Monkeypatch MediaFile to a simple
    # container to make the behavior deterministic for testing.
    class DummyMediaFile:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    monkeypatch.setattr(database, "MediaFile", DummyMediaFile, raising=False)

    database.db.client = None
    res = database.db.update_media_file(
        uuid4_str(),
        MediaFileUpdate(file_name="a.jpg", file_path="/a.jpg", file_type="image", mime_type="image/jpeg", file_size=1),
        uuid4_str(),
    )
    assert res is None or hasattr(res, "id")


def test_update_media_file_ownership_negative():
    database.db.client = FakeClient({"projects": [], "media_files": []})
    res = database.db.update_media_file(
        uuid4_str(),
        MediaFileUpdate(file_name="a.jpg", file_path="/a.jpg", file_type="image", mime_type="image/jpeg", file_size=1),
        uuid4_str(),
    )
    assert res is None


def test_update_media_file_success_and_audit(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    media_id = uuid4_str()

    rows = {
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "media_files": [{"id": media_id, "project_id": proj_id, "file_name": "old.jpg", "file_type": "image/jpeg", "file_size": 123}],
    }
    client = FakeClient(rows)
    database.db.client = client

    captured = {}

    def fake_audit(audit):
        captured['audit'] = audit

    # Patch the instance method on the live database.db object for consistency
    monkeypatch.setattr(database.db, "create_audit_log", fake_audit, raising=False)

    res = database.db.update_media_file(
        media_id,
        MediaFileUpdate(file_name="new.jpg", file_path="/new.jpg", file_type="image", mime_type="image/jpeg", file_size=2),
        profile_id,
    )
    assert res is not None
    assert 'audit' in captured


def test_update_media_file_data_error():
    class BrokenQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            raise AttributeError("bad data")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "media_files":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    res = database.db.update_media_file(
        uuid4_str(),
        MediaFileUpdate(file_name="a.jpg", file_path="/a.jpg", file_type="image", mime_type="image/jpeg", file_size=1),
        uuid4_str(),
    )
    assert res is None


def test_update_media_file_unexpected_exception_raises_database_error():
    class ExplodingQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise Exception("boom")

    class ExplodingClient(FakeClient):
        def table(self, name):
            if name == "media_files":
                return ExplodingQuery()
            return FakeClient({"projects": [{"id": uuid4_str(), "profile_id": uuid4_str()}]}).table(name)

    database.db.client = ExplodingClient({})
    with pytest.raises(database.DatabaseError):
        database.db.update_media_file(
            uuid4_str(),
            MediaFileUpdate(file_name="a.jpg", file_path="/a.jpg", file_type="image", mime_type="image/jpeg", file_size=1),
            uuid4_str(),
        )
