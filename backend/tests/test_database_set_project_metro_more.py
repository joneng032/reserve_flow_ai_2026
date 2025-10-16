from decimal import Decimal
from types import SimpleNamespace
from backend import database
from backend.models import ProjectMetroSettingCreate
from backend.tests.conftest import FakeClient, FakeQuery, uuid4_str


def test_set_project_metro_update_with_decimal_custom_multiplier():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    base = {
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "project_metro_settings": [{"id": uuid4_str(), "project_id": proj_id, "metro_area": "A"}],
    }
    client = FakeClient(base)

    # Create a FakeQuery for project_metro_settings where update returns a Decimal custom_multiplier
    fq = FakeQuery(data=list(base["project_metro_settings"]), table_name="project_metro_settings", client=client)

    def update_with_decimal(self, data):
        # simulate DB returning a row with Decimal custom_multiplier
        row = dict(self._data[0]) if self._data else {}
        row.update(data)
        row["custom_multiplier"] = Decimal("1.25")
        self._data = [row]
        return self

    fq.update = update_with_decimal.__get__(fq, type(fq))

    client.table = lambda name: fq if name == "project_metro_settings" else FakeQuery(client.table_data.get(name, []), table_name=name, client=client)
    database.db.client = client

    res = database.db.set_project_metro(proj_id, ProjectMetroSettingCreate(metro_area="B", project_id=proj_id), profile_id)
    assert res is not None
    # custom_multiplier should be converted/available on the returned model
    assert getattr(res, "custom_multiplier", None) is not None


def test_set_project_metro_insert_with_string_fields():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    base = {
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "project_metro_settings": [],
    }
    client = FakeClient(base)

    fq = FakeQuery(data=[], table_name="project_metro_settings", client=client)

    def insert_with_strings(self, data):
        # simulate DB returning string-typed fields (e.g., numeric fields as strings)
        row = dict(data)
        row.setdefault("id", uuid4_str())
        # intentionally provide custom_multiplier as a string
        if "custom_multiplier" not in row:
            row["custom_multiplier"] = "1.5"
        self._data = [row]
        return self

    fq.insert = insert_with_strings.__get__(fq, type(fq))

    client.table = lambda name: fq if name == "project_metro_settings" else FakeQuery(client.table_data.get(name, []), table_name=name, client=client)
    database.db.client = client

    res = database.db.set_project_metro(proj_id, ProjectMetroSettingCreate(metro_area="C", project_id=proj_id), profile_id)
    assert res is not None
    # custom_multiplier may be converted by pydantic; if present, ensure it's parseable
    cm = getattr(res, "custom_multiplier", None)
    if cm is not None:
        # either Decimal or string representing the numeric value
        assert str(cm).startswith("1")
