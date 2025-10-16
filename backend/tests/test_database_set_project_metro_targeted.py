import pytest
from backend import database
from backend.models import ProjectMetroSettingCreate
from backend.tests.conftest import FakeClient, FakeQuery, uuid4_str


def test_set_project_metro_ownership_negative():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    # projects table is empty -> ownership negative should return None
    database.db.client = FakeClient({"projects": [], "project_metro_settings": []})
    res = database.db.set_project_metro(proj_id, ProjectMetroSettingCreate(metro_area="X", project_id=proj_id), profile_id)
    assert res is None


def test_set_project_metro_response_no_data_returns_none():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    # ownership ok, but insert/update returns empty response
    client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "project_metro_settings": []})
    fq = FakeQuery(data=[], table_name="project_metro_settings", client=client)

    def insert_empty(self, data):
        self._data = []
        return self

    fq.insert = insert_empty.__get__(fq, type(fq))
    client.table = lambda name: fq if name == "project_metro_settings" else FakeQuery(client.table_data.get(name, []), table_name=name, client=client)
    database.db.client = client

    res = database.db.set_project_metro(proj_id, ProjectMetroSettingCreate(metro_area="Y", project_id=proj_id), profile_id)
    assert res is None


def test_set_project_metro_unexpected_exception_raises_database_error():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    class ExplodingClient(FakeClient):
        def table(self, name):
            raise RuntimeError("simulated client failure")

    database.db.client = ExplodingClient({"projects": [{"id": proj_id, "profile_id": profile_id}]})

    with pytest.raises(Exception):
        database.db.set_project_metro(proj_id, ProjectMetroSettingCreate(metro_area="Z", project_id=proj_id), profile_id)
