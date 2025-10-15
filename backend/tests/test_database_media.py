"""Tests for media-related methods in backend.database.

Pattern: mock-mode, fake client success response, client exception mapping,
and data-shape error handling where applicable.
"""
import pytest

from backend.database import Database, DatabaseError


def test_create_media_file_mock_mode_returns_namespace():
    db = Database()
    db.client = None

    class M:
        """Tests for media-related methods in backend.database.

        Pattern: mock-mode, fake client success response, client exception mapping,
        and data-shape error handling where applicable.
        """
        import pytest

        from backend.database import Database, DatabaseError


        def test_create_media_file_mock_mode_returns_namespace():
            db = Database()
            db.client = None

            class M:
                def __init__(self):
                    self.project_id = "550e8400-e29b-41d4-a716-446655440200"
                    self.file_name = "photo.png"
                    self.mime_type = "image/png"
                    self.size = 12345

            media = db.create_media_file(M(), "profile-1")
            assert media is not None
            assert getattr(media, "file_name", None) == "photo.png"


        def test_get_media_file_mock_mode_returns_none_or_media():
            db = Database()
            db.client = None

            out = db.get_media_file("mid", "profile-1")
            assert out is None or getattr(out, "id", None) is not None


        def test_create_media_file_client_exception_maps_to_database_error():
            class ExplodingClient:
                def table(self, _):
                    raise RuntimeError("boom")

            db = Database()
            db.client = ExplodingClient()

            class M:
                def __init__(self):
                    self.project_id = "p"
                    self.file_name = "f"

            with pytest.raises(DatabaseError):
                db.create_media_file(M(), "profile-1")

