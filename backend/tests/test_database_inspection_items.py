from backend.database import Database


def test_create_inspection_item_and_audit(monkeypatch):
    from backend.tests.conftest import FakeClient, uuid4_str
    from backend.models import InspectionItemCreate

    pid = uuid4_str()
    insp_id = uuid4_str()
    item_id = uuid4_str()

    client = FakeClient(table_data={
        "projects": [{"id": pid, "profile_id": "profile-1"}],
        "inspections": [{"id": insp_id, "project_id": pid, "projects": {"profile_id": "profile-1"}}],
        "inspection_items": [],
    })

    db = Database()
    db.client = client

    called = {}

    def fake_audit(a):
        called["ok"] = True
        return None

    monkeypatch.setattr(db, "create_audit_log", fake_audit)

    ii = InspectionItemCreate(inspection_id=insp_id, item_name="Window", item_type="condition")
    created = db.create_inspection_item(ii, profile_id="profile-1")
    assert created is not None
    assert called.get("ok")


def test_update_and_delete_inspection_item(monkeypatch):
    from backend.tests.conftest import FakeClient, uuid4_str

    pid = uuid4_str()
    insp_id = uuid4_str()
    item_id = uuid4_str()

    client = FakeClient(table_data={
        "inspections": [{"id": insp_id, "project_id": pid, "projects": {"profile_id": "profile-1"}}],
        "inspection_items": [{"id": item_id, "inspection_id": insp_id, "inspections": {"project_id": pid, "projects": {"profile_id": "profile-1"}}, "item_name": "Old"}],
    })

    db = Database()
    db.client = client

    called = {}

    def fake_audit(a):
        called["ok"] = True
        return None

    monkeypatch.setattr(db, "create_audit_log", fake_audit)

    # update
    from backend.models import InspectionItemUpdate

    upd = InspectionItemUpdate(item_name="Updated", item_type="condition")
    updated = db.update_inspection_item(item_id, upd, profile_id="profile-1")
    assert updated is not None
    assert called.get("ok")

    # delete
    deleted = db.delete_inspection_item(item_id, profile_id="profile-1")
    assert isinstance(deleted, bool)
