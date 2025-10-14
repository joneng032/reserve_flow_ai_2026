# imports for test runtime are minimal; conftest sets env and path

from fastapi import HTTPException

import backend.main as main
from backend import database

# sys.path manipulation moved to conftest.py


def test_safe_db_call_maps_database_error():
    def broken():
        raise database.DatabaseError("db-failure")

    try:
        main.safe_db_call(broken)
        assert False, "Expected HTTPException"
    except HTTPException as he:
        assert he.status_code == 500
        assert "Database error" in str(he.detail)


def test_safe_db_call_value_error_maps_to_400():
    def bad():
        raise ValueError("bad input")

    try:
        main.safe_db_call(bad)
        assert False, "Expected HTTPException"
    except HTTPException as he:
        assert he.status_code == 400


def test_ensure_belongs_to_project_404_when_missing():
    try:
        main.ensure_belongs_to_project(None, "pid", resource_name="Res")
        assert False
    except HTTPException as he:
        assert he.status_code == 404


def test_ensure_belongs_to_project_mismatch_and_match():
    class R:
        pass

    r = R()
    r.project_id = "other"
    try:
        main.ensure_belongs_to_project(r, "pid", resource_name="Res")
        assert False
    except HTTPException as he:
        assert he.status_code == 404

    # Now match - should not raise
    r.project_id = "pid"
    main.ensure_belongs_to_project(r, "pid", resource_name="Res")
