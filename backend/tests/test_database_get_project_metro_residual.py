import pytest
from decimal import Decimal

from backend import database
from backend.models import ProjectMetroSetting, ProjectMetroSettingCreate
from backend.tests.conftest import FakeClient, FakeQuery, uuid4_str


def test_get_project_metro_client_none():
    database.db.client = None
    res = database.db.get_project_metro(uuid4_str(), uuid4_str())
    assert res is None


def test_get_project_metro_ownership_negative():
    database.db.client = FakeClient({"projects": []})
    res = database.db.get_project_metro(uuid4_str(), uuid4_str())
    assert res is None


def test_get_project_metro_found_returns_model():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    row = {"id": uuid4_str(), "project_id": proj_id, "metro_area": "X", "custom_multiplier": Decimal("1.2")}
    client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "project_metro_settings": [row]})
    database.db.client = client
    res = database.db.get_project_metro(proj_id, profile_id)
    assert isinstance(res, ProjectMetroSetting)


def test_get_project_metro_empty_returns_none():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "project_metro_settings": []})
    database.db.client = client
    res = database.db.get_project_metro(proj_id, profile_id)
    assert res is None


def test_get_project_metro_data_error_returns_none():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    class BrokenQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise AttributeError("simulated")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "projects":
                return FakeQuery(data=[{"id": proj_id, "profile_id": profile_id}], table_name="projects", client=self)
            return BrokenQuery()

    database.db.client = BrokenClient({})
    res = database.db.get_project_metro(proj_id, profile_id)
    assert res is None


def test_get_project_metro_raises_database_error():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    class ExplodingQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise Exception("boom")

    class ExplodingClient(FakeClient):
        def table(self, name):
            if name == "projects":
                return FakeQuery(data=[{"id": proj_id, "profile_id": profile_id}], table_name="projects", client=self)
            return ExplodingQuery()

    database.db.client = ExplodingClient({})
    with pytest.raises(database.DatabaseError):
        database.db.get_project_metro(proj_id, profile_id)
from decimal import Decimal
import pytest
from backend import database
from backend.models import ProjectMetroSettingCreate
from backend.tests.conftest import FakeClient, FakeQuery, uuid4_str
from types import SimpleNamespace


def test_get_project_metro_client_none():
    database.db.client = None
    assert database.db.get_project_metro(uuid4_str(), uuid4_str()) is None


def test_get_project_metro_ownership_negative():
    database.db.client = FakeClient({"projects": []})
    assert database.db.get_project_metro(uuid4_str(), uuid4_str()) is None


def test_get_project_metro_existing_update_returns_model():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    base = {"projects": [{"id": proj_id, "profile_id": profile_id}], "project_metro_settings": [{"id": uuid4_str(), "project_id": proj_id, "metro_area": "A"}]}
    client = FakeClient(base)

    # Make update return a row
    fq = FakeQuery(data=list(base["project_metro_settings"]), table_name="project_metro_settings", client=client)

    def update_with_row(self, data):
        row = dict(self._data[0]) if self._data else {}
        row.update(data)
        self._data = [row]
        return self

    fq.update = update_with_row.__get__(fq, type(fq))
    client.table = lambda name: fq if name == "project_metro_settings" else FakeQuery(client.table_data.get(name, []), table_name=name, client=client)
    database.db.client = client

    res = database.db.get_project_metro(proj_id, profile_id)
    assert res is not None


def test_get_project_metro_insert_with_string_and_decimal():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    base = {"projects": [{"id": proj_id, "profile_id": profile_id}], "project_metro_settings": []}
    client = FakeClient(base)
    # Simulate DB returning a row for the select path
    row = {"id": uuid4_str(), "project_id": proj_id, "metro_area": "Z", "custom_multiplier": "1.5"}
    fq = FakeQuery(data=[row], table_name="project_metro_settings", client=client)
    client.table = lambda name: fq if name == "project_metro_settings" else FakeQuery(client.table_data.get(name, []), table_name=name, client=client)
    database.db.client = client

    res = database.db.get_project_metro(proj_id, profile_id)
    assert res is not None
    assert getattr(res, "custom_multiplier", None) is not None


def test_get_project_metro_model_instantiation_error_returns_none(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "project_metro_settings": []})
    fq = FakeQuery(data=[], table_name="project_metro_settings", client=client)

    def insert_row(self, data):
        row = dict(data)
        row.setdefault("id", uuid4_str())
        self._data = [row]
        return self

    fq.insert = insert_row.__get__(fq, type(fq))
    client.table = lambda name: fq if name == "project_metro_settings" else FakeQuery(client.table_data.get(name, []), table_name=name, client=client)
    database.db.client = client

    # Make ProjectMetroSetting constructor raise ValueError
    monkeypatch.setattr(database, "ProjectMetroSetting", lambda *a, **k: (_ for _ in ()).throw(ValueError("sim")))

    res = database.db.get_project_metro(proj_id, profile_id)
    assert res is None


def test_get_project_metro_unexpected_error_raises():
    class ExplodingClient(FakeClient):
        def table(self, name):
            raise RuntimeError("boom")

    database.db.client = ExplodingClient({"projects": [{"id": uuid4_str(), "profile_id": uuid4_str()}]})

    with pytest.raises(database.DatabaseError):
        database.db.get_project_metro(uuid4_str(), uuid4_str())


def test_get_project_metro_response_non_dict_triggers_data_error():
    # ownership ok but response.data[0] is not a dict -> should be caught and return None
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}]})

    # Create a FakeQuery whose execute returns a non-dict row (SimpleNamespace)
    fq = FakeQuery(data=[SimpleNamespace()], table_name="project_metro_settings", client=client)
    client.table = lambda name: fq if name == "project_metro_settings" else FakeQuery(client.table_data.get(name, []), table_name=name, client=client)
    database.db.client = client

    res = database.db.get_project_metro(proj_id, profile_id)
    assert res is None


def test_get_project_metro_response_none_item_triggers_type_error():
    # ownership ok but response.data contains None -> ProjectMetroSetting(**None) should raise TypeError and be caught
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}]})

    fq = FakeQuery(data=[None], table_name="project_metro_settings", client=client)
    client.table = lambda name: fq if name == "project_metro_settings" else FakeQuery(client.table_data.get(name, []), table_name=name, client=client)
    database.db.client = client

    res = database.db.get_project_metro(proj_id, profile_id)
    assert res is None


def test_get_project_metro_execute_raises_attribute_error():
    # Force execute() to raise AttributeError so the data-error except branch runs
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    class BrokenQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise AttributeError("simulated execute error")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "projects":
                return FakeQuery(data=[{"id": proj_id, "profile_id": profile_id}], table_name="projects", client=self)
            return BrokenQuery()

    database.db.client = BrokenClient({})
    res = database.db.get_project_metro(proj_id, profile_id)
    assert res is None
