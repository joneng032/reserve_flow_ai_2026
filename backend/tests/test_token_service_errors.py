import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from datetime import timedelta
from typing import Any, Dict, Optional

from backend.app.services.token_service import ITokenStrategy, TokenService


def test_simple_jwt_detects_invalid_signature():
    svc = TokenService()

    # Create a valid token and then tamper with the signature
    token = svc.create_access_token({"sub": "123", "email": "a@b.com", "username": "u"})
    parts = token.split(".")
    assert len(parts) == 3
    header_b64, payload_b64, sig = parts
    tampered = header_b64 + "." + payload_b64 + "." + ("A" * len(sig))

    with pytest.raises(ValueError):
        svc.verify_token(tampered)


def test_simple_jwt_detects_invalid_payload():
    svc = TokenService()
    token = svc.create_access_token({"sub": "123", "email": "a@b.com", "username": "u"})
    parts = token.split(".")
    assert len(parts) == 3
    header_b64, _payload_b64, sig = parts

    # Corrupt the payload to invalid base64
    bad_payload = "!!notbase64!!"
    bad = header_b64 + "." + bad_payload + "." + sig

    with pytest.raises(ValueError):
        svc.verify_token(bad)


def test_verify_token_propagates_unexpected_errors():
    svc = TokenService()

    class BrokenStrategy(ITokenStrategy):
        def create_token(
            self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
        ) -> str:
            # Reference parameters to avoid unused-argument warnings in static analysis
            _ = data
            _ = expires_delta
            return ""

        def verify_token(self, token: str) -> Dict[str, Any]:
            raise RuntimeError("crypto backend failure")

    svc.strategy = BrokenStrategy()

    with pytest.raises(RuntimeError):
        svc.verify_token("any")


def test_protected_endpoint_returns_500_on_unexpected_verify_error(
    monkeypatch: pytest.MonkeyPatch,
):
    """If verify_jwt_token raises an unexpected RuntimeError, the API should return 500."""
    from fastapi.testclient import TestClient

    import backend.main as main

    def broken_verify(token: str):
        raise RuntimeError("crypto backend failure")

    # Replace the verify_jwt_token function with one that raises
    monkeypatch.setattr(main, "verify_jwt_token", broken_verify)

    with TestClient(main.app, raise_server_exceptions=False) as c:
        resp = c.get("/api/protected", headers={"Authorization": "Bearer any"})
        assert resp.status_code == 500
