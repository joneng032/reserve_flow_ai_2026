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
