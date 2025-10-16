import pytest

from app.repositories.user_repository import UserRepository
from app.models.user_models import User


def make_user(username: str = "alice", id: int = None, active: bool = True) -> User:
    return User(id=id, username=username, email=f"{username}@example.com", is_active=active)


def test_create_and_get_user_happy_path():
    repo = UserRepository()
    repo.clear_users()

    user = make_user(username="bob")
    created = repo.create_user(user)

    assert created.id is not None
    fetched = repo.get_user_by_username("bob")
    assert fetched is not None
    assert fetched.username == "bob"

    fetched_by_id = repo.get_user_by_id(created.id)
    assert fetched_by_id.username == "bob"


def test_create_user_duplicate_raises():
    repo = UserRepository()
    repo.clear_users()

    user = make_user(username="carol")
    repo.create_user(user)

    with pytest.raises(ValueError):
        repo.create_user(make_user(username="carol"))


def test_update_user_and_nonexistent_update_raises():
    repo = UserRepository()
    repo.clear_users()

    user = make_user(username="dave")
    created = repo.create_user(user)

    created.email = "new@example.com"
    updated = repo.update_user(created)
    assert updated.email == "new@example.com"

    # Nonexistent user update should raise
    with pytest.raises(ValueError):
        repo.update_user(make_user(username="ghost"))


def test_delete_user_returns_bool():
    repo = UserRepository()
    repo.clear_users()

    u = repo.create_user(make_user(username="ellen"))
    assert repo.delete_user(u.id) is True
    assert repo.delete_user(9999) is False


def test_set_users_store_and_get_all_users():
    repo = UserRepository()
    repo.clear_users()

    store = {"x": make_user(username="x", id=10)}
    repo.set_users_store(store)
    all_users = repo.get_all_users()
    assert len(all_users) == 1
    assert all_users[0].id == 10
