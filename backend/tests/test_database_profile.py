"""Tests for Database profile-related methods in `backend.database`.

These tests exercise mock-mode behavior, mapping of client responses to
Pydantic models, and error normalization into DatabaseError.
"""
from types import SimpleNamespace

import pytest

from backend.database import Database, DatabaseError


def test_get_profile_mock_mode_returns_profile(monkeypatch):
    # Ensure environment leads Database to run in mock-mode (client None)
    db = Database()
    db.client = None

    profile = db.get_profile("550e8400-e29b-41d4-a716-446655440000")
    assert profile is not None
    assert str(profile.id) == "550e8400-e29b-41d4-a716-446655440000"
    assert profile.email == "user@example.com"


def test_create_profile_mock_mode_returns_profile():
    db = Database()
    db.client = None

    class P:
        def __init__(self):
            self.name = "New User"
            self.email = "new@example.com"

    profile = db.create_profile(P())
    assert profile is not None
    assert profile.email == "new@example.com"


def test_get_profile_client_returns_data(monkeypatch):
    # Simulate a supabase client response with data list containing a dict
    class FakeResp:
        def __init__(self, data):
            self.data = data

    class FakeClient:
        def table(self, _):
            return self

        def select(self, _):
            return self

        def eq(self, _k, _v):
            return self

        def execute(self):
            # Intentionally omit 'name' to exercise the code path that fills
            # a missing name and returns a validated Profile.
            return FakeResp([
                {"id": "550e8400-e29b-41d4-a716-446655440002", "email": "remote@example.com"}
            ])

    db = Database()
    db.client = FakeClient()

    profile = db.get_profile("550e8400-e29b-41d4-a716-446655440002")
    assert profile is not None
    assert str(profile.id) == "550e8400-e29b-41d4-a716-446655440002"
    assert profile.email == "remote@example.com"


def test_get_profile_client_raises_database_error(monkeypatch):
    class ExplodingClient:
        def table(self, _):
            raise RuntimeError("client failure")

    db = Database()
    db.client = ExplodingClient()

    with pytest.raises(DatabaseError):
        db.get_profile("pid-x")
