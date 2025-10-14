import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

# Cargar variables de entorno
load_dotenv()


class Settings(BaseSettings):
    """
    Configuración de la aplicación usando el patrón Singleton
    """

    # Configuración de JWT
    secret_key: str = os.getenv(
        "SECRET_KEY", "tu_clave_secreta_super_segura_aqui_cambiala_en_produccion"
    )
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    # Configuración del servidor
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "3000"))

    # Credenciales de prueba
    test_user: str = os.getenv("TEST_USER", "root")
    test_password: str = os.getenv("TEST_PASSWORD", "1234")

    # Configuración de la aplicación
    app_title: str = "API de Autenticación"
    app_version: str = "1.0.0"

    model_config = ConfigDict(env_file=".env", case_sensitive=False, extra="allow")


# Instancia singleton de configuración
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the singleton Settings instance using an lru cache.

    This replaces the previous global-backed implementation which
    triggered static-analysis warnings about the use of `global`.
    lru_cache provides the same memoization semantics with a clearer
    intent and no global state mutation.
    """
    return Settings()
