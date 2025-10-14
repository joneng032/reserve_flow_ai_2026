# imports for test runtime are minimal; conftest sets env and path

import pytest

from backend.app.services.auth_service import AuthService
from backend.app.services.token_service import TokenService
from backend.app.services.user_service import UserService

# Ensure backend package root is on sys.path for imports when running tests
# sys.path manipulation moved to conftest.py


class DummyLogin:
    def __init__(self, user: str, pass_: str):
        self.user = user
        self.pass_ = pass_


def test_user_service_propagates_unexpected_errors(monkeypatch):
    svc = UserService()

    def raise_db(user_id):
        raise RuntimeError("DB connection lost")

    monkeypatch.setattr(svc.user_repository, "get_user_by_id", raise_db)

    with pytest.raises(RuntimeError):
        svc.get_user_by_id(999)


def test_token_service_propagates_unexpected_errors():
    svc = TokenService()

    class FakeStrategy:
        def verify_token(self, _token: str):
            raise RuntimeError("crypto backend failure")

    # Replace the underlying strategy so verify_token won't try to import
    # heavy native backends during this test.
    svc.strategy = FakeStrategy()

    with pytest.raises(RuntimeError):
        svc.verify_token("irrelevant-token")


def test_token_service_get_username_raises_on_missing_sub():
    svc = TokenService()

    class FakeStrategy:
        def verify_token(self, _token: str):
            return {}

    svc.strategy = FakeStrategy()

    with pytest.raises(ValueError):
        svc.get_username_from_token("token-without-sub")


def test_auth_service_authenticate_user_propagates_unexpected_repo_errors(monkeypatch):
    svc = AuthService()

    # Cause the auth repository to raise an unexpected error
    def raise_unexpected(u, p):
        raise RuntimeError("unexpected repo failure")

    monkeypatch.setattr(svc.auth_repository, "validate_credentials", raise_unexpected)

    with pytest.raises(RuntimeError):
        svc.authenticate_user(DummyLogin("any", "pw"))


def test_auth_service_authenticate_user_handles_expected_validation_errors(monkeypatch):
    svc = AuthService()

    def raise_validation(u, p):
        raise ValueError("malformed input")

    monkeypatch.setattr(svc.auth_repository, "validate_credentials", raise_validation)

    success, token, message = svc.authenticate_user(DummyLogin("any", "pw"))
    assert success is False
    assert token is None
    assert "malformed input" in message


def test_auth_service_login_raises_value_error_on_auth_failure(monkeypatch):
    svc = AuthService()

    def always_false(_u, _p):
        return False

    monkeypatch.setattr(svc.auth_repository, "validate_credentials", always_false)

    with pytest.raises(ValueError):
        svc.login(DummyLogin("any", "pw"))


def test_auth_service_authenticate_user_generates_token_on_success(monkeypatch):
    svc = AuthService()

    # Ensure credentials validate, and user exists/active
    def valid_creds(_u, _p):
        return True

    class FakeUser:
        def __init__(self):
            self.is_active = True

    def get_user(_u):
        return FakeUser()

    # Apply monkeypatches and assert the successful login flow
    monkeypatch.setattr(svc.auth_repository, "validate_credentials", valid_creds)
    monkeypatch.setattr(svc.user_repository, "get_user_by_username", get_user)

    success, token, message = svc.authenticate_user(DummyLogin("any", "pw"))
    assert success is True
    assert token is not None
    assert "Login exitoso" in message


def test_auth_service_validate_token_propagates_database_error(monkeypatch):
    from backend.database import DatabaseError

    svc = AuthService()

    # TokenService returns the username as usual
    svc.token_service = type(
        "T", (), {"get_username_from_token": lambda self, t: "someuser"}
    )()

    def raise_db_error(username):
        raise DatabaseError("DB is down")

    monkeypatch.setattr(svc.user_repository, "get_user_by_username", raise_db_error)

    with pytest.raises(DatabaseError):
        svc.validate_token("any-token")


def test_user_service_create_user_handles_value_error(monkeypatch):
    svc = UserService()

    def raise_value(user):
        raise ValueError("username exists")

    monkeypatch.setattr(svc.user_repository, "create_user", raise_value)

    with pytest.raises(ValueError):
        svc.create_user(None)


def test_user_service_create_user_propagates_unexpected_error(monkeypatch):
    svc = UserService()

    def raise_runtime(user):
        raise RuntimeError("DB connection lost")

    monkeypatch.setattr(svc.user_repository, "create_user", raise_runtime)

    with pytest.raises(RuntimeError):
        svc.create_user(None)
