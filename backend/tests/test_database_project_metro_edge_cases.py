from backend import database
from backend.models import ProjectMetroSettingCreate
from backend.tests.conftest import FakeClient, FakeQuery, uuid4_str
import types


def test_set_project_metro_client_none_returns_none():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    # Ensure mock-mode (client None) returns None
    database.db.client = None
    res = database.db.set_project_metro(proj_id, ProjectMetroSettingCreate(metro_area="X", project_id=proj_id), profile_id)
    assert res is None


def test_set_project_metro_update_no_response_returns_none():
    # Simulate existing metro setting but the update call returns an empty response
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    base = {
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "project_metro_settings": [{"id": uuid4_str(), "project_id": proj_id, "metro_area": "A"}],
    }
    client = FakeClient(base)

    # Create a FakeQuery instance for the metro settings and override update to yield no data
    fq = FakeQuery(data=list(base["project_metro_settings"]), table_name="project_metro_settings", client=client)

    def update_empty(self, data):
        # Force update to produce an empty result set
        self._data = []
        return self

    fq.update = types.MethodType(update_empty, fq)

    # Patch the client's table resolver to return our special FakeQuery for metro settings
    orig_table = client.table

    def table_override(name):
        if name == "project_metro_settings":
            return fq
        return orig_table(name)

    client.table = table_override
    database.db.client = client

    # Attempt to set metro; update path will run but yield no response -> should return None
    res = database.db.set_project_metro(proj_id, ProjectMetroSettingCreate(metro_area="B", project_id=proj_id), profile_id)
    assert res is None


def test_get_project_metro_handles_data_error_and_returns_none():
    # Simulate a data error when fetching metro settings (execute raises TypeError)
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}]})

    class BadQuery(FakeQuery):
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)

        def execute(self):
            raise TypeError("simulated data error")

    # Override client's table to return BadQuery for project_metro_settings
    def table_override(name):
        if name == "project_metro_settings":
            return BadQuery(data=[], table_name=name, client=client)
        return FakeQuery(client.table_data.get(name, []), table_name=name, client=client)

    client.table = table_override
    database.db.client = client

    got = database.db.get_project_metro(proj_id, profile_id)
    assert got is None
