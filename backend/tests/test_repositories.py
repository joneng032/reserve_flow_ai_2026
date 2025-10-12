import os
import sys

import pytest

# Ensure backend package root is on sys.path for imports when running tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.user_models import User
from app.repositories.auth_repository import AuthRepository
from app.repositories.user_repository import UserRepository


def test_user_repository_create_duplicate_raises_valueerror():
    repo = UserRepository()
    # Reset in-memory store for deterministic behavior
    repo._users = {}

    user = User(username="alice", email="alice@example.com")
    created = repo.create_user(user)
    assert created.username == "alice"

    # Creating the same username again should raise ValueError
    with pytest.raises(ValueError):
        repo.create_user(User(username="alice", email="alice2@example.com"))


def test_user_repository_unexpected_error_propagates(monkeypatch):
    repo = UserRepository()

    class BadStore:
        def get(self, key):
            raise RuntimeError("underlying store failure")

    # Replace internal store with one that raises
    repo._users = BadStore()

    with pytest.raises(RuntimeError):
        repo.get_user_by_username("anything")


def test_user_repository_create_update_delete_propagate(monkeypatch):
    repo = UserRepository()

    class BadStore:
        def __init__(self):
            pass

        def __setitem__(self, k, v):
            raise RuntimeError("store set failed")

        def __getitem__(self, k):
            raise RuntimeError("store get failed")

        def items(self):
            raise RuntimeError("store items failed")

    repo._users = BadStore()

    with pytest.raises(RuntimeError):
        repo.create_user(User(username="x", email="x@example.com"))

    # update_user will check key membership first
    with pytest.raises(RuntimeError):
        repo.update_user(User(username="x", email="x@example.com"))

    with pytest.raises(RuntimeError):
        repo.delete_user(1)


def test_auth_repository_credentials_and_propagation(monkeypatch):
    repo = AuthRepository()
    # Use a clean credentials store
    repo._credentials = {}

    assert repo.validate_credentials("noone", "pw") is False

    repo.add_user_credentials("bob", "s3cret")
    assert repo.validate_credentials("bob", "s3cret") is True

    assert repo.remove_user_credentials("bob") is True
    assert repo.remove_user_credentials("bob") is False

    # Now simulate underlying storage failures
    class BadCreds:
        def get(self, key):
            raise RuntimeError("credentials backend error")

    repo._credentials = BadCreds()
    with pytest.raises(RuntimeError):
        repo.validate_credentials("bob", "pw")
