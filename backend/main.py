import os
from typing import Any, Dict, List, Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr

from backend.app.services.token_service import TokenService

# Import our database module (package-qualified imports are used across the
# test-suite and application; tests insert the repo root on sys.path when
# necessary so the package imports work during test collection.)
from backend.database import DatabaseError, db

# Import our new models (local import; kept after sys.path manipulation)
from backend.models import (  # noqa: E402
    AuditLog,
    Category,
    CategoryCreate,
    CategoryUpdate,
    Communication,
    CommunicationCreate,
    CommunicationUpdate,
    Component,
    ComponentCatalog,
    ComponentCreate,
    ComponentUpdate,
    ComponentWithTags,
    CostAnalysis,
    Evidence,
    EvidenceCreate,
    EvidenceUpdate,
    Inspection,
    InspectionCreate,
    InspectionItem,
    InspectionItemCreate,
    InspectionItemUpdate,
    InspectionUpdate,
    Interview,
    InterviewCreate,
    InterviewUpdate,
    MediaFile,
    MediaFileCreate,
    MediaFileUpdate,
    Meeting,
    MeetingCreate,
    MeetingUpdate,
    MetroMultiplier,
    Project,
    ProjectCreate,
    ProjectMetroSetting,
    ProjectMetroSettingCreate,
    ProjectUpdate,
    ProjectWithDetails,
    ReserveAnalysis,
)

# Decimal and uuid are not required at module import time in this file;
# database layer handles numeric and UUID operations where needed.


# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="Reserve Flow AI API",
    version="2.0.0",
    description="Professional Reserve Study Management API",
)

# Enhanced CORS configuration
# Configure CORS origins from environment for safer deployments. When DEPLOYMENT
# is set to "production" the environment should provide a comma-separated
# list in ALLOWED_ORIGINS. Falling back to sensible localhost defaults for
# development.
allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
if allowed_origins_env:
    allow_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
else:
    allow_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
    expose_headers=["*"],
    max_age=86400,  # 24 hours
)


# Modelos Pydantic
class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    username: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class RegisterResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict
    message: str


class ProtectedResponse(BaseModel):
    message: str
    user_info: dict


# Simulación de base de datos en memoria
users_db = {}

# Configuración JWT
# Prefer canonical env `JWT_SECRET`. Fall back to legacy `JWT_SECRET_KEY`
# for backward compatibility to avoid breaking existing setups immediately.
JWT_SECRET = os.getenv("JWT_SECRET", os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production"))
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_jwt_token(user_id: str, email: str, username: str) -> str:
    """Create a JWT using the configured TokenService.

    The TokenService will select a pure-Python fallback strategy when
    `USE_SIMPLE_JWT` is set in the environment which prevents importing
    native crypto libraries during test runs or in constrained CI.
    """
    svc = TokenService()
    payload = {"sub": str(user_id), "email": email, "username": username}
    # TokenService will apply expiration automatically according to settings
    return svc.create_access_token(payload)


def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify token using the TokenService.

    Returns a user-like dict on success or None when token is invalid or
    expired. ValueError is used by token strategies to indicate invalid
    tokens and is mapped to a None return here to keep previous behavior.
    """
    svc = TokenService()
    try:
        payload = svc.verify_token(token)
    except ValueError as e:
        # Token invalid or expired
        print(f"JWT error: {e}")
        return None
    # Do not catch broad Exception here: unexpected errors should propagate
    # to callers so that higher-level monitoring/handlers can surface them
    # (e.g., a runtime error in the token strategy indicates a genuine
    # platform issue that should not be silently converted to 'invalid').

    try:
        return {
            "id": payload["sub"],
            "email": payload.get("email"),
            "username": payload.get("username"),
            "is_active": True,
        }
    except (KeyError, TypeError) as e:
        print(f"Unexpected token payload error verifying token: {e}")
        return None


security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Resolve the current user from the Authorization header.

    Returns HTTP 401 with a WWW-Authenticate: Bearer header when credentials are
    missing or the token is invalid/expired so clients can react appropriately.
    """
    # When HTTPBearer is used with auto_error=False, credentials may be None.
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    user = verify_jwt_token(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def ensure_belongs_to_project(
    resource: Any, project_id: str, resource_name: str = "Resource"
):
    """Ensure the given resource belongs to the project_id.

    Raises HTTPException(404) when not found or not matching.
    """
    if resource is None:
        raise HTTPException(status_code=404, detail=f"{resource_name} not found")
    try:
        if str(getattr(resource, "project_id", "")) != project_id:
            raise HTTPException(status_code=404, detail=f"{resource_name} not found")
    except (AttributeError, TypeError) as exc:
        # Normalise attribute and type-related errors into a 404 to avoid leaking internals
        # Preserve original exception chaining to aid debugging.
        raise HTTPException(
            status_code=404, detail=f"{resource_name} not found"
        ) from exc


def safe_db_call(fn, *args, **kwargs):
    """Call a db function and map low-level errors to HTTPException with proper chaining.

    This allows endpoints to avoid repetitive try/except blocks and ensures
    DatabaseError and common data errors are translated to appropriate HTTP
    responses.
    """
    try:
        return fn(*args, **kwargs)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") from e
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        # Treat common data-shape and attribute errors as bad client requests
        raise HTTPException(status_code=400, detail=str(e)) from e
    # Let any other unexpected exceptions propagate to the framework and be
    # handled by FastAPI's error handling (returns a 500). Avoid catching
    # 'Exception' too broadly here so we don't accidentally swallow bugs.


@app.post("/api/register", response_model=RegisterResponse)
async def register(register_data: RegisterRequest):
    print(f"[REGISTER] Received registration request for email: {register_data.email}")

    # Simular registro exitoso
    user_id = "123"
    token = create_jwt_token(user_id, register_data.email, register_data.username)

    # Guardar en "base de datos" simulada
    users_db[register_data.email] = {
        "id": user_id,
        "email": register_data.email,
        "username": register_data.username,
        "password": register_data.password,  # En producción, esto estaría hasheado
        "is_active": True,
    }

    return RegisterResponse(
        access_token=token,
        token_type="bearer",
        user={
            "id": user_id,
            "email": register_data.email,
            "username": register_data.username,
            "is_active": True,
        },
        message="Usuario registrado exitosamente",
    )


@app.post("/api/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    print(f"[LOGIN] Received login request for email: {login_data.email}")

    # Verificar credenciales simuladas
    if login_data.email == "diegof.e3@gmail.com" and login_data.password == "123456789":
        user_id = "123"
        token = create_jwt_token(user_id, login_data.email, "diegof.e3")

        return LoginResponse(
            access_token=token,
            token_type="bearer",
            user={
                "id": user_id,
                "email": login_data.email,
                "username": "diegof.e3",
                "is_active": True,
            },
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas"
        )


@app.get("/api/protected", response_model=ProtectedResponse)
async def get_protected_data(current_user: dict = Depends(get_current_user)):
    return ProtectedResponse(
        message=f"Hola {current_user['username']}, has accedido a datos protegidos",
        user_info={
            "id": current_user["id"],
            "username": current_user["username"],
            "email": current_user["email"],
            "is_active": current_user["is_active"],
        },
    )


@app.get("/api/users", response_model=dict)
async def get_users(current_user: dict = Depends(get_current_user)):
    # current_user is provided by the dependency and used for auth context
    return {"users": [current_user]}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "reserve-flow-ai-api", "version": "2.0.0"}


# Root endpoint defined later in the file with Spanish message; keep only that one.

# ===== PROJECT ENDPOINTS =====


@app.post("/api/projects", response_model=Project)
async def create_project(
    project_data: ProjectCreate, current_user: dict = Depends(get_current_user)
):
    """Create a new project"""
    # If profile_id not included in payload, set it from the authenticated user
    if project_data.profile_id is None:
        project_data.profile_id = current_user["id"]

    project = safe_db_call(db.create_project, project_data)
    if project:
        return project
    # If the DB call completed but returned falsy, treat as a client error
    raise HTTPException(status_code=400, detail="Failed to create project")


@app.get("/api/projects", response_model=List[ProjectWithDetails])
async def get_projects(
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get all projects for the authenticated user"""
    return safe_db_call(db.get_projects, current_user["id"], skip, limit)


@app.put("/api/projects/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update a project"""
    project = safe_db_call(
        db.update_project, project_id, current_user["id"], project_data
    )
    if project:
        return project
    raise HTTPException(status_code=404, detail="Project not found")


@app.delete("/api/projects/{project_id}")
async def delete_project(
    project_id: str, current_user: dict = Depends(get_current_user)
):
    """Delete a project"""
    if safe_db_call(db.delete_project, project_id, current_user["id"]):
        return {"message": "Project deleted successfully"}
    raise HTTPException(status_code=404, detail="Project not found")


# ===== COMPONENT ENDPOINTS =====


@app.post("/api/projects/{project_id}/components", response_model=Component)
async def create_component(
    project_id: str,
    component_data: ComponentCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new component in a project"""
    # Ensure project_id matches the component's project_id
    if str(component_data.project_id) != project_id:
        raise HTTPException(status_code=400, detail="Project ID mismatch")

    component = safe_db_call(db.create_component, component_data, current_user["id"])
    if component:
        return component
    raise HTTPException(status_code=400, detail="Failed to create component")


@app.get(
    "/api/projects/{project_id}/components", response_model=List[ComponentWithTags]
)
async def get_project_components(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    category: Optional[str] = None,
    tag: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get all components for a project"""
    return safe_db_call(
        db.get_project_components,
        project_id,
        current_user["id"],
        category,
        tag,
        skip,
        limit,
    )


@app.put(
    "/api/projects/{project_id}/components/{component_id}", response_model=Component
)
async def update_component(
    project_id: str,  # intentionally unused: kept for RESTful route parity
    component_id: str,
    component_data: ComponentUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update a component"""
    # project_id path param intentionally unused - kept for RESTful route parity
    _ = project_id  # mark used for linters
    component = safe_db_call(
        db.update_component, component_id, component_data, current_user["id"]
    )
    # Normalize ownership/404 logic consistently with other update endpoints
    ensure_belongs_to_project(component, project_id, "Component")
    return component


@app.delete("/api/projects/{project_id}/components/{component_id}")
async def delete_component(
    project_id: str,  # intentionally unused: kept for RESTful route parity
    component_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a component"""
    # Use safe_db_call to perform delete and then return 404 when the
    # resource wasn't found or didn't belong to the authenticated user.
    _ = project_id  # mark used for linters
    deleted = safe_db_call(db.delete_component, component_id, current_user["id"])
    if deleted:
        return {"message": "Component deleted successfully"}
    # If delete returned falsy, translate into 404
    raise HTTPException(status_code=404, detail="Component not found")


# ===== CATEGORY ENDPOINTS =====


@app.post("/api/projects/{project_id}/categories", response_model=Category)
async def create_category(
    project_id: str,  # intentionally unused: kept for RESTful route parity
    category_data: CategoryCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new category in a project"""
    # Ensure project_id matches the category's project_id
    if str(category_data.project_id) != project_id:
        raise HTTPException(status_code=400, detail="Project ID mismatch")

    _ = project_id
    category = safe_db_call(db.create_category, category_data, current_user["id"])
    if category:
        return category
    raise HTTPException(status_code=400, detail="Failed to create category")


@app.get("/api/projects/{project_id}/categories", response_model=List[Category])
async def get_project_categories(
    project_id: str, current_user: dict = Depends(get_current_user)
):
    """Get all categories for a project"""
    return safe_db_call(db.get_project_categories, project_id, current_user["id"])


@app.put("/api/projects/{project_id}/categories/{category_id}", response_model=Category)
async def update_category(
    project_id: str,
    category_id: str,
    category_data: CategoryUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update a category"""
    _ = project_id
    category = safe_db_call(
        db.update_category, category_id, category_data, current_user["id"]
    )
    # Normalize ownership/404 logic consistently with other update endpoints
    ensure_belongs_to_project(category, project_id, "Category")
    return category


@app.delete("/api/projects/{project_id}/categories/{category_id}")
async def delete_category(
    project_id: str, category_id: str, current_user: dict = Depends(get_current_user)
):
    """Delete a category"""
    _ = project_id
    if safe_db_call(db.delete_category, category_id, current_user["id"]):
        return {"message": "Category deleted successfully"}
    raise HTTPException(status_code=404, detail="Category not found")


# ===== ANALYTICS ENDPOINTS =====


@app.get(
    "/api/projects/{project_id}/analytics/cost-analysis", response_model=CostAnalysis
)
async def get_cost_analysis(
    project_id: str, current_user: dict = Depends(get_current_user)
):
    """Get cost analysis for a project"""
    return safe_db_call(db.get_cost_analysis, project_id, current_user["id"])


@app.get(
    "/api/projects/{project_id}/analytics/reserve-analysis",
    response_model=ReserveAnalysis,
)
async def get_reserve_analysis(
    project_id: str, current_user: dict = Depends(get_current_user)
):
    """Get reserve analysis for a project"""
    return safe_db_call(db.get_reserve_analysis, project_id, current_user["id"])


# ===== METRO MULTIPLIERS ENDPOINTS =====


@app.get("/api/metro-multipliers", response_model=List[MetroMultiplier])
async def get_metro_multipliers(current_user: dict = Depends(get_current_user)):
    """Get all metro multipliers for cost adjustments"""
    # current_user param exists for consistency with other protected endpoints
    # and to keep the route ready for future authorization checks.
    _ = current_user
    return safe_db_call(db.get_metro_multipliers)


@app.post(
    "/api/projects/{project_id}/metro-setting", response_model=ProjectMetroSetting
)
async def set_project_metro(
    project_id: str,
    metro_data: ProjectMetroSettingCreate,
    current_user: dict = Depends(get_current_user),
):
    """Set metro area and multiplier for a project"""
    metro_setting = safe_db_call(
        db.set_project_metro, project_id, metro_data, current_user["id"]
    )
    if metro_setting:
        return metro_setting
    raise HTTPException(status_code=400, detail="Failed to set project metro setting")


@app.get(
    "/api/projects/{project_id}/metro-setting",
    response_model=Optional[ProjectMetroSetting],
)
async def get_project_metro(
    project_id: str, current_user: dict = Depends(get_current_user)
):
    """Get metro area and multiplier for a project"""
    # current_user included for parity with other protected endpoints;
    # mark as used for linters while still passing the id to the DB call.
    _ = current_user
    return safe_db_call(db.get_project_metro, project_id, current_user["id"])


# ===== COMPONENT CATALOG ENDPOINTS =====


@app.get("/api/component-catalog", response_model=List[ComponentCatalog])
async def get_component_catalog(
    current_user: dict = Depends(get_current_user), category: Optional[str] = None
):
    """Get the global component catalog"""
    # current_user included for consistency with other protected endpoints
    # and to keep the route ready for future authorization checks.
    _ = current_user
    return safe_db_call(db.get_component_catalog, category)


# ===== AUDIT LOG ENDPOINTS =====


@app.get("/api/projects/{project_id}/audit-logs", response_model=List[AuditLog])
async def get_project_audit_logs(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    entity_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
):
    """Get audit logs for a project"""
    return safe_db_call(
        db.get_project_audit_logs,
        project_id,
        current_user["id"],
        entity_type,
        skip,
        limit,
    )


# ===== MEETING ENDPOINTS =====


@app.post("/api/projects/{project_id}/meetings", response_model=Meeting)
async def create_meeting(
    project_id: str,
    meeting_data: MeetingCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new meeting for a project"""
    # Ensure project_id matches the meeting's project_id
    if str(meeting_data.project_id) != project_id:
        raise HTTPException(status_code=400, detail="Project ID mismatch")

    _ = project_id
    meeting = safe_db_call(db.create_meeting, meeting_data, current_user["id"])
    if meeting:
        return meeting
    raise HTTPException(status_code=400, detail="Failed to create meeting")


@app.get("/api/projects/{project_id}/meetings", response_model=List[Meeting])
async def get_project_meetings(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    meeting_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get all meetings for a project"""
    _ = current_user
    return safe_db_call(
        db.get_project_meetings,
        project_id,
        current_user["id"],
        meeting_type,
        skip,
        limit,
    )


@app.get("/api/projects/{project_id}/meetings/{meeting_id}", response_model=Meeting)
async def get_meeting(
    project_id: str, meeting_id: str, current_user: dict = Depends(get_current_user)
):
    """Get a specific meeting"""
    meeting = safe_db_call(db.get_meeting, meeting_id, current_user["id"])
    ensure_belongs_to_project(meeting, project_id, "Meeting")
    return meeting


@app.put("/api/projects/{project_id}/meetings/{meeting_id}", response_model=Meeting)
async def update_meeting(
    project_id: str,
    meeting_id: str,
    meeting_data: MeetingUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update a meeting"""
    _ = project_id
    meeting = safe_db_call(
        db.update_meeting, meeting_id, meeting_data, current_user["id"]
    )
    ensure_belongs_to_project(meeting, project_id, "Meeting")
    return meeting


@app.delete("/api/projects/{project_id}/meetings/{meeting_id}")
async def delete_meeting(
    project_id: str, meeting_id: str, current_user: dict = Depends(get_current_user)
):
    """Delete a meeting"""
    _ = project_id
    if safe_db_call(db.delete_meeting, meeting_id, current_user["id"]):
        return {"message": "Meeting deleted successfully"}
    raise HTTPException(status_code=404, detail="Meeting not found")


# ===== COMMUNICATION ENDPOINTS =====


@app.post("/api/projects/{project_id}/communications", response_model=Communication)
async def create_communication(
    project_id: str,
    communication_data: CommunicationCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new communication for a project"""
    # Ensure project_id matches the communication's project_id
    if str(communication_data.project_id) != project_id:
        raise HTTPException(status_code=400, detail="Project ID mismatch")

    _ = project_id
    communication = safe_db_call(
        db.create_communication, communication_data, current_user["id"]
    )
    if communication:
        return communication
    raise HTTPException(status_code=400, detail="Failed to create communication")


@app.get(
    "/api/projects/{project_id}/communications", response_model=List[Communication]
)
async def get_project_communications(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    communication_type: Optional[str] = None,
    comm_status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get all communications for a project"""
    return safe_db_call(
        db.get_project_communications,
        project_id,
        current_user["id"],
        communication_type,
        comm_status,
        skip,
        limit,
    )


@app.get(
    "/api/projects/{project_id}/communications/{communication_id}",
    response_model=Communication,
)
async def get_communication(
    project_id: str,
    communication_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a specific communication"""
    communication = safe_db_call(
        db.get_communication, communication_id, current_user["id"]
    )
    ensure_belongs_to_project(communication, project_id, "Communication")
    return communication


@app.put(
    "/api/projects/{project_id}/communications/{communication_id}",
    response_model=Communication,
)
async def update_communication(
    project_id: str,
    communication_id: str,
    communication_data: CommunicationUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update a communication"""
    _ = project_id
    communication = safe_db_call(
        db.update_communication,
        communication_id,
        communication_data,
        current_user["id"],
    )
    ensure_belongs_to_project(communication, project_id, "Communication")
    return communication


@app.delete("/api/projects/{project_id}/communications/{communication_id}")
async def delete_communication(
    project_id: str,
    communication_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a communication"""
    _ = project_id
    if safe_db_call(db.delete_communication, communication_id, current_user["id"]):
        return {"message": "Communication deleted successfully"}
    raise HTTPException(status_code=404, detail="Communication not found")


# ===== MEDIA FILE ENDPOINTS =====


@app.post("/api/projects/{project_id}/media-files", response_model=MediaFile)
async def create_media_file(
    project_id: str,
    media_file_data: MediaFileCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new media file for a project"""
    # Ensure project_id matches the media file's project_id
    if str(media_file_data.project_id) != project_id:
        raise HTTPException(status_code=400, detail="Project ID mismatch")

    media_file = safe_db_call(db.create_media_file, media_file_data, current_user["id"])
    if media_file:
        return media_file
    raise HTTPException(status_code=400, detail="Failed to create media file")


@app.get("/api/projects/{project_id}/media-files", response_model=List[MediaFile])
async def get_project_media_files(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    file_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get all media files for a project"""
    _ = current_user
    return safe_db_call(
        db.get_project_media_files,
        project_id,
        current_user["id"],
        file_type,
        skip,
        limit,
    )


@app.get(
    "/api/projects/{project_id}/media-files/{media_file_id}", response_model=MediaFile
)
async def get_media_file(
    project_id: str, media_file_id: str, current_user: dict = Depends(get_current_user)
):
    """Get a specific media file"""
    _ = project_id
    media_file = safe_db_call(db.get_media_file, media_file_id, current_user["id"])
    ensure_belongs_to_project(media_file, project_id, "Media file")
    return media_file


@app.put(
    "/api/projects/{project_id}/media-files/{media_file_id}", response_model=MediaFile
)
async def update_media_file(
    project_id: str,
    media_file_id: str,
    media_file_data: MediaFileUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update a media file"""
    _ = project_id
    media_file = safe_db_call(
        db.update_media_file, media_file_id, media_file_data, current_user["id"]
    )
    ensure_belongs_to_project(media_file, project_id, "Media file")
    return media_file


@app.delete("/api/projects/{project_id}/media-files/{media_file_id}")
async def delete_media_file(
    project_id: str, media_file_id: str, current_user: dict = Depends(get_current_user)
):
    """Delete a media file"""
    _ = project_id
    deleted = safe_db_call(db.delete_media_file, media_file_id, current_user["id"])
    if deleted:
        return {"message": "Media file deleted successfully"}
    raise HTTPException(status_code=404, detail="Media file not found")


# ===== INTERVIEW ENDPOINTS =====


@app.post("/api/projects/{project_id}/interviews", response_model=Interview)
async def create_interview(
    project_id: str,
    interview_data: InterviewCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new interview for a project"""
    # Ensure project_id matches the interview's project_id
    if str(interview_data.project_id) != project_id:
        raise HTTPException(status_code=400, detail="Project ID mismatch")

    _ = project_id
    interview = safe_db_call(db.create_interview, interview_data, current_user["id"])
    if interview:
        return interview
    raise HTTPException(status_code=400, detail="Failed to create interview")


@app.get("/api/projects/{project_id}/interviews", response_model=List[Interview])
async def get_project_interviews(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    interview_type: Optional[str] = None,
    interview_status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get all interviews for a project"""
    return safe_db_call(
        db.get_project_interviews,
        project_id,
        current_user["id"],
        interview_type,
        interview_status,
        skip,
        limit,
    )


@app.get(
    "/api/projects/{project_id}/interviews/{interview_id}", response_model=Interview
)
async def get_interview(
    project_id: str, interview_id: str, current_user: dict = Depends(get_current_user)
):
    """Get a specific interview"""
    interview = safe_db_call(db.get_interview, interview_id, current_user["id"])
    ensure_belongs_to_project(interview, project_id, "Interview")
    return interview


@app.put(
    "/api/projects/{project_id}/interviews/{interview_id}", response_model=Interview
)
async def update_interview(
    project_id: str,
    interview_id: str,
    interview_data: InterviewUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update an interview"""
    _ = project_id
    interview = safe_db_call(
        db.update_interview, interview_id, interview_data, current_user["id"]
    )
    ensure_belongs_to_project(interview, project_id, "Interview")
    return interview


@app.delete("/api/projects/{project_id}/interviews/{interview_id}")
async def delete_interview(
    project_id: str, interview_id: str, current_user: dict = Depends(get_current_user)
):
    """Delete an interview"""
    _ = project_id
    if safe_db_call(db.delete_interview, interview_id, current_user["id"]):
        return {"message": "Interview deleted successfully"}
    raise HTTPException(status_code=404, detail="Interview not found")


# ===== INSPECTION ENDPOINTS =====


@app.post("/api/projects/{project_id}/inspections", response_model=Inspection)
async def create_inspection(
    project_id: str,
    inspection_data: InspectionCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new inspection for a project"""
    # Ensure project_id matches the inspection's project_id
    if str(inspection_data.project_id) != project_id:
        raise HTTPException(status_code=400, detail="Project ID mismatch")

    _ = project_id
    inspection = safe_db_call(db.create_inspection, inspection_data, current_user["id"])
    if inspection:
        return inspection
    raise HTTPException(status_code=400, detail="Failed to create inspection")


@app.get("/api/projects/{project_id}/inspections", response_model=List[Inspection])
async def get_project_inspections(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    inspection_type: Optional[str] = None,
    inspection_status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get all inspections for a project"""
    return safe_db_call(
        db.get_project_inspections,
        project_id,
        current_user["id"],
        inspection_type,
        inspection_status,
        skip,
        limit,
    )


@app.get(
    "/api/projects/{project_id}/inspections/{inspection_id}", response_model=Inspection
)
async def get_inspection(
    project_id: str, inspection_id: str, current_user: dict = Depends(get_current_user)
):
    """Get a specific inspection"""
    _ = project_id
    inspection = safe_db_call(db.get_inspection, inspection_id, current_user["id"])
    ensure_belongs_to_project(inspection, project_id, "Inspection")
    return inspection


@app.put(
    "/api/projects/{project_id}/inspections/{inspection_id}", response_model=Inspection
)
async def update_inspection(
    project_id: str,
    inspection_id: str,
    inspection_data: InspectionUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update an inspection"""
    _ = project_id
    inspection = safe_db_call(
        db.update_inspection, inspection_id, inspection_data, current_user["id"]
    )
    ensure_belongs_to_project(inspection, project_id, "Inspection")
    return inspection


@app.delete("/api/projects/{project_id}/inspections/{inspection_id}")
async def delete_inspection(
    project_id: str, inspection_id: str, current_user: dict = Depends(get_current_user)
):
    """Delete an inspection"""
    _ = project_id
    if safe_db_call(db.delete_inspection, inspection_id, current_user["id"]):
        return {"message": "Inspection deleted successfully"}
    raise HTTPException(status_code=404, detail="Inspection not found")


# ===== INSPECTION ITEM ENDPOINTS =====


@app.post(
    "/api/projects/{project_id}/inspections/{inspection_id}/items",
    response_model=InspectionItem,
)
async def create_inspection_item(
    project_id: str,
    inspection_id: str,
    inspection_item_data: InspectionItemCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new inspection item for an inspection"""
    # Ensure inspection_id matches the inspection item's inspection_id
    if str(inspection_item_data.inspection_id) != inspection_id:
        raise HTTPException(status_code=400, detail="Inspection ID mismatch")

    _ = project_id
    _ = inspection_id
    inspection_item = safe_db_call(
        db.create_inspection_item, inspection_item_data, current_user["id"]
    )
    if inspection_item:
        return inspection_item
    raise HTTPException(status_code=400, detail="Failed to create inspection item")


@app.get(
    "/api/projects/{project_id}/inspections/{inspection_id}/items",
    response_model=List[InspectionItem],
)
async def get_inspection_items(
    project_id: str,
    inspection_id: str,
    current_user: dict = Depends(get_current_user),
    item_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get all inspection items for an inspection"""
    # `project_id` provided for route parity; `inspection_id` is used to
    # query items and validate ownership later when individual resources
    # are accessed. Mark both as used to satisfy linters while keeping
    # the route signatures stable.
    _ = project_id
    _ = inspection_id
    return safe_db_call(
        db.get_inspection_items,
        inspection_id,
        current_user["id"],
        item_type,
        skip,
        limit,
    )


@app.get(
    "/api/projects/{project_id}/inspections/{inspection_id}/items/{item_id}",
    response_model=InspectionItem,
)
async def get_inspection_item(
    project_id: str,
    inspection_id: str,
    item_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a specific inspection item"""
    # Keep project_id and inspection_id in signature for route parity;
    # mark both used for linters. The ownership check below validates
    # the inspection/project relationship.
    _ = project_id
    _ = inspection_id
    inspection_item = safe_db_call(db.get_inspection_item, item_id, current_user["id"])
    # For inspection items we normalize the resource name and ensure the
    # returned item's project matches the requested project. Pass the
    # top-level `project_id` (route param) into the ownership check so
    # we compare the item's project_id against the project requested by
    # the client.
    ensure_belongs_to_project(inspection_item, project_id, "Inspection item")
    return inspection_item


@app.put(
    "/api/projects/{project_id}/inspections/{inspection_id}/items/{item_id}",
    response_model=InspectionItem,
)
async def update_inspection_item(
    project_id: str,
    inspection_id: str,
    item_id: str,
    inspection_item_data: InspectionItemUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update an inspection item"""
    _ = project_id
    _ = inspection_id
    inspection_item = safe_db_call(
        db.update_inspection_item, item_id, inspection_item_data, current_user["id"]
    )
    ensure_belongs_to_project(inspection_item, inspection_id, "Inspection item")
    return inspection_item


@app.delete("/api/projects/{project_id}/inspections/{inspection_id}/items/{item_id}")
async def delete_inspection_item(
    project_id: str,
    inspection_id: str,
    item_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete an inspection item"""
    _ = project_id
    _ = inspection_id
    if safe_db_call(db.delete_inspection_item, item_id, current_user["id"]):
        return {"message": "Inspection item deleted successfully"}
    raise HTTPException(status_code=404, detail="Inspection item not found")

    ensure_belongs_to_project(inspection_item, project_id, "Inspection item")
# ===== EVIDENCE ENDPOINTS =====


@app.post("/api/projects/{project_id}/evidence", response_model=Evidence)
async def create_evidence(
    project_id: str,
    evidence_data: EvidenceCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new evidence item for a project"""
    # Ensure project_id matches the evidence's project_id
    if str(evidence_data.project_id) != project_id:
        raise HTTPException(status_code=400, detail="Project ID mismatch")

    _ = project_id
    evidence = safe_db_call(db.create_evidence, evidence_data, current_user["id"])
    if evidence:
        return evidence
    raise HTTPException(status_code=400, detail="Failed to create evidence")


@app.get("/api/projects/{project_id}/evidence", response_model=List[Evidence])
async def get_project_evidence(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    evidence_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get all evidence for a project"""
    return safe_db_call(
        db.get_project_evidence,
        project_id,
        current_user["id"],
        evidence_type,
        skip,
        limit,
    )


@app.get("/api/projects/{project_id}/evidence/{evidence_id}", response_model=Evidence)
async def get_evidence(
    project_id: str, evidence_id: str, current_user: dict = Depends(get_current_user)
):
    """Get a specific evidence item"""
    evidence = safe_db_call(db.get_evidence, evidence_id, current_user["id"])
    ensure_belongs_to_project(evidence, project_id, "Evidence")
    return evidence


@app.put("/api/projects/{project_id}/evidence/{evidence_id}", response_model=Evidence)
async def update_evidence(
    project_id: str,
    evidence_id: str,
    evidence_data: EvidenceUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update an evidence item"""
    _ = project_id
    evidence = safe_db_call(
        db.update_evidence, evidence_id, evidence_data, current_user["id"]
    )
    ensure_belongs_to_project(evidence, project_id, "Evidence")
    return evidence


@app.delete("/api/projects/{project_id}/evidence/{evidence_id}")
async def delete_evidence(
    project_id: str, evidence_id: str, current_user: dict = Depends(get_current_user)
):
    """Delete an evidence item"""
    _ = project_id
    if safe_db_call(db.delete_evidence, evidence_id, current_user["id"]):
        return {"message": "Evidence deleted successfully"}
    raise HTTPException(status_code=404, detail="Evidence not found")


@app.get("/api/test")
async def test_endpoint():
    return {"message": "Endpoint de prueba funcionando"}


@app.get("/")
async def root():
    return {
        "message": "Reserve Flow AI API",
        # Provide a localized fallback for Spanish consumers.
        "message_localized": "API de Autenticación con JWT",
        "version": "2.0.0",
        "documentation": "/docs",
    }


if __name__ == "__main__":
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "3000"))
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
