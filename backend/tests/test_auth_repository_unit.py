from app.repositories.auth_repository import AuthRepository


def test_validate_and_get_credentials_and_helpers():
    repo = AuthRepository()
    repo.clear_credentials()

    # initially empty
    assert repo.get_user_credentials() == {}

    # add credentials and validate
    repo.add_user_credentials("alice", "pw")
    assert repo.validate_credentials("alice", "pw") is True
    assert repo.validate_credentials("alice", "wrong") is False

    # remove and check
    assert repo.remove_user_credentials("alice") is True
    assert repo.remove_user_credentials("alice") is False

    # set store replacement
    repo.set_credentials_store({"bob": "bpw"})
    creds = repo.get_user_credentials()
    assert "bob" in creds and creds["bob"] == "bpw"
