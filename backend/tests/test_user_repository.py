from backend.app.models.user_models import User
from backend.app.repositories.user_repository import UserRepository


def test_user_repository_basic_crud():
    repo = UserRepository()

    # Create user without id/created_at so repository assigns them
    user = User(username="newuser", email="n@example.com")
    created = repo.create_user(user)
    assert created.username == "newuser"
    assert created.id is not None

    fetched = repo.get_user_by_username("newuser")
    assert fetched is not None
    assert fetched.username == "newuser"

    # Update user
    fetched.email = "changed@example.com"
    updated = repo.update_user(fetched)
    assert updated.email == "changed@example.com"

    # Delete user
    assert updated.id is not None
    deleted = repo.delete_user(int(updated.id))
    assert deleted is True
