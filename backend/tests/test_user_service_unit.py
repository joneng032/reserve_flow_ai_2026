import pytest
from unittest.mock import Mock

from app.models.user_models import User
from app.services.user_service import UserService


def make_user(id: int = 1, username: str = "alice", active: bool = True) -> User:
    return User(id=id, username=username, email=f"{username}@example.com", is_active=active)


def test_activate_user_happy_path():
    # Arrange
    repo = Mock()
    user = make_user(active=False)
    repo.get_user_by_id.return_value = user
    repo.update_user.return_value = User(**{**user.model_dump(), "is_active": True})

    svc = UserService(user_repository=repo)

    # Act
    result = svc.activate_user(user.id)

    # Assert
    assert result.is_active is True
    repo.get_user_by_id.assert_called_once_with(user.id)
    repo.update_user.assert_called_once()


def test_activate_user_not_found_raises():
    repo = Mock()
    repo.get_user_by_id.return_value = None
    svc = UserService(user_repository=repo)

    with pytest.raises(ValueError):
        svc.activate_user(999)


def test_deactivate_user_happy_path():
    repo = Mock()
    user = make_user(active=True)
    repo.get_user_by_id.return_value = user
    repo.update_user.return_value = User(**{**user.model_dump(), "is_active": False})

    svc = UserService(user_repository=repo)

    result = svc.deactivate_user(user.id)

    assert result.is_active is False
    repo.get_user_by_id.assert_called_once_with(user.id)
    repo.update_user.assert_called_once()


def test_create_user_delegates_to_repository():
    repo = Mock()
    new_user = make_user(id=None, username="bob")
    created = make_user(id=2, username="bob")
    repo.create_user.return_value = created

    svc = UserService(user_repository=repo)

    result = svc.create_user(new_user)

    assert result.id == 2
    repo.create_user.assert_called_once_with(new_user)
