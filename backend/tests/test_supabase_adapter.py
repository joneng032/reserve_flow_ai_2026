import os
import sys
import types

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.app.utils import supabase_adapter


def test_legacy_supabase_module_used(monkeypatch):
    # Create a fake legacy 'supabase' module with a create_client factory
    # Patch importlib.import_module so the adapter can't accidentally import
    # the real `supabase` package (which pulls in gotrue/cryptography).
    import importlib as _importlib

    orig_import = _importlib.import_module

    def fake_import(name, package=None):
        if name == "supabase":
            mod = types.ModuleType("supabase")

            def fake_create(url, key):
                return f"legacy:{url}:{key}"

            mod.create_client = fake_create
            return mod
        return orig_import(name, package=package)

    monkeypatch.setattr("importlib.import_module", fake_import)

    client = supabase_adapter.create_supabase_client("u", "k")
    assert client == "legacy:u:k"


def test_fallback_to_supabase_auth(monkeypatch):
    # Patch importlib.import_module so the adapter can't accidentally import
    # the real `supabase` package. Ensure `supabase` import raises while
    # `supabase_auth` returns our fake module.
    import importlib as _importlib

    orig_import = _importlib.import_module

    def fake_import(name, package=None):
        if name == "supabase":
            raise ImportError("simulate missing legacy supabase")
        if name == "supabase_auth":
            mod = types.ModuleType("supabase_auth")

            def fake_new_create(url, key):
                return f"new:{url}:{key}"

            mod.create_client = fake_new_create
            return mod
        return orig_import(name, package=package)

    monkeypatch.setattr("importlib.import_module", fake_import)

    client = supabase_adapter.create_supabase_client("u2", "k2")
    assert client == "new:u2:k2"


def test_supabase_auth_supabaseclient_class_fallback(monkeypatch):
    import importlib as _importlib

    orig_import = _importlib.import_module

    def fake_import(name, package=None):
        if name == "supabase":
            raise ImportError("simulate missing legacy supabase")
        if name == "supabase_auth":
            mod = types.ModuleType("supabase_auth")

            class FakeClient:
                def __init__(self, url, key):
                    self.url = url
                    self.key = key

            mod.SupabaseClient = FakeClient
            return mod
        return orig_import(name, package=package)

    monkeypatch.setattr("importlib.import_module", fake_import)

    client = supabase_adapter.create_supabase_client("u3", "k3")
    assert client.__class__.__name__ == "FakeClient"
    assert getattr(client, "url") == "u3" and getattr(client, "key") == "k3"
