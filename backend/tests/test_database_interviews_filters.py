from backend.database import Database


def test_get_project_interviews_filters():
    from backend.tests.conftest import FakeClient, uuid4_str

    pid = uuid4_str()
    i1 = {"id": uuid4_str(), "project_id": pid, "interview_type": "initial", "status": "scheduled", "interviewee_name": "A"}
    i2 = {"id": uuid4_str(), "project_id": pid, "interview_type": "follow_up", "status": "completed", "interviewee_name": "B"}

    client = FakeClient(table_data={
        "projects": [{"id": pid, "profile_id": "profile-1"}],
        "interviews": [i1, i2],
    })

    db = Database()
    db.client = client

    res = db.get_project_interviews(pid, "profile-1", interview_type="initial")
    assert len(res) == 1
    assert getattr(res[0], "interview_type", None) == "initial"
