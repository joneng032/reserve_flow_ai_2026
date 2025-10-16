from backend import database
from backend.models import ProjectMetroSettingCreate
from backend.tests.conftest import FakeClient, FakeQuery, uuid4_str
import types


def test_set_project_metro_update_returns_empty():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    base = {
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "project_metro_settings": [{"id": uuid4_str(), "project_id": proj_id, "metro_area": "A"}],
    }
    client = FakeClient(base)

    # Create a FakeQuery for project_metro_settings with update returning empty
    fq = FakeQuery(data=list(base["project_metro_settings"]), table_name="project_metro_settings", client=client)

    def update_empty(self, data):
        self._data = []
        return self

    fq.update = types.MethodType(update_empty, fq)

    client.table = lambda name: fq if name == "project_metro_settings" else FakeQuery(client.table_data.get(name, []), table_name=name, client=client)
    database.db.client = client

    res = database.db.set_project_metro(proj_id, ProjectMetroSettingCreate(metro_area="B", project_id=proj_id), profile_id)
    assert res is None


def test_set_project_metro_insert_returns_empty():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    base = {
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "project_metro_settings": [],
    }
    client = FakeClient(base)

    fq = FakeQuery(data=[], table_name="project_metro_settings", client=client)

    def insert_empty(self, data):
        self._data = []
        return self

    fq.insert = types.MethodType(insert_empty, fq)

    client.table = lambda name: fq if name == "project_metro_settings" else FakeQuery(client.table_data.get(name, []), table_name=name, client=client)
    database.db.client = client

    res = database.db.set_project_metro(proj_id, ProjectMetroSettingCreate(metro_area="C", project_id=proj_id), profile_id)
    assert res is None


def test_set_project_metro_execute_raises_typeerror():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "project_metro_settings": []})

    class BadQuery(FakeQuery):
        def execute(self):
            raise TypeError("simulated execute error")

    client.table = lambda name: BadQuery(client.table_data.get(name, []), table_name=name, client=client)
    database.db.client = client

    res = database.db.set_project_metro(proj_id, ProjectMetroSettingCreate(metro_area="D", project_id=proj_id), profile_id)
    assert res is None
