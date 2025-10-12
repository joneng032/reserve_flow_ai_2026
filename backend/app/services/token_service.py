import base64
import binascii
import hashlib
import hmac
import json
import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

# Defer imports from `jose` (which may load native crypto backends) into
# the functions that actually need them. This avoids importing heavy
# native libraries at module import time which can cause test collection
# failures on some platforms (see README/testing notes).
from app.config.settings import get_settings


class ITokenStrategy(ABC):
    """
    Interfaz para estrategias de generación de tokens
    """

    @abstractmethod
    def create_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """Crear token usando la estrategia específica"""
        raise NotImplementedError()

    @abstractmethod
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verificar token usando la estrategia específica"""
        raise NotImplementedError()


class JWTTokenStrategy(ITokenStrategy):
    """
    Estrategia para tokens JWT
    """

    def __init__(self):
        self.settings = get_settings()

    def create_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """Crear token JWT"""
        # Import here to avoid importing cryptography-backed dependencies at
        # module import time which can cause Windows-specific failures in some
        # CI/test environments.
        from jose import jwt

        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.settings.access_token_expire_minutes
            )

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, self.settings.secret_key, algorithm=self.settings.algorithm
        )
        return encoded_jwt

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verificar token JWT"""
        from jose import jwt
        from jose.exceptions import JWTError

        try:
            payload = jwt.decode(
                token, self.settings.secret_key, algorithms=[self.settings.algorithm]
            )
            return payload
        except JWTError as exc:
            # Preserve exception chaining so callers can inspect original causes when needed
            raise ValueError("Token inválido") from exc


class SimpleJWTStrategy(ITokenStrategy):
    """
    Minimal JWT strategy implemented using HMAC-SHA256 and the Python
    standard library only. Intended as a fallback for test and constrained
    environments where `python-jose` or native crypto backends are not
    available. This implementation is intentionally small and only supports
    the features required in tests (HS256, `exp` claim).
    """

    def __init__(self):
        self.settings = get_settings()

    @staticmethod
    def _b64u_encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

    @staticmethod
    def _b64u_decode(s: str) -> bytes:
        pad = "=" * ((4 - len(s) % 4) % 4)
        return base64.urlsafe_b64decode(s + pad)

    def create_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        header = {"alg": "HS256", "typ": "JWT"}
        to_encode = dict(data)
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.settings.access_token_expire_minutes
            )

        to_encode.update({"exp": int(expire.timestamp())})

        header_b = json.dumps(header, separators=(",", ":")).encode("utf-8")
        payload_b = json.dumps(to_encode, separators=(",", ":")).encode("utf-8")
        signing_input = (
            f"{self._b64u_encode(header_b)}.{self._b64u_encode(payload_b)}".encode(
                "ascii"
            )
        )

        sig = hmac.new(
            self.settings.secret_key.encode("utf-8"), signing_input, hashlib.sha256
        ).digest()
        return signing_input.decode("ascii") + "." + self._b64u_encode(sig)

    def verify_token(self, token: str) -> Dict[str, Any]:
        try:
            header_b64, payload_b64, sig_b64 = token.split(".")
        except ValueError as exc:
            # Preserve chaining to aid debugging callers while normalizing
            # the public error type for callers of the strategy.
            raise ValueError("Token inválido") from exc

        signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
        expected_sig = hmac.new(
            self.settings.secret_key.encode("utf-8"), signing_input, hashlib.sha256
        ).digest()

        try:
            sig = self._b64u_decode(sig_b64)
        except (binascii.Error, TypeError) as e:
            # Narrowly catch base64-related decoding errors only. Other
            # unexpected exceptions should propagate so callers/tests can
            # detect genuine platform issues.
            raise ValueError("Token inválido") from e

        if not hmac.compare_digest(expected_sig, sig):
            raise ValueError("Token inválido")

        try:
            payload_bytes = self._b64u_decode(payload_b64)
            payload = json.loads(payload_bytes)
        except (binascii.Error, TypeError, json.JSONDecodeError) as e:
            # Catch only payload-related decoding/parsing errors and
            # normalize them to a ValueError indicating an invalid token.
            raise ValueError("Token inválido") from e

        exp = payload.get("exp")
        if exp is None:
            raise ValueError("Token inválido")
        if datetime.utcnow().timestamp() > float(exp):
            raise ValueError("Token inválido")

        return payload


class TokenService:
    """
    Servicio de tokens usando el patrón Factory y Strategy
    """

    def __init__(self, strategy: ITokenStrategy = None):
        # Allow tests and CI to opt-in to a pure-Python JWT implementation
        # by setting USE_SIMPLE_JWT=1 in the environment. This avoids
        # importing native crypto-backed libraries during test execution.
        use_simple = str(os.getenv("USE_SIMPLE_JWT", "")).lower() in (
            "1",
            "true",
            "yes",
        )
        if strategy is not None:
            self.strategy = strategy
        elif use_simple:
            self.strategy = SimpleJWTStrategy()
        else:
            self.strategy = JWTTokenStrategy()
        self.settings = get_settings()

    def create_access_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """Crear token de acceso"""
        return self.strategy.create_token(data, expires_delta)

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verificar token"""
        return self.strategy.verify_token(token)

    def create_user_token(
        self, username: str, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Crear token para usuario específico"""
        data = {"sub": username}
        if expires_delta:
            return self.create_access_token(data, expires_delta)
        else:
            return self.create_access_token(
                data, timedelta(minutes=self.settings.access_token_expire_minutes)
            )

    def get_token_payload(self, token: str) -> Dict[str, Any]:
        """Obtener payload del token"""
        return self.verify_token(token)

    def get_username_from_token(self, token: str) -> str:
        """Obtener nombre de usuario desde token"""
        payload = self.get_token_payload(token)
        username = payload.get("sub")
        if username is None:
            raise ValueError("Token no contiene información de usuario")
        return username
