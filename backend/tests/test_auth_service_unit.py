import pytest
from unittest.mock import Mock

from app.models.auth_models import LoginRequest
from app.services.auth_service import AuthService


def make_login(user="alice", pwd="secret"):
    # Note: alias 'pass' maps to field 'pass_'
    return LoginRequest(**{"user": user, "pass": pwd})


def test_authenticate_user_happy_path():
    auth_repo = Mock()
    user_repo = Mock()
    token_svc = Mock()

    auth_repo.validate_credentials.return_value = True
    user_repo.get_user_by_username.return_value = Mock(is_active=True)
    token_svc.create_user_token.return_value = "tok"

    svc = AuthService(auth_repository=auth_repo, user_repository=user_repo, token_service=token_svc)

    success, token, msg = svc.authenticate_user(make_login())

    assert success is True
    assert token == "tok"
    assert "exitoso" in msg.lower()


def test_authenticate_user_invalid_credentials():
    auth_repo = Mock()
    user_repo = Mock()
    token_svc = Mock()

    auth_repo.validate_credentials.return_value = False
    svc = AuthService(auth_repository=auth_repo, user_repository=user_repo, token_service=token_svc)

    success, token, msg = svc.authenticate_user(make_login())

    assert success is False
    assert token is None
    assert "incorrect" in msg.lower() or "credenciales" in msg.lower()


def test_authenticate_user_inactive_user():
    auth_repo = Mock()
    user_repo = Mock()
    token_svc = Mock()

    auth_repo.validate_credentials.return_value = True
    user_repo.get_user_by_username.return_value = Mock(is_active=False)

    svc = AuthService(auth_repository=auth_repo, user_repository=user_repo, token_service=token_svc)

    success, token, msg = svc.authenticate_user(make_login())

    assert success is False
    assert token is None
    assert "inactivo" in msg.lower() or "inactive" in msg.lower()


def test_login_raises_on_auth_failure():
    auth_repo = Mock()
    user_repo = Mock()
    token_svc = Mock()

    auth_repo.validate_credentials.return_value = False
    svc = AuthService(auth_repository=auth_repo, user_repository=user_repo, token_service=token_svc)

    with pytest.raises(ValueError):
        svc.login(make_login())


def test_validate_token_user_not_found_raises():
    auth_repo = Mock()
    user_repo = Mock()
    token_svc = Mock()

    token_svc.get_username_from_token.return_value = "ghost"
    user_repo.get_user_by_username.return_value = None

    svc = AuthService(auth_repository=auth_repo, user_repository=user_repo, token_service=token_svc)

    with pytest.raises(ValueError):
        svc.validate_token("sometoken")


def test_authenticate_user_repo_raises_handled():
    auth_repo = Mock()
    user_repo = Mock()
    token_svc = Mock()

    auth_repo.validate_credentials.side_effect = ValueError("bad data")
    svc = AuthService(auth_repository=auth_repo, user_repository=user_repo, token_service=token_svc)

    success, token, msg = svc.authenticate_user(make_login())
    assert success is False
    assert token is None
    assert "error" in msg.lower()


def test_login_success_returns_tokenresponse():
    auth_repo = Mock()
    user_repo = Mock()
    token_svc = Mock()

    auth_repo.validate_credentials.return_value = True
    user_repo.get_user_by_username.return_value = Mock(is_active=True)
    token_svc.create_user_token.return_value = "tok"

    svc = AuthService(auth_repository=auth_repo, user_repository=user_repo, token_service=token_svc)
    resp = svc.login(make_login())
    assert resp.access_token == "tok"


def test_validate_token_inactive_user_raises():
    auth_repo = Mock()
    user_repo = Mock()
    token_svc = Mock()

    token_svc.get_username_from_token.return_value = "alice"
    user_repo.get_user_by_username.return_value = Mock(is_active=False)

    svc = AuthService(auth_repository=auth_repo, user_repository=user_repo, token_service=token_svc)

    with pytest.raises(ValueError):
        svc.validate_token("sometoken")
