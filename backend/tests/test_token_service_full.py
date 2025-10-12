import base64
import json
import os
import sys
import types
from datetime import timedelta
from typing import Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app.services.token_service import (  # type: ignore
    ITokenStrategy,
    JWTTokenStrategy,
    TokenService,
)


def test_simple_jwt_create_verify_happy_path():
    svc = TokenService()  # conftest ensures USE_SIMPLE_JWT=1
    payload = {"sub": "u1", "email": "u1@example.com", "username": "u1"}
    token = svc.create_access_token(payload)
    decoded = svc.verify_token(token)
    assert decoded.get("sub") == "u1"


def test_simple_jwt_tampered_signature():
    svc = TokenService()
    token = svc.create_access_token({"sub": "u2"})
    header_b64, payload_b64, sig = token.split(".")
    tampered = header_b64 + "." + payload_b64 + "." + ("A" * len(sig))
    with pytest.raises(ValueError):
        svc.verify_token(tampered)


def test_simple_jwt_corrupted_payload():
    svc = TokenService()
    token = svc.create_access_token({"sub": "u3"})
    header_b64, payload_b64, sig = token.split(".")
    bad = header_b64 + ".!!notbase64!!." + sig
    with pytest.raises(ValueError):
        svc.verify_token(bad)


def test_simple_jwt_expired_token():
    svc = TokenService()
    token = svc.create_access_token({"sub": "u4"}, expires_delta=timedelta(seconds=-10))
    with pytest.raises(ValueError):
        svc.verify_token(token)


def test_verify_propagates_unexpected_errors():
    class BrokenStrategy(ITokenStrategy):
        def create_token(self, data: Any, expires_delta: Any = None) -> str:
            _ = data
            _ = expires_delta
            return ""

        def verify_token(self, token: str) -> Any:
            _ = token
            raise RuntimeError("strategy-failure")

    svc = TokenService(strategy=BrokenStrategy())
    with pytest.raises(RuntimeError):
        svc.verify_token("any")


def _make_fake_jose_module(
    monkeypatch: Any, raise_on_decode: bool = False, expired: bool = False
) -> None:
    # Create a fake jwt object
    class JWTError(Exception):
        pass

    class FakeJWT:
        last_payload = None

        @staticmethod
        def encode(payload: Any, secret: str, algorithm: str) -> str:
            FakeJWT.last_payload = dict(payload)
            # Reference secret to avoid unused-argument static warnings
            _ = secret
            # encode payload as b64 so JWTTokenStrategy.verify_token can parse
            payload_b64 = (
                base64.urlsafe_b64encode(json.dumps(payload).encode())
                .rstrip(b"=")
                .decode("ascii")
            )
            header_b64 = (
                base64.urlsafe_b64encode(json.dumps({"alg": algorithm}).encode())
                .rstrip(b"=")
                .decode("ascii")
            )
            sig = "fakesig"
            return f"{header_b64}.{payload_b64}.{sig}"

        @staticmethod
        def decode(token: str, secret: str, algorithms: Any = None) -> Any:
            # Reference secret/algorithms so static checkers don't warn
            _ = secret
            _ = algorithms
            if raise_on_decode:
                raise JWTError("invalid")
            try:
                # Only the payload fragment is required for tests; ignore other parts
                _hdr, payload_b64, _sig = token.split(".")
                payload_json = base64.urlsafe_b64decode(payload_b64 + "==").decode()
                payload = json.loads(payload_json)
                if expired:
                    # Simulate an expired token
                    raise JWTError("expired")
                return payload
            except JWTError:
                raise
            except Exception as e:
                raise JWTError() from e

    fake_jose = types.ModuleType("jose")
    setattr(fake_jose, "jwt", FakeJWT)
    fake_ex = types.ModuleType("jose.exceptions")
    setattr(fake_ex, "JWTError", JWTError)

    monkeypatch.setitem(sys.modules, "jose", fake_jose)
    monkeypatch.setitem(sys.modules, "jose.exceptions", fake_ex)


def test_jwt_strategy_monkeypatched_happy_path(monkeypatch: Any) -> None:
    _make_fake_jose_module(monkeypatch)
    strat = JWTTokenStrategy()
    token = strat.create_token({"sub": "jwt-user"})
    payload = strat.verify_token(token)
    assert payload.get("sub") == "jwt-user"


def test_jwt_strategy_monkeypatched_invalid_signature(monkeypatch: Any) -> None:
    # Make decode raise to simulate invalid signature
    _make_fake_jose_module(monkeypatch, raise_on_decode=True)
    strat = JWTTokenStrategy()
    token = "a.b.c"
    with pytest.raises(ValueError):
        strat.verify_token(token)
