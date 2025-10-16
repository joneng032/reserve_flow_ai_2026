"""
Additional focused unit tests for backend.main to cover error branches
that are not exercised by other tests.
"""
from types import SimpleNamespace

import pytest

import backend.main as main
from backend import database
from backend.models import ComponentCreate


def _auth_user():
    return {"id": "123", "email": "test@example.com", "username": "tester"}


def test_create_component_project_id_mismatch_direct_call():
    """Call the endpoint function directly with a constructed Pydantic model
    to avoid FastAPI body validation and exercise the project-id mismatch
    branch which should raise an HTTPException with a 400 status.
    """
    # Construct a ComponentCreate model instance (valid UUID string used)
    # Use valid UUIDv4 strings so Pydantic validation succeeds
    comp = ComponentCreate(name="My Component", project_id="550e8400-e29b-41d4-a716-446655440000")

    import asyncio

    with pytest.raises(main.HTTPException) as exc:
        asyncio.run(main.create_component("abc123", comp, _auth_user()))

    assert exc.value.status_code == 400
    assert "Project ID mismatch" in str(exc.value.detail)


from backend.models import CategoryCreate


def test_create_category_project_id_mismatch_direct_call():
    cat = CategoryCreate(name="Cat", project_id="550e8400-e29b-41d4-a716-446655440001")
    import asyncio

    with pytest.raises(main.HTTPException) as exc:
        asyncio.run(main.create_category("x", cat, {"id": "123"}))

    assert exc.value.status_code == 400
    assert "Project ID mismatch" in str(exc.value.detail)


def test_verify_jwt_token_missing_sub(monkeypatch):
    """If the token payload doesn't include 'sub', verify_jwt_token should
    return None (and not raise).
    """

    class DummyTokenSvc:
        def verify_token(self, token):
            return {"email": "no-sub@example.com", "username": "nosub"}

    monkeypatch.setattr(main, "TokenService", lambda: DummyTokenSvc())
    assert main.verify_jwt_token("any-token") is None
