from backend.app.repositories.auth_repository import AuthRepository


def test_auth_repository_validate_and_manage_credentials():
    repo = AuthRepository()

    # Default test_user/test_password come from settings; ensure validate works
    creds = repo.get_user_credentials()
    assert isinstance(creds, dict)

    # Add a new user and validate
    repo.add_user_credentials("abc", "pwd")
    assert repo.validate_credentials("abc", "pwd")

    # Wrong password
    assert not repo.validate_credentials("abc", "wrong")

    # Remove user
    assert repo.remove_user_credentials("abc")
    assert not repo.remove_user_credentials("does-not-exist")
