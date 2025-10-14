import os
import sys
from types import SimpleNamespace
from typing import Any, Optional

import pytest

# Ensure test import resolution when running under tools that do not set PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from typing import cast

from backend.app.models.auth_models import LoginRequest
from backend.app.repositories.auth_repository import IAuthRepository
from backend.app.repositories.user_repository import IUserRepository
from backend.app.services.auth_service import AuthService
from backend.app.services.token_service import TokenService


class FakeAuthRepo:
    def __init__(self, valid: bool = True, raise_on_validate: bool = False) -> None:
        self.valid = valid
        self.raise_on_validate = raise_on_validate

    def validate_credentials(self, user: str, pass_: str) -> bool:
        # Use params to avoid unused-arg linter warnings
        _ = user
        _ = pass_
        if self.raise_on_validate:
            raise RuntimeError("db-failure")
        if not user or not pass_:
            raise ValueError("missing")
        return self.valid


class FakeUser:
    def __init__(self, username: str, is_active: bool = True) -> None:
        self.username = username
        self.is_active = is_active


class FakeUserRepo:
    def __init__(
        self, user: Optional[FakeUser] = None, raise_on_get: bool = False
    ) -> None:
        self.user = user
        self.raise_on_get = raise_on_get

    def get_user_by_username(self, username: str) -> Optional[FakeUser]:
        # Use parameter to avoid unused argument warnings
        _ = username
        if self.raise_on_get:
            raise RuntimeError("db-get-failure")
        return self.user


class FakeTokenService:
    def __init__(self, token: str = "tok") -> None:
        self.token = token

    def create_user_token(self, username: str, expires_delta: Any = None) -> str:
        _ = username
        _ = expires_delta
        return self.token

    def get_username_from_token(self, token: str) -> str:
        if token == "bad":
            raise ValueError("invalid")
        return "u1"


def test_authenticate_user_success():
    auth_repo = FakeAuthRepo(valid=True)
    user_repo = FakeUserRepo(user=FakeUser("u1"))
    svc = AuthService(
        auth_repository=cast(IAuthRepository, auth_repo),
        user_repository=cast(IUserRepository, user_repo),
        token_service=cast(TokenService, FakeTokenService()),
    )

    login_data = cast(LoginRequest, SimpleNamespace(user="u1", pass_="pw"))
    success, token, msg = svc.authenticate_user(login_data)
    assert success is True
    assert token == "tok"
    assert isinstance(msg, str)
    assert ("éxito" in msg) or ("Login exitoso" in msg)


def test_authenticate_user_bad_credentials():
    auth_repo = FakeAuthRepo(valid=False)
    user_repo = FakeUserRepo(user=FakeUser("u1"))
    svc = AuthService(
        auth_repository=cast(IAuthRepository, auth_repo),
        user_repository=cast(IUserRepository, user_repo),
        token_service=cast(TokenService, FakeTokenService()),
    )
    success, token, msg = svc.authenticate_user(
        cast(LoginRequest, SimpleNamespace(user="u1", pass_="pw"))
    )
    assert not success
    assert token is None


def test_authenticate_user_missing_fields_returns_controlled_error():
    auth_repo = FakeAuthRepo()
    user_repo = FakeUserRepo(user=FakeUser("u1"))
    svc = AuthService(
        auth_repository=cast(IAuthRepository, auth_repo),
        user_repository=cast(IUserRepository, user_repo),
        token_service=cast(TokenService, FakeTokenService()),
    )
    success, token, msg = svc.authenticate_user(
        cast(LoginRequest, SimpleNamespace(user="", pass_=""))
    )
    assert not success
    assert token is None
    assert isinstance(msg, str) and "Error de autenticación" in msg


def test_login_raises_on_failure():
    auth_repo = FakeAuthRepo(valid=False)
    user_repo = FakeUserRepo(user=FakeUser("u1"))
    svc = AuthService(
        auth_repository=cast(IAuthRepository, auth_repo),
        user_repository=cast(IUserRepository, user_repo),
        token_service=cast(TokenService, FakeTokenService()),
    )
    with pytest.raises(ValueError):
        svc.login(cast(LoginRequest, SimpleNamespace(user="u1", pass_="pw")))


def test_validate_token_success_and_inactive_user():
    user_repo = FakeUserRepo(user=FakeUser("u1", is_active=False))
    svc = AuthService(
        auth_repository=FakeAuthRepo(valid=True),
        user_repository=user_repo,
        token_service=FakeTokenService(),
    )
    with pytest.raises(ValueError):
        svc.validate_token("tok")


def test_validate_token_propagates_unexpected_repo_errors():
    user_repo = FakeUserRepo(raise_on_get=True)
    svc = AuthService(
        auth_repository=FakeAuthRepo(),
        user_repository=user_repo,
        token_service=FakeTokenService(),
    )
    with pytest.raises(RuntimeError):
        svc.validate_token("tok")
