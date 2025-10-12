"""Compatibility adapter for Supabase client creation.

This module centralizes creation of a Supabase client so the rest of the
codebase doesn't import the `supabase` package directly. Keeping the heavy
imports inside this function lets tests and CI avoid import-time crashes on
platforms where native crypto extensions may be problematic.

The adapter prefers the legacy `supabase` package (backwards compatible)
and falls back to `supabase_auth` if available. If neither package is
available an ImportError is raised.
"""
import importlib
from typing import Any


def create_supabase_client(url: str, key: str) -> Any:
    """Create and return a Supabase client.

    This defers imports until runtime and attempts to adapt to either the
    legacy `supabase` package or the newer `supabase_auth` package if
    installed. The goal is to centralize the import surface so upgrades can be
    implemented in one place.
    """
    # Use importlib so tests can monkeypatch importlib.import_module and
    # simulate ImportError scenarios without actually loading heavy native
    # extensions (e.g., cryptography/gotrue) during unit tests.
    legacy_exc = None
    try:
        supabase_mod = importlib.import_module("supabase")
        if hasattr(supabase_mod, "create_client"):
            return getattr(supabase_mod, "create_client")(url, key)
        legacy_exc = ImportError(
            "legacy supabase package imported but no create_client"
        )
    except Exception as exc:  # Could be ImportError or other import-time error
        legacy_exc = exc

    # Try the newer supabase_auth package (best-effort support)
    try:
        supabase_auth_mod = importlib.import_module("supabase_auth")
        if hasattr(supabase_auth_mod, "create_client"):
            return getattr(supabase_auth_mod, "create_client")(url, key)
        if hasattr(supabase_auth_mod, "SupabaseClient"):
            return getattr(supabase_auth_mod, "SupabaseClient")(url, key)
        raise ImportError(
            "supabase_auth module found but no compatible factory function exposed"
        )
    except Exception as new_exc:
        # Provide helpful context about both failures
        raise ImportError(
            f"Could not create a Supabase client (legacy error: {legacy_exc}; new-api error: {new_exc})"
        ) from new_exc
