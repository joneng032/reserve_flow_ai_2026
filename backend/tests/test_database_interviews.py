"""Tests for interview-related methods in backend.database.

Pattern: mock-mode, fake client success response, client exception mapping,
and data-shape error handling where applicable.
"""
import pytest

from backend.database import Database, DatabaseError


def test_create_interview_mock_mode_returns_interview():
    db = Database()
    db.client = None

    class I:
        def __init__(self):
            self.project_id = "550e8400-e29b-41d4-a716-446655440300"
            self.interviewee_name = "Alice"
            self.interview_type = "phone"

        def model_dump(self):
            return {"interviewee_name": "Alice", "interview_type": "phone"}

    interview = db.create_interview(I(), "profile-1")
    assert interview is not None
    assert getattr(interview, "interviewee_name", None) == "Alice"


def test_create_interview_client_exception_maps_to_database_error():
    class ExplodingClient:
        def table(self, _):
            raise RuntimeError("boom")

    db = Database()
    db.client = ExplodingClient()

    class I:
        def __init__(self):
            self.project_id = "p"

        def model_dump(self):
            return {"interviewee_name": "Bob"}

    with pytest.raises(DatabaseError):
        db.create_interview(I(), "profile-1")

