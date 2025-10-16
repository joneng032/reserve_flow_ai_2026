import pytest

from backend import database
from backend.tests.conftest import FakeClient, FakeQuery, uuid4_str


def test_delete_communication_client_none():
    database.db.client = None
    assert database.db.delete_communication(uuid4_str(), uuid4_str()) is False


def test_delete_communication_ownership_negative():
    database.db.client = FakeClient({"communications": []})
    assert database.db.delete_communication(uuid4_str(), uuid4_str()) is False


def test_delete_communication_success_and_audit(monkeypatch):
    comm_id = uuid4_str()
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    # communication_check returns a row with project_id and joined project
    client = FakeClient({
        "communications": [{"id": comm_id, "project_id": proj_id}],
        "projects": [{"id": proj_id, "profile_id": profile_id}],
    })
    database.db.client = client

    seen = []
    monkeypatch.setattr(database.db, "create_audit_log", lambda a: seen.append(a))

    result = database.db.delete_communication(comm_id, profile_id)
    assert result is True
    assert len(seen) == 1


def test_delete_communication_empty_delete_returns_false():
    comm_id = uuid4_str()
    proj_id = uuid4_str()
    profile_id = uuid4_str()
    client = FakeClient({
        "communications": [{"id": comm_id, "project_id": proj_id}],
        "projects": [{"id": proj_id, "profile_id": profile_id}],
        # simulate a delete that returns no rows
        "deleted_rows": [],
    })

    # Override table behavior: communications.delete().eq(...).execute() returns empty
    class EmptyDeleteQuery(FakeQuery):
        def delete(self):
            self._data = []
            return self

    class EmptyDeleteClient(FakeClient):
        def table(self, name):
            if name == "projects":
                return FakeQuery(data=[{"id": proj_id, "profile_id": profile_id}], table_name="projects", client=self)
            if name == "communications":
                return EmptyDeleteQuery(data=[{"id": comm_id, "project_id": proj_id}], table_name=name, client=self)
            return FakeQuery(data=[], table_name=name, client=self)

    database.db.client = EmptyDeleteClient({})
    assert database.db.delete_communication(comm_id, profile_id) is False


def test_delete_communication_data_error_returns_false():
    comm_id = uuid4_str()
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
    assert database.db.delete_communication(comm_id, profile_id) is False


def test_delete_communication_unexpected_exception_raises_database_error():
    comm_id = uuid4_str()
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    class ExplodingQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def delete(self):
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
        database.db.delete_communication(comm_id, profile_id)
import pytest
from backend import database
from backend.tests.conftest import FakeClient, FakeQuery, uuid4_str
from backend.models import AuditLogCreate


def test_delete_communication_ownership_negative():
    # If the communications join returns no rows, deletion should be denied
    database.db.client = FakeClient({"communications": []})
    res = database.db.delete_communication(uuid4_str(), uuid4_str())
    assert res is False


def test_delete_communication_success_creates_audit(monkeypatch):
    comm_id = uuid4_str()
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    # communication exists and ownership ok
    com_row = {"id": comm_id, "project_id": proj_id, "communication_type": "email"}
    base = {"communications": [com_row], "projects": [{"id": proj_id, "profile_id": profile_id}]}
    client = FakeClient(base)

    # communication_check should return the row with project join info
    cq = FakeQuery(data=[{"project_id": proj_id, "projects": {"profile_id": profile_id}}], table_name="communications", client=client)

    # delete should return the deleted row
    dq = FakeQuery(data=[com_row], table_name="communications", client=client)

    # Build a combined table object that returns `cq` for select flows and `dq` for delete flows
    class CombinedQuery:
        def __init__(self, cq_obj, dq_obj):
            self._cq = cq_obj
            self._dq = dq_obj

        def select(self, *a, **kw):
            return self._cq.select(*a, **kw)

        def eq(self, *a, **kw):
            # eq will be called on the returned select() chain; delegate to cq
            return self._cq.eq(*a, **kw)

        def execute(self):
            # execute after select() should delegate to cq
            return self._cq.execute()

        def delete(self):
            # delete path should delegate to dq (which supports eq/execute)
            return self._dq

    # Create a single query object that returns ownership data on select/execute,
    # and returns delete-data when delete() is invoked.
    class SingleCommQuery:
        def __init__(self, check_rows, delete_rows):
            self._check = check_rows
            self._delete = delete_rows
            self._deleted = False

        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def delete(self):
            self._deleted = True
            return self

        def execute(self):
            return FakeQuery(data=(self._delete if self._deleted else self._check), table_name="communications", client=client).execute()

    client.table = lambda name: SingleCommQuery([{"project_id": proj_id, "projects": {"profile_id": profile_id}}], [com_row]) if name == "communications" else FakeQuery(client.table_data.get(name, []), table_name=name, client=client)
    database.db.client = client

    created = []
    monkeypatch.setattr(database.db, "create_audit_log", lambda a: created.append(a))

    res = database.db.delete_communication(comm_id, profile_id)
    assert res is True
    assert len(created) == 1
    # verify audit basic fields captured (AuditLogCreate may not persist 'details')
    aud: AuditLogCreate = created[0]
    assert aud.entity_type == "communication"
    assert str(aud.entity_id) == comm_id
    assert aud.action == "delete"


def test_delete_communication_delete_returns_empty():
    # Ownership ok but delete returns no rows -> should return False
    comm_id = uuid4_str()
    proj_id = uuid4_str()
    profile_id = uuid4_str()

    client = FakeClient({"communications": [{"id": comm_id, "project_id": proj_id}], "projects": [{"id": proj_id, "profile_id": profile_id}]})
    # create a query that returns empty on delete
    fq = FakeQuery(data=[{"project_id": proj_id, "projects": {"profile_id": profile_id}}], table_name="communications", client=client)

    def delete_empty(self):
        self._data = []
        return self

    fq.delete = delete_empty.__get__(fq, type(fq))
    client.table = lambda name: fq if name == "communications" else FakeQuery(client.table_data.get(name, []), table_name=name, client=client)
    database.db.client = client

    res = database.db.delete_communication(comm_id, profile_id)
    assert res is False


def test_delete_communication_unexpected_error_raises():
    class ExplodingClient(FakeClient):
        def table(self, name):
            raise RuntimeError("boom")

    database.db.client = ExplodingClient({"communications": [{"id": uuid4_str(), "project_id": uuid4_str()}]})

    with pytest.raises(database.DatabaseError):
        database.db.delete_communication(uuid4_str(), uuid4_str())


def test_delete_communication_client_none_explicit():
    # Explicit client None (mock-mode) should return False early
    database.db.client = None
    assert database.db.delete_communication(uuid4_str(), uuid4_str()) is False


def test_delete_communication_data_error_returns_false():
    # Simulate a data-shape error (AttributeError) during the ownership check
    class BrokenQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise AttributeError("simulated data error")

    class BrokenClient(FakeClient):
        def table(self, name):
            return BrokenQuery()

    database.db.client = BrokenClient({})
    # The function should catch AttributeError and return False
    assert database.db.delete_communication(uuid4_str(), uuid4_str()) is False
