import uuid
from types import SimpleNamespace


def uuid4_str():
    return str(uuid.uuid4())


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeQuery:
    def __init__(self, data=None, table_name=None, client=None):
        # data should be a list or None
        self._data = data or []
        self._table = table_name
        self._client = client

    def select(self, *_a, **_kw):
        return self

    def eq(self, *_a, **_kw):
        # Simple equality filter emulation for common query patterns.
        # Usage: .eq(column, value)
        try:
            if len(_a) >= 2:
                col, val = _a[0], _a[1]
            elif len(_a) == 1 and "value" in _kw:
                col, val = _a[0], _kw["value"]
            else:
                return self

            def match(row):
                if not isinstance(row, dict):
                    return False
                # handle nested access like 'inspections.projects.profile_id'
                if "." in col:
                    parts = col.split(".")
                    curr = row
                    for p in parts:
                        if not isinstance(curr, dict):
                            return False
                        next_val = curr.get(p)
                        if next_val is None and self._client:
                            # Attempt to emulate a join: if p names a related table that exists
                            # in client.table_data, try to find the related row using a foreign key
                            if p in self._client.table_data:
                                related_table = p
                                # common fk names: project_id, inspection_id, etc.
                                # prefer '<related_table[:-1]>_id' when plural form
                                fk_candidates = []
                                if related_table.endswith("s"):
                                    fk_candidates.append(related_table[:-1] + "_id")
                                fk_candidates.append(related_table + "_id")
                                fk_candidates.extend([k for k in curr.keys() if k.endswith("_id")])

                                fk = None
                                for fk_name in fk_candidates:
                                    fk = curr.get(fk_name)
                                    if fk:
                                        break
                                if not fk:
                                    return False
                                # lookup related row by id
                                rel_rows = self._client.table_data.get(related_table, [])
                                rel = None
                                for rr in rel_rows:
                                    if rr.get("id") == fk:
                                        rel = rr
                                        break
                                if rel is None:
                                    return False
                                curr = rel
                                continue
                            return False
                        curr = next_val
                    try:
                        return str(curr) == str(val)
                    except Exception:
                        return curr == val
                # direct equality
                try:
                    return str(row.get(col)) == str(val)
                except Exception:
                    return row.get(col) == val

            self._data = [r for r in (self._data or []) if match(r)]
        except Exception:
            # On any unexpected shape, leave data unchanged to avoid test crashes
            pass
        return self

    def order(self, *_a, **_kw):
        return self

    def range(self, *_a, **_kw):
        return self

    def insert(self, data):
        # simulate inserting: merge with sensible defaults based on table
        row = dict(data)
        # provide minimal defaults to satisfy Pydantic models
        if self._table == "media_files":
            row.setdefault("file_path", "mock/path.jpg")
            row.setdefault("file_type", "image")
            row.setdefault("mime_type", "image/jpeg")
            row.setdefault("file_size", 0)
            row.setdefault("project_id", row.get("project_id", "mock-project"))
        if self._table == "interviews":
            row.setdefault("interview_type", "mock")
            row.setdefault("project_id", row.get("project_id", "mock-project"))
        if self._table == "components":
            row.setdefault("name", row.get("name", "Unnamed Component"))
            row.setdefault("category", row.get("category", None))
            row.setdefault("base_cost", row.get("base_cost", 0))
            row.setdefault("useful_life", row.get("useful_life", None))
        if self._table == "inspection_items":
            row.setdefault("item_type", "mock")
            row.setdefault("inspection_id", row.get("inspection_id", "mock-insp"))
        if self._table == "evidence":
            row.setdefault("project_id", row.get("project_id", "mock-project"))
            row.setdefault("evidence_type", row.get("evidence_type", "photo"))
        # ensure an id is present
        row.setdefault("id", str(uuid.uuid4()))
        self._data = [row]
        return self

    def update(self, data):
        # simulate update: merge incoming data onto existing row if present
        if self._data and isinstance(self._data, list) and len(self._data) > 0 and isinstance(self._data[0], dict):
            merged = dict(self._data[0])
            merged.update(data)
            # ensure minimal defaults similar to insert
            if self._table == "media_files":
                merged.setdefault("file_path", "mock/path.jpg")
                merged.setdefault("file_type", "image")
                merged.setdefault("mime_type", "image/jpeg")
                merged.setdefault("file_size", 0)
            if self._table == "interviews":
                merged.setdefault("interview_type", "mock")
            if self._table == "inspection_items":
                merged.setdefault("item_type", "mock")

            self._data = [merged]
        else:
            self._data = [data]
        return self

    def delete(self):
        # simulate delete: keep existing _data as the rows that would be returned
        return self

    def execute(self):
        # ensure existing rows have minimal defaults for model construction
        normalized = []
        for row in (self._data or []):
            if not isinstance(row, dict):
                normalized.append(row)
                continue
            r = dict(row)
            # set sensible defaults based on table
            if self._table == "media_files":
                r.setdefault("file_path", "mock/path.jpg")
                r.setdefault("file_type", "image")
                r.setdefault("mime_type", "image/jpeg")
                r.setdefault("file_size", 0)
                r.setdefault("project_id", r.get("project_id", "mock-project"))
            if self._table == "interviews":
                r.setdefault("interview_type", "mock")
                r.setdefault("project_id", r.get("project_id", "mock-project"))
            if self._table == "components":
                r.setdefault("name", r.get("name", "Unnamed Component"))
                r.setdefault("category", r.get("category", None))
                r.setdefault("base_cost", r.get("base_cost", 0))
                r.setdefault("useful_life", r.get("useful_life", None))
            if self._table == "inspection_items":
                r.setdefault("item_type", "mock")
                r.setdefault("inspection_id", r.get("inspection_id", "mock-insp"))
            if self._table == "evidence":
                r.setdefault("project_id", r.get("project_id", "mock-project"))
                r.setdefault("evidence_type", r.get("evidence_type", "photo"))
            r.setdefault("id", str(uuid.uuid4()))
            normalized.append(r)

        return FakeResponse(normalized)


class FakeClient:
    def __init__(self, table_data=None):
        # table_data: dict mapping table name to list of rows
        self.table_data = table_data or {}

    def table(self, name):
        data = self.table_data.get(name, [])
        return FakeQuery(data, table_name=name, client=self)

import os
import subprocess
import sys
import warnings

import pytest

# Ensure the repository root is on sys.path so package-qualified imports
# like `backend.models` work when tests are run from the project root or
# when individual test files are executed by tooling. Placing this once in
# conftest avoids repeated sys.path manipulation and prevents E402 errors
# (module-level import not at top of file) in each test module.
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

# Default to the simple pure-Python JWT implementation for local test runs
# to avoid importing heavy native crypto backends during test collection.
# CI workflows may set USE_SIMPLE_JWT explicitly in matrix entries. Some CI
# runners set an environment variable to an empty string which counts as
# "present" for setdefault; treat empty values as unset so tests still
# default to the safe pure-Python strategy during collection.
if not os.environ.get("USE_SIMPLE_JWT"):
    # Covers both not-present and present-but-empty values
    os.environ["USE_SIMPLE_JWT"] = "1"


@pytest.fixture(autouse=True)
def set_test_env_vars(monkeypatch):
    """Ensure tests use the simple JWT strategy and silence upstream
    deprecation warnings until code is migrated.
    """
    monkeypatch.setenv("USE_SIMPLE_JWT", "1")
    # Silence upstream deprecation warnings from third-party libs during tests
    warnings.filterwarnings(
        "ignore", message=r".*gotrue.*deprecated.*", category=DeprecationWarning
    )
    warnings.filterwarnings(
        "ignore", message=r".*supabase.*deprecated.*", category=DeprecationWarning
    )
    warnings.filterwarnings(
        "ignore",
        message=r"Support for class-based `config` is deprecated.*",
        category=DeprecationWarning,
    )


@pytest.fixture(autouse=True, scope="session")
def neutralize_git_calls(tmp_path_factory):
    """A defensive fallback for CI: neutralize calls to the `git` binary
    during test collection and test runs.

    Some CI runners (and third-party libs) invoke `git` at import or
    collection time to determine versions or repository metadata. If
    the runner environment causes those git invocations to fail with
    exit code 128 the whole job will fail. Add a minimal shim that
    short-circuits git invocations so tests can run reliably in CI.

    This fixture:
    - creates a small fake `git` executable in a temp dir and prepends
      it to PATH so plain `git` lookups resolve to our harmless stub;
    - monkeypatches `subprocess.run`, `subprocess.check_output`,
      `subprocess.Popen`, and `os.system` to intercept git commands by
      executable name or command string and return success.
    """
    # Create a small temporary directory for the fake git shim and
    # ensure it's first on PATH so it takes precedence over system git.
    fake_dir = tmp_path_factory.mktemp("fakegit")
    if sys.platform == "win32":
        git_stub = fake_dir / "git.cmd"
        git_stub.write_text("@echo off\r\nexit /b 0\r\n")
    else:
        git_stub = fake_dir / "git"
        git_stub.write_text("#!/bin/sh\nexit 0\n")
        git_stub.chmod(0o755)

    old_path = os.environ.get("PATH", "")
    # Prepend the fake git directory to PATH for the whole test session.
    os.environ["PATH"] = str(fake_dir) + os.pathsep + old_path

    # Helpers to detect git invocations
    def _is_git_cmd(cmd):
        if not cmd:
            return False
        # cmd may be a list/tuple or a string
        exe = None
        if isinstance(cmd, (list, tuple)):
            exe = cmd[0]
        elif isinstance(cmd, str):
            # crude split for the command string to detect leading exe
            exe = cmd.split()[0]
        else:
            try:
                exe = str(cmd)
            except Exception:
                return False
        exe_name = os.path.basename(str(exe)).lower()
        return exe_name in ("git", "git.exe", "git.cmd", "git.bat")

    # Monkeypatch subprocess.run / check_output to short-circuit git
    # Save originals so we can restore them at teardown
    _orig_run = subprocess.run
    _orig_check_output = subprocess.check_output
    _orig_popen = subprocess.Popen
    _orig_os_system = os.system

    def _fake_run(cmd, *a, **kw):
        try:
            if _is_git_cmd(cmd):
                return subprocess.CompletedProcess(
                    cmd, 0, stdout=b"" if kw.get("capture_output") else None
                )
        except Exception:
            pass
        return _orig_run(cmd, *a, **kw)

    def _fake_check_output(cmd, *a, **kw):
        try:
            if _is_git_cmd(cmd):
                return b""
        except Exception:
            pass
        return _orig_check_output(cmd, *a, **kw)

    class _DummyPopen:
        def __init__(self, args, *a, **kw):
            self.args = args
            self.returncode = 0
            self.pid = 1

        def communicate(self, input=None):
            return (b"", b"")

        def wait(self, timeout=None):
            return 0

        def poll(self):
            return 0

        def terminate(self):
            return None

        def kill(self):
            return None

    def _fake_popen(args, *a, **kw):
        try:
            if _is_git_cmd(args):
                return _DummyPopen(args, *a, **kw)
        except Exception:
            pass
        return _orig_popen(args, *a, **kw)

    def _fake_system(cmd):
        try:
            if isinstance(cmd, str) and "git" in cmd:
                return 0
        except Exception:
            pass
        return _orig_os_system(cmd)

    # Apply our process-level patches for the session
    subprocess.run = _fake_run
    subprocess.check_output = _fake_check_output
    subprocess.Popen = _fake_popen
    os.system = _fake_system

    try:
        yield
    finally:
        # Restore originals and PATH
        subprocess.run = _orig_run
        subprocess.check_output = _orig_check_output
        subprocess.Popen = _orig_popen
        os.system = _orig_os_system
        os.environ["PATH"] = old_path
