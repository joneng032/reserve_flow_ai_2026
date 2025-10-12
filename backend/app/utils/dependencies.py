from app.repositories.auth_repository import AuthRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.token_service import TokenService
from app.services.user_service import UserService
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Configuración de seguridad
# Use auto_error=False so we can standardize 401 + WWW-Authenticate responses
# rather than allowing the security dependency to raise its own HTTPExceptions
# with potentially differing headers/status codes.
security = HTTPBearer(auto_error=False)


def get_auth_repository():
    """Dependency para repositorio de autenticación"""
    return AuthRepository()


def get_user_repository():
    """Dependency para repositorio de usuarios"""
    return UserRepository()


def get_token_service():
    """Dependency para servicio de tokens"""
    return TokenService()


def get_auth_service(
    auth_repo=Depends(get_auth_repository),
    user_repo=Depends(get_user_repository),
    token_service=Depends(get_token_service),
) -> AuthService:
    """Dependency para servicio de autenticación"""
    return AuthService(auth_repo, user_repo, token_service)


def get_user_service(user_repo=Depends(get_user_repository)) -> UserService:
    """Dependency para servicio de usuarios"""
    return UserService(user_repo)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> str:
    """
    Dependency para obtener usuario actual desde token JWT
    """
    # When HTTPBearer is used with auto_error=False, credentials may be None.
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        username = auth_service.validate_token(credentials.credentials)
        return username
    except ValueError as e:
        # Token validation failed — normalize to 401 with WWW-Authenticate
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
