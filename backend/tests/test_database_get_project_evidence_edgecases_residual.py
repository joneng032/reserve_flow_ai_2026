import pytest
from backend import database
from backend.tests.conftest import FakeClient, uuid4_str


def test_get_project_evidence_data_error():
    class BrokenQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def order(self, *a, **kw):
            return self

        def range(self, *a, **kw):
            return self

        def execute(self):
            raise AttributeError("bad data")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "projects":
                return FakeClient({}).table(name)
            if name == "evidence":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    assert database.db.get_project_evidence(uuid4_str(), uuid4_str()) == []


def test_get_project_evidence_unexpected_exception_raises_database_error():
    class ExplodingQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            # used for the ownership check; return a passing project
            return type("R", (), {"data": [{"id": "p1", "profile_id": "u1"}]})()

        def order(self, *a, **kw):
            return self

        def range(self, *a, **kw):
            return self

        def delete(self):
            return self

        def insert(self, data):
            return self

        def execute_failing(self):
            raise Exception("boom")

    class ExplodingClient(FakeClient):
        def table(self, name):
            if name == "projects":
                return FakeClient({"projects": [{"id": "p1", "profile_id": "u1"}]}).table(name)
            if name == "evidence":
                # ownership check will call select/eq/execute, then subsequent chain should raise
                class Q(ExplodingQuery):
                    def execute(self):
                        # first execute is ownership check returning data
                        return type("R", (), {"data": [{"id": "e1", "project_id": "p1", "evidence_type": "photo"}]})()

                    def range(self, *a, **kw):
                        return self

                    def order(self, *a, **kw):
                        return self

                    def execute(self):
                        # subsequent execute for the data fetch will raise
                        raise Exception("boom")

                return Q()
            return FakeClient({}).table(name)

    database.db.client = ExplodingClient({})
    with pytest.raises(database.DatabaseError):
        database.db.get_project_evidence("p1", "u1")


def test_get_evidence_data_error():
    class BrokenQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            raise AttributeError("bad data")

    class BrokenClient(FakeClient):
        def table(self, name):
            if name == "evidence":
                return BrokenQuery()
            return FakeClient({}).table(name)

    database.db.client = BrokenClient({})
    assert database.db.get_evidence(uuid4_str(), uuid4_str()) is None


def test_get_evidence_unexpected_exception_raises_database_error():
    class ExplodingQuery:
        def select(self, *a, **kw):
            return self

        def eq(self, *a, **kw):
            return self

        def execute(self):
            # ownership check returns a row
            return type("R", (), {"data": [{"id": "e1", "project_id": "p1", "projects": {"profile_id": "u1"}}]})()

        def execute_failing(self):
            raise Exception("boom")

    class ExplodingClient(FakeClient):
        def table(self, name):
            if name == "evidence":
                class Q(ExplodingQuery):
                    def execute(self):
                        # first execute returns ownership row
                        return type("R", (), {"data": [{"id": "e1", "project_id": "p1", "projects": {"profile_id": "u1"}}]})()

                    def eq(self, *a, **kw):
                        return self

                    def select(self, *a, **kw):
                        return self

                    def execute(self):
                        # subsequent action raises
                        raise Exception("boom")

                return Q()
            return FakeClient({}).table(name)

    database.db.client = ExplodingClient({})
    with pytest.raises(database.DatabaseError):
        database.db.get_evidence("e1", "u1")
