import pytest
from unittest.mock import Mock
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.utils.dependencies import get_current_user
from app.utils.dependencies import (
    get_auth_repository,
    get_user_repository,
    get_token_service,
    get_auth_service,
    get_user_service,
)
from app.repositories.auth_repository import AuthRepository
from app.repositories.user_repository import UserRepository
from app.services.token_service import TokenService
from app.services.auth_service import AuthService
from app.services.user_service import UserService


class DummyCreds:
    def __init__(self, token: str):
        self.credentials = token


def test_get_current_user_no_credentials_raises():
    # auth_service won't be called when credentials is None
    with pytest.raises(HTTPException) as exc:
        get_current_user(credentials=None, auth_service=None)

    assert exc.value.status_code == 401


def test_get_current_user_valid_token_returns_username():
    # mock auth_service with validate_token implementation
    class AuthSvc:
        def validate_token(self, token: str):
            assert token == "goodtoken"
            return "alice"

    creds = DummyCreds("goodtoken")
    username = get_current_user(credentials=creds, auth_service=AuthSvc())
    assert username == "alice"


def test_get_current_user_invalid_token_raises():
    class AuthSvc:
        def validate_token(self, token: str):
            raise ValueError("invalid token")

    creds = DummyCreds("badtoken")
    with pytest.raises(HTTPException) as exc:
        get_current_user(credentials=creds, auth_service=AuthSvc())

    assert exc.value.status_code == 401


def test_dependency_factories_return_expected_types():
    # Simple factory functions (no FastAPI runtime) should return instances
    auth_repo = get_auth_repository()
    # verify expected public method exists instead of strict isinstance
    assert hasattr(auth_repo, "validate_credentials") or hasattr(auth_repo, "get_user_credentials")

    user_repo = get_user_repository()
    assert hasattr(user_repo, "get_user_by_id")

    token_svc = get_token_service()
    assert hasattr(token_svc, "create_access_token") or hasattr(token_svc, "verify_token")


def test_get_auth_service_and_user_service_with_mocks():
    # get_auth_service expects concrete objects when called directly
    mock_auth_repo = Mock()
    mock_user_repo = Mock()
    mock_token = Mock()

    auth_service = get_auth_service(auth_repo=mock_auth_repo, user_repo=mock_user_repo, token_service=mock_token)
    # check the returned object exposes expected methods and references
    assert hasattr(auth_service, "authenticate_user")
    assert getattr(auth_service, "auth_repository", None) is mock_auth_repo
    assert getattr(auth_service, "user_repository", None) is mock_user_repo
    assert getattr(auth_service, "token_service", None) is mock_token

    user_service = get_user_service(user_repo=mock_user_repo)
    assert hasattr(user_service, "get_user_by_id")
    assert getattr(user_service, "user_repository", None) is mock_user_repo
