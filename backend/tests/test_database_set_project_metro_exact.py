from backend import database
from backend.models import ProjectMetroSettingCreate
from backend.tests.conftest import FakeClient, FakeQuery, uuid4_str


def test_set_project_metro_client_none_explicit():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    database.db.client = None
    res = database.db.set_project_metro(proj_id, ProjectMetroSettingCreate(metro_area="X", project_id=proj_id), profile_id)
    assert res is None


def test_set_project_metro_update_returns_model():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    base = {
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        "project_metro_settings": [{"id": uuid4_str(), "project_id": proj_id, "metro_area": "A"}],
    }
    client = FakeClient(base)

    # Make existing.data True by returning rows on select
    select_query = FakeQuery(data=list(base["project_metro_settings"]), table_name="project_metro_settings", client=client)

    # Make update return a response with data so the model path is taken
    def update_with_row(self, data):
        row = dict(self._data[0]) if self._data else {}
        row.update(data)
        row.setdefault("id", uuid4_str())
        row.setdefault("metro_area", data.get("metro_area", "A"))
        self._data = [row]
        return self

    select_query.update = update_with_row.__get__(select_query, type(select_query))

    client.table = lambda name: select_query if name == "project_metro_settings" else FakeQuery(client.table_data.get(name, []), table_name=name, client=client)
    database.db.client = client

    res = database.db.set_project_metro(proj_id, ProjectMetroSettingCreate(metro_area="B", project_id=proj_id), profile_id)
    assert res is not None


def test_set_project_metro_model_instantiation_error_returns_none(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "project_metro_settings": []})

    # Make insert return a row, but monkeypatch ProjectMetroSetting to raise ValueError when called
    fq = FakeQuery(data=[], table_name="project_metro_settings", client=client)

    def insert_row(self, data):
        row = dict(data)
        row.setdefault("id", uuid4_str())
        self._data = [row]
        return self

    fq.insert = insert_row.__get__(fq, type(fq))
    client.table = lambda name: fq if name == "project_metro_settings" else FakeQuery(client.table_data.get(name, []), table_name=name, client=client)
    database.db.client = client

    # Monkeypatch the ProjectMetroSetting constructor to raise ValueError
    monkeypatch.setattr(database, "ProjectMetroSetting", lambda *a, **k: (_ for _ in ()).throw(ValueError("simulated")))

    res = database.db.set_project_metro(proj_id, ProjectMetroSettingCreate(metro_area="Z", project_id=proj_id), profile_id)
    assert res is None
