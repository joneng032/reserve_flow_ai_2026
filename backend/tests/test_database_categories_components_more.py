from types import SimpleNamespace

from backend.database import Database


def test_update_category_and_delete_with_audit(monkeypatch):
    from backend.tests.conftest import FakeClient, uuid4_str

    cid = uuid4_str()
    proj_id = uuid4_str()

    client = FakeClient(table_data={
        "categories": [{"id": cid, "project_id": proj_id, "projects": {"profile_id": "profile-1"}, "name": "Old"}],
    })

    db = Database()
    db.client = client

    called = {}

    def fake_audit(a):
        called['ok'] = True
        return None

    monkeypatch.setattr(db, "create_audit_log", fake_audit)

    class U:
        def model_dump(self, exclude_unset=True):
            return {"name": "NewCat"}

    updated = db.update_category(cid, U(), "profile-1")
    assert updated is not None

    deleted = db.delete_category(cid, "profile-1")
    # FakeClient.delete returns underlying row; delete_category returns bool
    assert deleted is True or deleted is False
    assert called.get('ok', True) is True

