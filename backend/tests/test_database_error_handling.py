import os
import sys

import pytest

# Ensure backend package root is on sys.path for imports when running tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException

from backend.database import Database, DatabaseError
from backend.main import safe_db_call
from backend.models import AuditLogCreate, ComponentCreate, ProjectCreate, ProjectUpdate


class _FakeQuery:
    def __init__(self, exc):
        self._exc = exc

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, *_args, **_kwargs):
        return self

    def range(self, *_args, **_kwargs):
        return self

    def insert(self, *_args, **_kwargs):
        return self

    def update(self, *_args, **_kwargs):
        return self

    def delete(self, *_args, **_kwargs):
        return self

    def contains(self, *_args, **_kwargs):
        return self

    def order(self, *_args, **_kwargs):
        return self

    def execute(self):
        raise self._exc


class _FakeClient:
    def __init__(self, exc):
        self._exc = exc

    def table(self, _name):
        return _FakeQuery(self._exc)


def _make_project_create():
    return ProjectCreate(
        name="X",
        client_name="Y",
        address="Z",
        profile_id=str(uuid4()),
        current_reserve_balance=Decimal("0"),
        custom_fields={},
    )


def _make_component_create():
    return ComponentCreate(
        project_id=uuid4(),
        name="Comp",
        category="Cat",
        base_cost=Decimal("1000"),
        useful_life=10,
    )


def test_database_methods_raise_databaseerror_on_unexpected_client_failure():
    db = Database()
    # Inject a fake client that raises an unexpected RuntimeError from execute()
    db.client = _FakeClient(RuntimeError("simulated client failure"))

    with pytest.raises(DatabaseError):
        db.get_profile("id")

    with pytest.raises(DatabaseError):
        db.create_profile(_make_project_create())

    with pytest.raises(DatabaseError):
        db.get_projects("profile")

    with pytest.raises(DatabaseError):
        db.create_project(_make_project_create())

    with pytest.raises(DatabaseError):
        db.update_project("pid", "profile", ProjectUpdate(name="New"))

    with pytest.raises(DatabaseError):
        db.delete_project("pid", "profile")

    with pytest.raises(DatabaseError):
        db.create_component(_make_component_create(), "profile")

    with pytest.raises(DatabaseError):
        db.get_cost_analysis("pid", "profile")

    # Audit log insert should be normalized as DatabaseError when client fails
    audit = AuditLogCreate(
        project_id=str(uuid4()),
        entity_type="t",
        entity_id=str(uuid4()),
        action="a",
        user_id=str(uuid4()),
        details={},
    )
    with pytest.raises(DatabaseError):
        db.create_audit_log(audit)


def test_database_methods_handle_expected_data_errors_as_fallbacks():
    db = Database()
    # Inject a fake client that raises a ValueError (expected/data error)
    db.client = _FakeClient(ValueError("malformed response"))

    # Data errors should be handled gracefully and return fallback values
    assert db.get_profile("id") is None
    assert db.get_projects("profile") == []
    assert db.create_project(_make_project_create()) is None
    assert db.delete_project("pid", "profile") is False
    analysis = db.get_cost_analysis("pid", "profile")
    # When a data error is encountered, cost analysis should return a default shaped object
    assert hasattr(analysis, "total_components")
    assert analysis.total_components == 0


def test_safe_db_call_translates_databaseerror_and_valueerror_to_http_exceptions():
    # DatabaseError -> HTTP 500
    def raise_db():
        raise DatabaseError("boom")

    with pytest.raises(HTTPException) as ei:
        safe_db_call(raise_db)
    assert ei.value.status_code == 500

    # ValueError -> HTTP 400
    def raise_val():
        raise ValueError("bad input")

    with pytest.raises(HTTPException) as ei2:
        safe_db_call(raise_val)
    assert ei2.value.status_code == 400


def test_safe_db_call_translates_attributeerror_to_400():
    def raise_attr():
        raise AttributeError("missing attribute")

    with pytest.raises(HTTPException) as ei3:
        safe_db_call(raise_attr)
    assert ei3.value.status_code == 400


def test_safe_db_call_does_not_swallow_unexpected_exceptions():
    def raise_runtime():
        raise RuntimeError("unexpected runtime")

    with pytest.raises(RuntimeError):
        safe_db_call(raise_runtime)
