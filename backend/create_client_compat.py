"""Compatibility shim exposing create_supabase_client at a top-level name.

Some scripts historically called `from supabase import create_client` or
referenced a top-level factory. This module exposes `create_supabase_client`
so those call sites can be migrated incrementally.
"""
from backend.app.utils.supabase_adapter import create_supabase_client


# Re-export under the familiar name
def create_client(url: str, key: str):
    return create_supabase_client(url, key)
