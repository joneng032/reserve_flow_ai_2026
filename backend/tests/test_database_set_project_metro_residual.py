import pytest
from decimal import Decimal

from backend import database
from backend.models import ProjectMetroSettingCreate, ProjectMetroSetting
from backend.tests.conftest import FakeClient, FakeQuery, uuid4_str


def test_set_project_metro_client_none():
    database.db.client = None
    res = database.db.set_project_metro(uuid4_str(), ProjectMetroSettingCreate(project_id=uuid4_str(), metro_area="A", custom_multiplier=Decimal("1.0")), uuid4_str())
    assert res is None


def test_set_project_metro_ownership_negative():
    database.db.client = FakeClient({"projects": []})
    res = database.db.set_project_metro(uuid4_str(), ProjectMetroSettingCreate(project_id=uuid4_str(), metro_area="A", custom_multiplier=Decimal("1.0")), uuid4_str())
    assert res is None


def test_set_project_metro_create_new():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    # projects exists, but no existing metro settings
    client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "project_metro_settings": []})
    database.db.client = client

    data = ProjectMetroSettingCreate(project_id=proj_id, metro_area="MetroX", custom_multiplier=Decimal("1.23"))
    res = database.db.set_project_metro(proj_id, data, profile_id)
    assert isinstance(res, ProjectMetroSetting)
    assert str(res.project_id) == proj_id


def test_set_project_metro_update_existing():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    # Simulate an existing metro setting row
    existing_row = {"id": uuid4_str(), "project_id": proj_id, "metro_area": "Old", "custom_multiplier": Decimal("1.0")}
    client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "project_metro_settings": [existing_row]})
    database.db.client = client

    data = ProjectMetroSettingCreate(project_id=proj_id, metro_area="NewMetro", custom_multiplier=Decimal("1.5"))
    res = database.db.set_project_metro(proj_id, data, profile_id)
    assert isinstance(res, ProjectMetroSetting)
    assert str(res.project_id) == proj_id


def test_set_project_metro_response_empty_returns_none():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    class EmptyResponseQuery(FakeQuery):
        def insert(self, data):
            # set no data to simulate empty response
            self._data = []
            return self

        def update(self, data):
            self._data = []
            return self

    class EmptyResponseClient(FakeClient):
        def table(self, name):
            if name == "projects":
                return FakeQuery(data=[{"id": proj_id, "profile_id": profile_id}], table_name="projects", client=self)
            return EmptyResponseQuery(data=[], table_name=name, client=self)

    database.db.client = EmptyResponseClient({})
    data = ProjectMetroSettingCreate(project_id=proj_id, metro_area="M", custom_multiplier=Decimal("1.0"))
    res = database.db.set_project_metro(proj_id, data, profile_id)
    assert res is None


def test_set_project_metro_data_error_returns_none():
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
    data = ProjectMetroSettingCreate(project_id=proj_id, metro_area="M", custom_multiplier=Decimal("1.0"))
    res = database.db.set_project_metro(proj_id, data, profile_id)
    assert res is None


def test_set_project_metro_unexpected_exception_raises_database_error():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    class ExplodingQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def insert(self, *a, **kw):
            return self

        def update(self, *a, **kw):
            return self

        def execute(self):
            raise Exception("boom")

    class ExplodingClient(FakeClient):
        def table(self, name):
            if name == "projects":
                return FakeQuery(data=[{"id": proj_id, "profile_id": profile_id}], table_name="projects", client=self)
            return ExplodingQuery()

    database.db.client = ExplodingClient({})
    data = ProjectMetroSettingCreate(project_id=proj_id, metro_area="M", custom_multiplier=Decimal("1.0"))
    with pytest.raises(database.DatabaseError):
        database.db.set_project_metro(proj_id, data, profile_id)
from decimal import Decimal
import pytest

from backend import database
from backend.models import ProjectMetroSettingCreate, ProjectMetroSetting
from backend.tests.conftest import FakeClient, FakeQuery, uuid4_str


def test_set_project_metro_client_none():
    database.db.client = None
    res = database.db.set_project_metro(uuid4_str(), ProjectMetroSettingCreate(metro_area="A", project_id=uuid4_str()), uuid4_str())
    assert res is None


def test_set_project_metro_ownership_negative():
    database.db.client = FakeClient({"projects": []})
    res = database.db.set_project_metro(uuid4_str(), ProjectMetroSettingCreate(metro_area="A", project_id=uuid4_str()), uuid4_str())
    assert res is None


def test_set_project_metro_create_new():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    metro = ProjectMetroSettingCreate(metro_area="MetroX", custom_multiplier=Decimal("1.25"), project_id=proj_id)
    client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "project_metro_settings": []})
    database.db.client = client

    res = database.db.set_project_metro(proj_id, metro, profile_id)
    assert isinstance(res, ProjectMetroSetting)
    assert getattr(res, "metro_area", None) == "MetroX"


def test_set_project_metro_update_existing():
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    # existing row present
    existing = {"id": uuid4_str(), "project_id": proj_id, "metro_area": "Old", "custom_multiplier": Decimal("1.0")}
    metro = ProjectMetroSettingCreate(metro_area="NewArea", custom_multiplier=Decimal("1.5"), project_id=proj_id)
    client = FakeClient({"projects": [{"id": proj_id, "profile_id": profile_id}], "project_metro_settings": [existing]})
    database.db.client = client

    res = database.db.set_project_metro(proj_id, metro, profile_id)
    assert isinstance(res, ProjectMetroSetting)
    assert getattr(res, "metro_area", None) == "NewArea"


def test_set_project_metro_raises_database_error():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    class ExplodingQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def update(self, *a, **kw):
            return self

        def insert(self, *a, **kw):
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
        database.db.set_project_metro(proj_id, ProjectMetroSettingCreate(metro_area="X", project_id=proj_id), profile_id)
import pytest
from backend import database
from backend.models import ProjectMetroSettingCreate
from backend.tests.conftest import FakeClient, FakeQuery, uuid4_str


def test_set_project_metro_projects_missing_returns_none():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    # projects table empty -> ownership negative path (should return None)
    database.db.client = FakeClient({"projects": [], "project_metro_settings": []})
    res = database.db.set_project_metro(proj_id, ProjectMetroSettingCreate(metro_area="X", project_id=proj_id), profile_id)
    assert res is None


def test_set_project_metro_insert_returns_model_success():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    # ownership ok, no existing metro -> insert returns a row and should return a model
    base = {"projects": [{"id": proj_id, "profile_id": profile_id}], "project_metro_settings": []}
    client = FakeClient(base)

    fq = FakeQuery(data=[], table_name="project_metro_settings", client=client)

    def insert_row(self, data):
        row = dict(data)
        row.setdefault("id", uuid4_str())
        self._data = [row]
        return self

    fq.insert = insert_row.__get__(fq, type(fq))

    client.table = lambda name: fq if name == "project_metro_settings" else FakeQuery(client.table_data.get(name, []), table_name=name, client=client)
    database.db.client = client

    res = database.db.set_project_metro(proj_id, ProjectMetroSettingCreate(metro_area="AreaZ", project_id=proj_id), profile_id)
    assert res is not None
    assert getattr(res, "metro_area", None) == "AreaZ"


def test_set_project_metro_model_instantiation_attribute_error_returns_none(monkeypatch):
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    # ownership ok, insert returns a row but constructing the model raises AttributeError
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

    # Make ProjectMetroSetting raise AttributeError when called
    monkeypatch.setattr(database, "ProjectMetroSetting", lambda *a, **k: (_ for _ in ()).throw(AttributeError("simulated")))

    res = database.db.set_project_metro(proj_id, ProjectMetroSettingCreate(metro_area="Bad", project_id=proj_id), profile_id)
    assert res is None


def test_set_project_metro_unexpected_exception_is_database_error():
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    class ExplodingClient(FakeClient):
        def table(self, name):
            raise RuntimeError("simulated client boom")

    database.db.client = ExplodingClient({"projects": [{"id": proj_id, "profile_id": profile_id}]})

    with pytest.raises(database.DatabaseError):
        database.db.set_project_metro(proj_id, ProjectMetroSettingCreate(metro_area="Z", project_id=proj_id), profile_id)
