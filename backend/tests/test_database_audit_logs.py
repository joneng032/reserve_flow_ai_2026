"""Tests for audit-log related methods in backend.database.

Pattern: mock-mode, fake client success response, client exception mapping,
and data-shape error handling where applicable.
"""
"""Tests for audit-log related methods in backend.database.

Pattern: mock-mode, fake client success response, client exception mapping,
and data-shape error handling where applicable.
"""
import pytest

from backend.database import Database, DatabaseError


def test_get_project_audit_logs_mock_mode_returns_list():
    db = Database()
    db.client = None

    logs = db.get_project_audit_logs("pid", "profile-1")
    assert isinstance(logs, list)


def test_get_project_audit_logs_client_exception_maps_to_database_error():
    class ExplodingClient:
        def table(self, _):
            raise RuntimeError("boom")

    db = Database()
    db.client = ExplodingClient()

    with pytest.raises(DatabaseError):
        db.get_project_audit_logs("p", "profile-1")

