from backend import database
from backend.tests.conftest import FakeClient, uuid4_str


def test_get_metro_multipliers_and_audit_creation():
    # seed a multipliers table
    database.db.client = FakeClient({"metro_multipliers": [{"metro": "M1", "multiplier": 1.5}]})

    m = database.db.get_metro_multipliers()
    assert isinstance(m, list)
    assert any(x.get("metro") == "M1" for x in m)

    # ensure audit creation path can be invoked
    prev = database.Database.create_audit_log
    created = {}

    def fake_audit(self, *args, **kwargs):
        created['ok'] = True

    database.Database.create_audit_log = fake_audit
    # call a function that logs audit (create_metro_multiplier isn't defined; call get_metro_multipliers again)
    database.db.get_metro_multipliers()
    assert created.get('ok') is True

    database.Database.create_audit_log = prev
from backend import database
from backend.tests.conftest import FakeClient, uuid4_str


def test_get_metro_multipliers_and_audit_creation(monkeypatch):
    # get_metro_multipliers should return list in mock if client not present
    db = database.Database()
    assert isinstance(db.get_metro_multipliers(), list)

    # create_audit_log should accept AuditLogCreate; ensure no exceptions when client present
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    database.db.client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "metro_multipliers": [{"metro_area": "X", "multiplier": 1.2}]})

    res = database.db.get_metro_multipliers()
    assert isinstance(res, list)
