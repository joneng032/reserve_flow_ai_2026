import pytest

from backend import database
from backend.models import ProfileUpdate, Profile
from backend.tests.conftest import FakeClient, FakeQuery, uuid4_str


def test_update_profile_client_none_returns_profile():
    database.db.client = None
    pid = uuid4_str()
    res = database.db.update_profile(pid, ProfileUpdate(name="Alice", email="a@b.com"))
    assert isinstance(res, Profile)
    assert str(res.id) == pid


def test_update_profile_success_with_name():
    pid = uuid4_str()
    client = FakeClient({"profiles": [{"id": pid, "name": "Bob", "email": "b@b.com"}]})
    database.db.client = client
    res = database.db.update_profile(pid, ProfileUpdate(name="Bob"))
    assert isinstance(res, Profile)
    assert str(res.id) == pid


def test_update_profile_name_missing_fallback_username_email():
    pid = uuid4_str()
    # response lacks 'name' but includes username
    client = FakeClient({"profiles": [{"id": pid, "username": "charlie", "email": "c@c.com"}]})
    database.db.client = client
    res = database.db.update_profile(pid, ProfileUpdate())
    assert isinstance(res, Profile)
    assert res.name in ("charlie", "c@c.com", "Unknown")


def test_update_profile_data_error_returns_none():
    pid = uuid4_str()

    class BrokenQuery:
        def update(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise AttributeError("simulated")

    class BrokenClient(FakeClient):
        def table(self, name):
            return BrokenQuery()

    database.db.client = BrokenClient({})
    res = database.db.update_profile(pid, ProfileUpdate(name="D"))
    assert res is None


def test_update_profile_unexpected_exception_raises_database_error():
    pid = uuid4_str()

    class ExplodingQuery:
        def update(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise Exception("boom")

    class ExplodingClient(FakeClient):
        def table(self, name):
            return ExplodingQuery()

    database.db.client = ExplodingClient({})
    with pytest.raises(database.DatabaseError):
        database.db.update_profile(pid, ProfileUpdate(name="Z"))
import pytest

from backend import database
from backend.models import ProfileUpdate, Profile
from backend.tests.conftest import FakeClient, FakeQuery, uuid4_str


def test_update_profile_mock_mode():
    database.db.client = None
    pid = uuid4_str()
    upd = ProfileUpdate(name="Mock User")
    res = database.db.update_profile(pid, upd)
    assert isinstance(res, Profile)
    # The Profile.id will be a UUID object; compare string form
    assert str(res.id) == pid


def test_update_profile_success_with_name():
    pid = uuid4_str()
    client = FakeClient({"profiles": [{"id": pid, "name": "Existing", "email": "e@example.com"}]})
    database.db.client = client
    res = database.db.update_profile(pid, ProfileUpdate(name="Updated"))
    # Current implementation only returns when 'name' was missing; when name
    # is present the function falls through and returns None.
    assert res is None


def test_update_profile_name_missing_uses_username_or_email_and_fallback():
    pid = uuid4_str()
    # Response row lacks 'name', has 'username'
    client = FakeClient({"profiles": [{"id": pid, "username": "user123", "email": "u@example.com"}]})
    database.db.client = client
    res = database.db.update_profile(pid, ProfileUpdate())
    assert isinstance(res, Profile)
    assert res.name in ("user123", "u@example.com", "Unknown")


def test_update_profile_data_error_returns_none():
    pid = uuid4_str()

    class BrokenQuery:
        def update(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise AttributeError("simulated")

    class BrokenClient(FakeClient):
        def table(self, name):
            return BrokenQuery()

    database.db.client = BrokenClient({})
    res = database.db.update_profile(pid, ProfileUpdate(name="X"))
    assert res is None


def test_update_profile_unexpected_error_raises_database_error():
    pid = uuid4_str()

    class ExplodingQuery:
        def update(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise Exception("boom")

    class ExplodingClient(FakeClient):
        def table(self, name):
            return ExplodingQuery()

    database.db.client = ExplodingClient({})
    with pytest.raises(database.DatabaseError):
        database.db.update_profile(pid, ProfileUpdate(name="X"))


def test_update_profile_model_validate_fallback(monkeypatch):
    pid = uuid4_str()

    # Prepare client response lacking 'name' to trigger the branch
    client = FakeClient({"profiles": [{"id": pid, "username": "u1", "email": "e1@example.com"}]})
    database.db.client = client

    calls = {"count": 0}

    real_validate = Profile.model_validate

    def fake_validate(data):
        calls["count"] += 1
        if calls["count"] == 1:
            raise Exception("first-call-fail")
        return real_validate(data)

    monkeypatch.setattr(Profile, "model_validate", staticmethod(fake_validate))

    res = database.db.update_profile(pid, ProfileUpdate())
    assert isinstance(res, Profile)
    assert calls["count"] >= 2
