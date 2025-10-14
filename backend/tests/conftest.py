import os
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
