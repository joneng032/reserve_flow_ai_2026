from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import UUID4, BaseModel, ConfigDict, Field


# Base models with common fields
class BaseDBModel(BaseModel):
    id: Optional[UUID4] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Profile models
class ProfileBase(BaseModel):
    # `name` used to be required; make it optional to accept legacy
    # payloads that have `username` instead. A model-level validator
    # will populate `name` from `username` when present.
    name: Optional[str] = None
    # Accept legacy field `username` in incoming records
    username: Optional[str] = None
    email: Optional[str] = None
    hashed_pin: Optional[str] = None
    pin_salt: Optional[str] = None
    kdf: Optional[Dict[str, Any]] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class Profile(ProfileBase, BaseDBModel):
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def model_validate(cls, obj):
        # Pydantic v2 hook: ensure `name` exists when `username` is present
        if isinstance(obj, dict):
            if "name" not in obj and "username" in obj:
                obj["name"] = obj.get("username")
        return super().model_validate(obj)


# Project models
class ProjectBase(BaseModel):
    name: str
    client_name: Optional[str] = None
    address: Optional[str] = None
    current_reserve_balance: Optional[Decimal] = Field(default=Decimal("0"))
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ProjectCreate(ProjectBase):
    # profile_id may be supplied by the client or set by the API from the
    # authenticated user. Keep it optional to make the API more flexible.
    profile_id: Optional[UUID4] = None


class ProjectUpdate(ProjectBase):
    pass


class Project(ProjectBase, BaseDBModel):
    profile_id: UUID4
    model_config = ConfigDict(from_attributes=True)


# Category models
class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[UUID4] = None
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CategoryCreate(CategoryBase):
    project_id: UUID4


class CategoryUpdate(CategoryBase):
    pass


class Category(CategoryBase, BaseDBModel):
    project_id: UUID4
    model_config = ConfigDict(from_attributes=True)


# Field Definition models
class FieldDefinitionBase(BaseModel):
    name: str
    entity_type: str  # 'component' or 'project'
    field_type: str  # 'text', 'number', 'currency', 'date', 'select', 'boolean'
    label: str
    required: Optional[bool] = False
    default_value: Optional[Any] = None
    options: Optional[List[str]] = None
    validation: Optional[Dict[str, Any]] = None


class FieldDefinitionCreate(FieldDefinitionBase):
    project_id: UUID4


class FieldDefinitionUpdate(FieldDefinitionBase):
    pass


class FieldDefinition(FieldDefinitionBase, BaseDBModel):
    project_id: UUID4
    model_config = ConfigDict(from_attributes=True)


# Template models
class TemplateBase(BaseModel):
    name: str
    entity_type: str  # 'component' or 'project'
    field_definitions: Optional[List[UUID4]] = Field(default_factory=list)


class TemplateCreate(TemplateBase):
    project_id: UUID4


class TemplateUpdate(TemplateBase):
    pass


class Template(TemplateBase, BaseDBModel):
    project_id: UUID4
    model_config = ConfigDict(from_attributes=True)


# Tag models
class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    project_id: UUID4


class TagUpdate(TagBase):
    pass


class Tag(TagBase, BaseDBModel):
    project_id: UUID4
    model_config = ConfigDict(from_attributes=True)


# Component models
class ComponentBase(BaseModel):
    name: str
    category: Optional[str] = None
    base_cost: Optional[Decimal] = None
    useful_life: Optional[int] = None
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ComponentCreate(ComponentBase):
    project_id: UUID4


class ComponentUpdate(ComponentBase):
    pass


class Component(ComponentBase, BaseDBModel):
    project_id: UUID4
    model_config = ConfigDict(from_attributes=True)


# Component Tag models
class ComponentTagBase(BaseModel):
    component_id: UUID4
    tag_id: UUID4


class ComponentTagCreate(ComponentTagBase):
    pass


class ComponentTag(ComponentTagBase, BaseDBModel):
    model_config = ConfigDict(from_attributes=True)


# Component Catalog models
class ComponentCatalogBase(BaseModel):
    name: str
    category: Optional[str] = None
    base_cost: Optional[Decimal] = None
    useful_life: Optional[int] = None


class ComponentCatalogCreate(ComponentCatalogBase):
    pass


class ComponentCatalog(ComponentCatalogBase, BaseDBModel):
    model_config = ConfigDict(from_attributes=True)


# Audit Log models
class AuditLogBase(BaseModel):
    entity_type: str
    entity_id: UUID4
    action: str
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AuditLogCreate(AuditLogBase):
    profile_id: Optional[UUID4] = None


class AuditLog(AuditLogBase, BaseDBModel):
    profile_id: Optional[UUID4] = None
    model_config = ConfigDict(from_attributes=True)


# App Settings models
class AppSettingBase(BaseModel):
    key: str
    value: Any


class AppSettingCreate(AppSettingBase):
    pass


class AppSettingUpdate(AppSettingBase):
    pass


class AppSetting(AppSettingBase, BaseDBModel):
    model_config = ConfigDict(from_attributes=True)


# Metro Multiplier models
class MetroMultiplierBase(BaseModel):
    metro_area: str
    multiplier: Decimal
    region: Optional[str] = None


class MetroMultiplierCreate(MetroMultiplierBase):
    pass


class MetroMultiplier(MetroMultiplierBase, BaseDBModel):
    model_config = ConfigDict(from_attributes=True)


# Project Metro Settings models
class ProjectMetroSettingBase(BaseModel):
    metro_area: str
    custom_multiplier: Optional[Decimal] = None


class ProjectMetroSettingCreate(ProjectMetroSettingBase):
    project_id: UUID4


class ProjectMetroSetting(ProjectMetroSettingBase, BaseDBModel):
    project_id: UUID4
    model_config = ConfigDict(from_attributes=True)


# Meeting models
class MeetingBase(BaseModel):
    title: str
    meeting_date: datetime
    location: Optional[str] = None
    meeting_type: str
    attendees: Optional[List[str]] = Field(default_factory=list)
    facilitator: Optional[str] = None
    note_taker: Optional[str] = None
    agenda_items: Optional[List[str]] = Field(default_factory=list)
    discussion_notes: Optional[str] = None
    decisions: Optional[List[str]] = Field(default_factory=list)
    action_items: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    next_meeting_date: Optional[datetime] = None
    attachments: Optional[List[str]] = Field(default_factory=list)
    tags: Optional[List[str]] = Field(default_factory=list)


class MeetingCreate(MeetingBase):
    project_id: UUID4


class MeetingUpdate(MeetingBase):
    pass


class Meeting(MeetingBase, BaseDBModel):
    project_id: UUID4
    created_by: Optional[UUID4] = None
    model_config = ConfigDict(from_attributes=True)


# Communication models
class CommunicationBase(BaseModel):
    communication_type: str
    direction: str
    contact_name: str
    contact_method: Optional[str] = None
    subject: Optional[str] = None
    content: Optional[str] = None
    attachments: Optional[List[str]] = Field(default_factory=list)
    follow_up_required: Optional[bool] = False
    follow_up_date: Optional[datetime] = None
    follow_up_notes: Optional[str] = None
    status: Optional[str] = "completed"
    related_meeting_id: Optional[UUID4] = None
    related_component_id: Optional[UUID4] = None


class CommunicationCreate(CommunicationBase):
    project_id: UUID4


class CommunicationUpdate(CommunicationBase):
    pass


class Communication(CommunicationBase, BaseDBModel):
    project_id: UUID4
    created_by: Optional[UUID4] = None
    model_config = ConfigDict(from_attributes=True)


# Media File models
class MediaFileBase(BaseModel):
    file_name: str
    file_path: str
    file_type: str
    mime_type: str
    file_size: int
    description: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    related_meeting_id: Optional[UUID4] = None
    related_component_id: Optional[UUID4] = None
    related_communication_id: Optional[UUID4] = None


class MediaFileCreate(MediaFileBase):
    project_id: UUID4


class MediaFileUpdate(MediaFileBase):
    pass


class MediaFile(MediaFileBase, BaseDBModel):
    project_id: UUID4
    uploaded_by: Optional[UUID4] = None
    model_config = ConfigDict(from_attributes=True)


# Interview models
class InterviewBase(BaseModel):
    interviewee_name: str
    interviewee_role: Optional[str] = None
    interviewee_contact: Optional[str] = None
    interview_type: str  # 'initial', 'follow_up', 'clarification', 'exit'
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    location: Optional[str] = None
    status: str = "scheduled"  # 'scheduled', 'in_progress', 'completed', 'cancelled'
    question_template: Optional[str] = None
    responses: Optional[Dict[str, Any]] = Field(default_factory=dict)
    notes: Optional[str] = None
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None
    attachments: Optional[List[str]] = Field(default_factory=list)


class InterviewCreate(InterviewBase):
    project_id: UUID4


class InterviewUpdate(InterviewBase):
    pass


class Interview(InterviewBase, BaseDBModel):
    project_id: UUID4
    conducted_by: Optional[UUID4] = None
    model_config = ConfigDict(from_attributes=True)


# Inspection models
class InspectionBase(BaseModel):
    inspection_type: str  # 'building_exterior', 'building_interior', 'site', 'systems', 'roof', 'parking', 'common_areas', 'units'
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    location: Optional[str] = None
    weather_conditions: Optional[str] = None
    temperature: Optional[Decimal] = None
    status: str = "scheduled"  # 'scheduled', 'in_progress', 'completed', 'cancelled'
    overall_condition: Optional[
        str
    ] = None  # 'excellent', 'good', 'fair', 'poor', 'critical'
    priority_findings: Optional[str] = None
    recommendations: Optional[str] = None
    estimated_cost: Optional[Decimal] = None


class InspectionCreate(InspectionBase):
    project_id: UUID4


class InspectionUpdate(InspectionBase):
    pass


class Inspection(InspectionBase, BaseDBModel):
    project_id: UUID4
    conducted_by: Optional[UUID4] = None
    model_config = ConfigDict(from_attributes=True)


# Inspection Item models
class InspectionItemBase(BaseModel):
    component_id: Optional[UUID4] = None
    item_name: str
    item_type: str  # 'measurement', 'condition', 'observation', 'recommendation'
    location: Optional[str] = None
    condition_rating: Optional[int] = Field(None, ge=1, le=5)  # 1-5 scale
    condition_description: Optional[str] = None
    measurement_value: Optional[Decimal] = None
    measurement_unit: Optional[str] = None
    notes: Optional[str] = None
    priority: Optional[str] = None  # 'low', 'medium', 'high', 'critical'
    estimated_replacement_cost: Optional[Decimal] = None
    estimated_remaining_life: Optional[int] = None
    photos: Optional[List[str]] = Field(default_factory=list)


class InspectionItemCreate(InspectionItemBase):
    inspection_id: UUID4


class InspectionItemUpdate(InspectionItemBase):
    pass


class InspectionItem(InspectionItemBase, BaseDBModel):
    inspection_id: UUID4
    model_config = ConfigDict(from_attributes=True)


# Evidence models
class EvidenceBase(BaseModel):
    evidence_type: str  # 'photo', 'video', 'audio', 'measurement', 'note'
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    altitude: Optional[Decimal] = None
    accuracy: Optional[Decimal] = None
    heading: Optional[Decimal] = None
    speed: Optional[Decimal] = None
    timestamp: Optional[datetime] = None
    measurement_value: Optional[Decimal] = None
    measurement_unit: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    related_inspection_id: Optional[UUID4] = None
    related_inspection_item_id: Optional[UUID4] = None
    related_component_id: Optional[UUID4] = None
    device_info: Optional[Dict[str, Any]] = Field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class EvidenceCreate(EvidenceBase):
    project_id: UUID4


class EvidenceUpdate(EvidenceBase):
    pass


class Evidence(EvidenceBase, BaseDBModel):
    project_id: UUID4
    captured_by: Optional[UUID4] = None
    model_config = ConfigDict(from_attributes=True)


# Response models for API endpoints
class ProjectWithDetails(Project):
    categories: Optional[List[Category]] = []
    components_count: Optional[int] = 0
    total_value: Optional[Decimal] = Decimal("0")


class ComponentWithTags(Component):
    tags: Optional[List[Tag]] = []


# Analytics models
class CostAnalysis(BaseModel):
    total_components: int
    total_value: Decimal
    average_cost: Decimal
    categories_breakdown: Dict[str, Dict[str, Any]]


class ReserveAnalysis(BaseModel):
    percent_funded: Decimal
    total_reserve_balance: Decimal
    total_liability: Decimal
    funding_gap: Decimal
    recommendations: List[str]
