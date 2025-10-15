import time
import pytest

from app.services.token_service import SimpleJWTStrategy, TokenService


def test_simple_jwt_create_and_verify():
    strat = SimpleJWTStrategy()
    token = strat.create_token({"sub": "alice"})

    payload = strat.verify_token(token)
    assert payload.get("sub") == "alice"
    assert "exp" in payload


def test_simple_jwt_invalid_signature_raises():
    strat = SimpleJWTStrategy()
    token = strat.create_token({"sub": "alice"})

    # Tamper with token signature
    parts = token.rsplit(".", 1)
    tampered = parts[0] + "." + ("A" * 10)

    with pytest.raises(ValueError):
        strat.verify_token(tampered)


def test_token_service_create_user_token_and_get_username():
    svc = TokenService(strategy=SimpleJWTStrategy())
    token = svc.create_user_token("bob")
    username = svc.get_username_from_token(token)
    assert username == "bob"


def test_expired_token_raises():
    from datetime import timedelta

    svc = TokenService(strategy=SimpleJWTStrategy())
    # Create a token that expired 1 second ago
    token = svc.create_access_token({"sub": "carol"}, expires_delta=timedelta(seconds=-1))
    with pytest.raises(ValueError):
        svc.verify_token(token)
