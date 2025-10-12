# The project consolidates domain models in the top-level `backend/models.py`.
# Some earlier code assumed split files like meeting_models.py which are not
# present. Import the relevant classes from the central models module instead.
from models import (
    Communication,
    CommunicationCreate,
    CommunicationUpdate,
    MediaFile,
    MediaFileCreate,
    MediaFileUpdate,
    Meeting,
    MeetingCreate,
    MeetingUpdate,
)

from .auth_models import ErrorResponse, LoginRequest, TokenResponse
from .user_models import User

__all__ = [
    "LoginRequest",
    "TokenResponse",
    "ErrorResponse",
    "User",
    "Meeting",
    "MeetingCreate",
    "MeetingUpdate",
    "Communication",
    "CommunicationCreate",
    "CommunicationUpdate",
    "MediaFile",
    "MediaFileCreate",
    "MediaFileUpdate",
]
