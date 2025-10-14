from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    """
    Modelo de usuario
    """

    id: Optional[int] = Field(None, description="ID del usuario")
    username: str = Field(..., description="Nombre de usuario")
    email: Optional[str] = Field(None, description="Email del usuario")
    is_active: bool = Field(default=True, description="Estado activo del usuario")
    created_at: Optional[datetime] = Field(None, description="Fecha de creación")

    model_config = ConfigDict(from_attributes=True)
