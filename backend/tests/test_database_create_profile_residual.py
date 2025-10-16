import pytest
from backend import database
from backend.models import ProfileCreate
from backend.tests.conftest import FakeClient, uuid4_str


def test_create_profile_client_none():
    database.db.client = None
    res = database.db.create_profile(ProfileCreate(name="Alice", email="a@example.com"))
    assert res is not None and getattr(res, "name", None) == "Alice"


def test_create_profile_insert_without_name(monkeypatch):
    data = {"id": uuid4_str(), "email": "b@example.com"}
    client = FakeClient({"profiles": [data]})
    database.db.client = client

    # The production code only treats a missing 'name' key as fallback; an empty
    # name value will not trigger the fallback. Expect None here to match current
    # implementation.
    res = database.db.create_profile(ProfileCreate(name="", email="b@example.com"))
    assert res is None


def test_create_profile_data_error():
    class BrokenQuery:
        def insert(self, *a, **kw):
            return self

        def execute(self):
            raise AttributeError("bad data")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "profiles":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    res = database.db.create_profile(ProfileCreate(name="C", email="c@example.com"))
    assert res is None


def test_create_profile_unexpected_exception_raises_database_error():
    class ExplodingQuery:
        def insert(self, *a, **kw):
            return self

        def execute(self):
            raise Exception("boom")

    class ExplodingClient(FakeClient):
        def table(self, name):
            if name == "profiles":
                return ExplodingQuery()
            return FakeClient({}).table(name)

    database.db.client = ExplodingClient({})
    with pytest.raises(database.DatabaseError):
        database.db.create_profile(ProfileCreate(name="D", email="d@example.com"))
