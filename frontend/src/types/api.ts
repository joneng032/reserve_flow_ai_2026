// Tipos para autenticación
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  username: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RegisterResponse {
  access_token: string;
  token_type: string;
  user: User;
  message: string;
}

export interface ProtectedResponse {
  message: string;
  user_info: User;
}

// Tipos para usuarios
export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  created_at?: string;
}

export interface UsersResponse {
  users: User[];
}

// Tipos para proyectos
export interface Project {
  id: string;
  name: string;
  client_name?: string;
  address?: string;
  current_reserve_balance?: number;
  profile_id?: string;
  created_at?: string;
  updated_at?: string;
  custom_fields?: Record<string, unknown>;
}

// Convenience type for creating/updating projects via the API
export type ProjectCreate = Omit<
  Project,
  "id" | "profile_id" | "created_at" | "updated_at"
> & {
  client_contact_name?: string;
  client_email?: string;
  client_phone?: string;
  property_type?: string;
  property_size?: number;
  property_size_unit?: string;
  ownership_structure?: string;
  target_funding_percentage?: number;
  project_status?: string;
  project_description?: string;
  custom_fields?: Record<string, unknown>;
};

// Tipos para componentes
export interface Component {
  id: string;
  name: string;
  category: string;
  description?: string;
  useful_life?: number;
  current_age?: number;
  cost?: number;
  priority?: string;
  status?: string;
  project_id: string;
  created_at?: string;
  updated_at?: string;
}

// Tipos para reuniones
export interface Meeting {
  id: string;
  title: string;
  meeting_date: string;
  location?: string;
  meeting_type: string;
  attendees?: string[];
  facilitator?: string;
  note_taker?: string;
  agenda_items?: string[];
  discussion_notes?: string;
  decisions?: string[];
  action_items?: Array<Record<string, unknown>>;
  next_meeting_date?: string;
  attachments?: string[];
  tags?: string[];
  project_id: string;
  created_by?: string;
  created_at?: string;
  updated_at?: string;
}

export interface MeetingCreate {
  title: string;
  meeting_date: string;
  location?: string;
  meeting_type: string;
  attendees?: string[];
  facilitator?: string;
  note_taker?: string;
  agenda_items?: string[];
  discussion_notes?: string;
  decisions?: string[];
  action_items?: Array<Record<string, unknown>>;
  next_meeting_date?: string;
  attachments?: string[];
  tags?: string[];
  project_id: string;
}

export type MeetingUpdate = Partial<MeetingCreate>;

// Tipos para comunicaciones
export interface Communication {
  id: string;
  communication_type: string;
  direction: string;
  contact_name: string;
  contact_method?: string;
  subject?: string;
  content?: string;
  attachments?: string[];
  follow_up_required?: boolean;
  follow_up_date?: string;
  follow_up_notes?: string;
  status?: string;
  related_meeting_id?: string;
  related_component_id?: string;
  tags?: string[];
  project_id: string;
  created_by?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CommunicationCreate {
  communication_type: string;
  direction: string;
  contact_name: string;
  contact_method?: string;
  subject?: string;
  content?: string;
  attachments?: string[];
  follow_up_required?: boolean;
  follow_up_date?: string;
  follow_up_notes?: string;
  status?: string;
  related_meeting_id?: string;
  related_component_id?: string;
  tags?: string[];
  project_id: string;
}

export type CommunicationUpdate = Partial<CommunicationCreate>;

// Tipos para archivos multimedia
export interface MediaFile {
  id: string;
  file_name: string;
  file_path: string;
  file_type: string;
  mime_type: string;
  file_size: number;
  description?: string;
  tags?: string[];
  metadata?: Record<string, unknown>;
  related_meeting_id?: string;
  related_component_id?: string;
  related_communication_id?: string;
  project_id: string;
  uploaded_by?: string;
  created_at?: string;
  updated_at?: string;
}

export interface MediaFileCreate {
  file_name: string;
  file_path: string;
  file_type: string;
  mime_type: string;
  file_size: number;
  description?: string;
  tags?: string[];
  metadata?: Record<string, unknown>;
  related_meeting_id?: string;
  related_component_id?: string;
  related_communication_id?: string;
  project_id: string;
}

export type MediaFileUpdate = Partial<MediaFileCreate>;

// Tipos para entrevistas
export interface Interview {
  id: string;
  interviewee_name: string;
  interviewee_role?: string;
  interviewee_contact?: string;
  interview_type: string;
  scheduled_date?: string;
  completed_date?: string;
  location?: string;
  status: string;
  question_template?: string;
  responses?: Record<string, unknown>;
  notes?: string;
  follow_up_required: boolean;
  follow_up_date?: string;
  attachments?: string[];
  tags?: string[];
  project_id: string;
  conducted_by?: string;
  created_at?: string;
  updated_at?: string;
}

export interface InterviewCreate {
  interviewee_name: string;
  interviewee_role?: string;
  interviewee_contact?: string;
  interview_type: string;
  scheduled_date?: string;
  completed_date?: string;
  location?: string;
  status?: string;
  question_template?: string;
  responses?: Record<string, unknown>;
  notes?: string;
  follow_up_required?: boolean;
  follow_up_date?: string;
  attachments?: string[];
  project_id: string;
}

export type InterviewUpdate = Partial<InterviewCreate>;

// Tipos para inspecciones
export interface Inspection {
  id: string;
  inspection_type: string;
  scheduled_date?: string;
  completed_date?: string;
  location?: string;
  weather_conditions?: string;
  temperature?: number;
  status: string;
  overall_condition?: string;
  priority_findings?: string;
  recommendations?: string;
  estimated_cost?: number;
  project_id: string;
  conducted_by?: string;
  created_at?: string;
  updated_at?: string;
}

export interface InspectionCreate {
  inspection_type: string;
  scheduled_date?: string;
  completed_date?: string;
  location?: string;
  weather_conditions?: string;
  temperature?: number;
  status?: string;
  overall_condition?: string;
  priority_findings?: string;
  recommendations?: string;
  estimated_cost?: number;
  project_id: string;
}

export type InspectionUpdate = Partial<InspectionCreate>;

// Tipos para elementos de inspección
export interface InspectionItem {
  id: string;
  component_id?: string;
  item_name: string;
  item_type: string;
  location?: string;
  condition_rating?: number;
  condition_description?: string;
  measurement_value?: number;
  measurement_unit?: string;
  notes?: string;
  priority?: string;
  estimated_replacement_cost?: number;
  estimated_remaining_life?: number;
  photos?: string[];
  inspection_id: string;
  created_at?: string;
  updated_at?: string;
}

export interface InspectionItemCreate {
  component_id?: string;
  item_name: string;
  item_type: string;
  location?: string;
  condition_rating?: number;
  condition_description?: string;
  measurement_value?: number;
  measurement_unit?: string;
  notes?: string;
  priority?: string;
  estimated_replacement_cost?: number;
  estimated_remaining_life?: number;
  photos?: string[];
  inspection_id: string;
}

export type InspectionItemUpdate = Partial<InspectionItemCreate>;

// Tipos para evidencia
export interface Evidence {
  id: string;
  evidence_type: string;
  file_name?: string;
  file_path?: string;
  mime_type?: string;
  file_size?: number;
  latitude?: number;
  longitude?: number;
  altitude?: number;
  accuracy?: number;
  heading?: number;
  speed?: number;
  timestamp?: string;
  measurement_value?: number;
  measurement_unit?: string;
  notes?: string;
  tags?: string[];
  related_inspection_id?: string;
  related_inspection_item_id?: string;
  related_component_id?: string;
  device_info?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
  project_id: string;
  captured_by?: string;
  created_at?: string;
  updated_at?: string;
}

export interface EvidenceCreate {
  evidence_type: string;
  file_name?: string;
  file_path?: string;
  mime_type?: string;
  file_size?: number;
  latitude?: number;
  longitude?: number;
  altitude?: number;
  accuracy?: number;
  heading?: number;
  speed?: number;
  timestamp?: string;
  measurement_value?: number;
  measurement_unit?: string;
  notes?: string;
  tags?: string[];
  related_inspection_id?: string;
  related_inspection_item_id?: string;
  related_component_id?: string;
  device_info?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
  project_id: string;
}

export type EvidenceUpdate = Partial<EvidenceCreate>;

// Tipos para análisis
export interface CostAnalysis {
  total_components: number;
  total_value: number;
  average_cost: number;
  categories_breakdown: Record<string, Record<string, unknown>>;
}

export interface ReserveAnalysis {
  percent_funded: number;
  total_reserve_balance: number;
  total_liability: number;
  funding_gap: number;
  recommendations: string[];
}

// Tipos para categorías y etiquetas
export interface Category {
  id: string;
  name: string;
  description?: string;
}

export interface Tag {
  id: string;
  name: string;
  color?: string;
}

export interface ApiError {
  detail: string;
}
