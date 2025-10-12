from typing import Optional, Tuple

from app.models.auth_models import LoginRequest, TokenResponse
from app.repositories.auth_repository import AuthRepository, IAuthRepository
from app.repositories.user_repository import IUserRepository, UserRepository
from app.services.token_service import TokenService


class AuthService:
    """
    Servicio de autenticación usando el patrón Service

    Behavior:
    - authenticate_user will catch expected validation/data errors (ValueError, TypeError, KeyError, AttributeError)
      and return a controlled failure tuple. Unexpected exceptions (e.g., repository/DB failures) will propagate
      to callers so higher layers (API or tests) can observe and handle them appropriately.
    """

    def __init__(
        self,
        auth_repository: Optional[IAuthRepository] = None,
        user_repository: Optional[IUserRepository] = None,
        token_service: Optional[TokenService] = None,
    ):
        self.auth_repository = auth_repository or AuthRepository()
        self.user_repository = user_repository or UserRepository()
        self.token_service = token_service or TokenService()

    def authenticate_user(
        self, login_data: LoginRequest
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Autenticar usuario y retornar (éxito, token, mensaje)

        Note: only expected validation/data errors are handled here. Unexpected
        errors are allowed to bubble up so callers (and tests) can assert
        propagation behavior.
        """
        # Validate credentials; repository methods may raise ValueError for
        # expected data issues which we handle locally. Allow other
        # runtime errors to propagate.
        is_valid = None
        try:
            is_valid = self.auth_repository.validate_credentials(
                login_data.user, login_data.pass_
            )
        except (ValueError, TypeError, KeyError, AttributeError) as e:
            return False, None, f"Error de autenticación: {str(e)}"

        if not is_valid:
            return False, None, "Credenciales incorrectas"

        # Verify the user exists
        user = self.user_repository.get_user_by_username(login_data.user)
        if not user:
            return False, None, "Usuario no encontrado"

        if not user.is_active:
            return False, None, "Usuario inactivo"

        # Generate token
        token = self.token_service.create_user_token(login_data.user)

        return True, token, "Login exitoso"

    def login(self, login_data: LoginRequest) -> TokenResponse:
        """
        Proceso completo de login
        """
        success, token, message = self.authenticate_user(login_data)

        if not success:
            raise ValueError(message)

        # Token and message are guaranteed when success is True; assert for type checkers
        assert token is not None
        assert message is not None
        return TokenResponse(access_token=token, token_type="bearer", message=message)

    def validate_token(self, token: str) -> str:
        """
        Validar token y retornar nombre de usuario

        This method is intentionally letting unexpected errors (e.g., repo/DB
        RuntimeError) bubble up so that callers and tests can observe them and
        distinguish them from token/validation errors which raise ValueError.
        """
        username = self.token_service.get_username_from_token(token)

        # Verificar que el usuario existe y está activo
        user = self.user_repository.get_user_by_username(username)
        if not user or not user.is_active:
            raise ValueError("Usuario no válido")

        return username
        # Let unexpected errors propagate (e.g., DB issues)

    def get_user_info(self, username: str):
        """
        Obtener información del usuario
        """
        user = self.user_repository.get_user_by_username(username)
        if not user:
            raise ValueError("Usuario no encontrado")
        return user
