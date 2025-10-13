import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import Database


def test_database_mock_mode_when_env_missing(monkeypatch):
    # Ensure env vars not set -> mock mode
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    db = Database()
    # In mock mode client should be None
    assert getattr(db, "client", None) is None


def test_database_strict_init_raises(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    monkeypatch.setenv("DB_STRICT_INIT", "1")
    with pytest.raises(ValueError):
        Database()


def test_get_profile_returns_mock_profile(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    db = Database()
    from uuid import uuid4

    pid = str(uuid4())
    profile = db.get_profile(pid)
    assert profile is not None
    assert str(getattr(profile, "id", "")) == pid


def test_create_project_in_mock_mode(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    db = Database()
    from uuid import uuid4

    from app.models import ProjectCreate

    pid = str(uuid4())
    p = ProjectCreate(
        profile_id=pid,
        name="P",
        client_name="C",
        address="A",
        current_reserve_balance="0",
    )
    created = db.create_project(p)
    assert created is not None
    assert str(getattr(created, "profile_id", "")) == pid


def test_update_project_in_mock_mode(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    db = Database()
    from app.models import ProjectUpdate

    updated = db.update_project("proj-1", "profile-1", ProjectUpdate(name="New Name"))
    assert updated is not None
    assert updated.name == "New Name"
