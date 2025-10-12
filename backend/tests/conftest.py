import os
import warnings

import pytest

# Default to the simple pure-Python JWT implementation for local test runs
# to avoid importing heavy native crypto backends during test collection.
# CI workflows will explicitly set USE_SIMPLE_JWT as needed.
os.environ.setdefault("USE_SIMPLE_JWT", "1")


@pytest.fixture(autouse=True)
def set_test_env_vars(monkeypatch):
    """Ensure tests use the simple JWT strategy and silence upstream deprecation warnings until code is migrated."""
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
