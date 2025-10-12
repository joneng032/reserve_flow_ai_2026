import os
import sys

import pytest

# Ensure backend package root is on sys.path for imports when running tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from import_to_supabase import SupabaseImporter


def test_load_migration_data_file_not_found():
    importer = SupabaseImporter(None)
    with pytest.raises(SystemExit) as se:
        importer.load_migration_data("nonexistent_file.json")
    assert se.value.code == 1


def test_load_migration_data_invalid_json(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not a json")

    importer = SupabaseImporter(None)
    with pytest.raises(SystemExit) as se:
        importer.load_migration_data(str(bad))
    assert se.value.code == 1


def test_import_table_data_handles_value_error():
    class FakeQuery:
        def __init__(self, exc):
            self._exc = exc

        def insert(self, *args, **kwargs):
            return self

        def execute(self):
            raise self._exc

    class FakeClient:
        def __init__(self, exc):
            self._exc = exc

        def table(self, _name):
            return FakeQuery(self._exc)

    importer = SupabaseImporter(FakeClient(ValueError("bad data")))
    imported = importer.import_table_data("table", [{"id": 1}])
    assert imported == 0


def test_verify_import_handles_select_error():
    class FakeQuery:
        def select(self, *args, **kwargs):
            return self

        def execute(self):
            raise RuntimeError("select failed")

    class FakeClient:
        def table(self, _name):
            return FakeQuery()

    importer = SupabaseImporter(FakeClient())
    prepared = {"profiles": [{"id": "1"}]}
    results = {"profiles": 1}
    issues = importer.verify_import(prepared, results)
    assert isinstance(issues, list)
    assert len(issues) >= 1
