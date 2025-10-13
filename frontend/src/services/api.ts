import axios from "axios";
import type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  ProtectedResponse,
  UsersResponse,
  Project,
  Component,
  Category,
  CostAnalysis,
  ReserveAnalysis,
  Meeting,
  MeetingCreate,
  MeetingUpdate,
  Communication,
  CommunicationCreate,
  CommunicationUpdate,
  MediaFile,
  MediaFileCreate,
  MediaFileUpdate,
  Interview,
  InterviewCreate,
  InterviewUpdate,
  Inspection,
  InspectionCreate,
  InspectionUpdate,
  InspectionItem,
  InspectionItemCreate,
  InspectionItemUpdate,
  Evidence,
  EvidenceCreate,
  EvidenceUpdate,
} from "../types/api";

// Re-export types so other modules can import types from services/api
export * from "../types/api";

// Configurar la URL base según el entorno
const API_BASE_URL = import.meta.env.PROD
  ? "/api" // En producción, usar rutas relativas
  : "http://localhost:3000/api"; // En desarrollo, usar localhost

// Crear instancia de axios
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor para agregar token a las peticiones
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor para manejar errores
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Solo redirigir si no estamos en el proceso de login
    if (
      error.response?.status === 401 &&
      !error.config.url?.includes("/login") &&
      !error.config.url?.includes("/register")
    ) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

export const apiService = {
  // Authentication endpoints
  register: async (userData: RegisterRequest): Promise<RegisterResponse> => {
    console.log("🌐 API Service: Making registration request to /register");
    console.log("🌐 API Service: Request data:", userData);
    console.log("🌐 API Service: Base URL:", API_BASE_URL);

    try {
      const response = await apiClient.post<RegisterResponse>(
        "/register",
        userData,
      );
      console.log("🌐 API Service: Registration successful:", response.data);
      return response.data;
    } catch (error: unknown) {
      console.error("🌐 API Service: Registration failed:", error);
      if (typeof error === "object" && error !== null && "response" in error) {
        const e = error as unknown as { response?: unknown };
        console.error("🌐 API Service: Error response:", e.response);
      }
      throw error;
    }
  },

  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post<LoginResponse>("/login", credentials);
    return response.data;
  },

  getProtectedData: async (): Promise<ProtectedResponse> => {
    const response = await apiClient.get<ProtectedResponse>("/protected");
    return response.data;
  },

  getUsers: async (): Promise<UsersResponse> => {
    const response = await apiClient.get<UsersResponse>("/users");
    return response.data;
  },

  healthCheck: async (): Promise<unknown> => {
    const response = await apiClient.get("/health");
    return response.data as unknown;
  },

  // Reserve Study endpoints
  reserveStudiesHealth: async (): Promise<unknown> => {
    const response = await apiClient.get("/reserve-studies/health");
    return response.data as unknown;
  },

  // Project endpoints
  createProject: async (
    projectData: Omit<
      Project,
      "id" | "profile_id" | "created_at" | "updated_at"
    >,
  ): Promise<Project> => {
    const response = await apiClient.post<Project>("/projects", projectData);
    return response.data;
  },

  getProjects: async (params?: {
    skip?: number;
    limit?: number;
  }): Promise<Project[]> => {
    const response = await apiClient.get<Project[]>("/projects", { params });
    return response.data;
  },

  getProject: async (projectId: string): Promise<Project> => {
    const response = await apiClient.get<Project>(`/projects/${projectId}`);
    return response.data;
  },

  updateProject: async (
    projectId: string,
    projectData: Partial<Project>,
  ): Promise<Project> => {
    const response = await apiClient.put<Project>(
      `/projects/${projectId}`,
      projectData,
    );
    return response.data;
  },

  deleteProject: async (projectId: string): Promise<void> => {
    await apiClient.delete(`/projects/${projectId}`);
  },

  // Component endpoints
  createComponent: async (
    projectId: string,
    componentData: Omit<
      Component,
      "id" | "project_id" | "created_at" | "updated_at"
    >,
  ): Promise<Component> => {
    const response = await apiClient.post<Component>(
      `/projects/${projectId}/components`,
      componentData,
    );
    return response.data;
  },

  getProjectComponents: async (
    projectId: string,
    params?: { category?: string; tag?: string; skip?: number; limit?: number },
  ): Promise<Component[]> => {
    const response = await apiClient.get<Component[]>(
      `/projects/${projectId}/components`,
      { params },
    );
    return response.data;
  },

  getComponent: async (
    projectId: string,
    componentId: string,
  ): Promise<Component> => {
    const response = await apiClient.get<Component>(
      `/projects/${projectId}/components/${componentId}`,
    );
    return response.data;
  },

  updateComponent: async (
    projectId: string,
    componentId: string,
    componentData: Partial<Component>,
  ): Promise<Component> => {
    const response = await apiClient.put<Component>(
      `/projects/${projectId}/components/${componentId}`,
      componentData,
    );
    return response.data;
  },

  deleteComponent: async (
    projectId: string,
    componentId: string,
  ): Promise<void> => {
    await apiClient.delete(`/projects/${projectId}/components/${componentId}`);
  },

  // Category endpoints
  createCategory: async (
    projectId: string,
    categoryData: Omit<
      Category,
      "id" | "project_id" | "created_at" | "updated_at"
    >,
  ): Promise<Category> => {
    const response = await apiClient.post<Category>(
      `/projects/${projectId}/categories`,
      categoryData,
    );
    return response.data;
  },

  getProjectCategories: async (projectId: string): Promise<Category[]> => {
    const response = await apiClient.get<Category[]>(
      `/projects/${projectId}/categories`,
    );
    return response.data;
  },

  // Analytics endpoints
  getCostAnalysis: async (projectId: string): Promise<CostAnalysis> => {
    const response = await apiClient.get<CostAnalysis>(
      `/projects/${projectId}/analytics/cost-analysis`,
    );
    return response.data;
  },

  getReserveAnalysis: async (projectId: string): Promise<ReserveAnalysis> => {
    const response = await apiClient.get<ReserveAnalysis>(
      `/projects/${projectId}/analytics/reserve-analysis`,
    );
    return response.data;
  },

  // Metro multipliers
  getMetroMultipliers: async (): Promise<unknown[]> => {
    const response = await apiClient.get("/metro-multipliers");
    return response.data as unknown[];
  },

  setProjectMetro: async (
    projectId: string,
    metroData: { metro_area: string; custom_multiplier?: number },
  ): Promise<unknown> => {
    const response = await apiClient.post(
      `/projects/${projectId}/metro-setting`,
      metroData,
    );
    return response.data as unknown;
  },

  // Component catalog
  getComponentCatalog: async (category?: string): Promise<unknown[]> => {
    const params = category ? { category } : {};
    const response = await apiClient.get("/component-catalog", { params });
    return response.data as unknown[];
  },

  // Audit logs
  getProjectAuditLogs: async (
    projectId: string,
    params?: { entity_type?: string; skip?: number; limit?: number },
  ): Promise<unknown[]> => {
    const response = await apiClient.get(`/projects/${projectId}/audit-logs`, {
      params,
    });
    return response.data as unknown[];
  },

  // Meeting endpoints
  createMeeting: async (meetingData: MeetingCreate): Promise<Meeting> => {
    const response = await apiClient.post<Meeting>("/meetings", meetingData);
    return response.data;
  },

  getProjectMeetings: async (
    projectId: string,
    params?: { skip?: number; limit?: number },
  ): Promise<Meeting[]> => {
    const response = await apiClient.get<Meeting[]>(
      `/projects/${projectId}/meetings`,
      { params },
    );
    return response.data;
  },

  getMeeting: async (meetingId: string): Promise<Meeting> => {
    const response = await apiClient.get<Meeting>(`/meetings/${meetingId}`);
    return response.data;
  },

  updateMeeting: async (
    meetingId: string,
    meetingData: MeetingUpdate,
  ): Promise<Meeting> => {
    const response = await apiClient.put<Meeting>(
      `/meetings/${meetingId}`,
      meetingData,
    );
    return response.data;
  },

  deleteMeeting: async (meetingId: string): Promise<void> => {
    await apiClient.delete(`/meetings/${meetingId}`);
  },

  // Communication endpoints
  createCommunication: async (
    communicationData: CommunicationCreate,
  ): Promise<Communication> => {
    const response = await apiClient.post<Communication>(
      "/communications",
      communicationData,
    );
    return response.data;
  },

  getProjectCommunications: async (
    projectId: string,
    params?: { skip?: number; limit?: number },
  ): Promise<Communication[]> => {
    const response = await apiClient.get<Communication[]>(
      `/projects/${projectId}/communications`,
      { params },
    );
    return response.data;
  },

  getCommunication: async (communicationId: string): Promise<Communication> => {
    const response = await apiClient.get<Communication>(
      `/communications/${communicationId}`,
    );
    return response.data;
  },

  updateCommunication: async (
    communicationId: string,
    communicationData: CommunicationUpdate,
  ): Promise<Communication> => {
    const response = await apiClient.put<Communication>(
      `/communications/${communicationId}`,
      communicationData,
    );
    return response.data;
  },

  deleteCommunication: async (communicationId: string): Promise<void> => {
    await apiClient.delete(`/communications/${communicationId}`);
  },

  // Media File endpoints
  createMediaFile: async (
    mediaFileData: MediaFileCreate,
  ): Promise<MediaFile> => {
    const response = await apiClient.post<MediaFile>(
      "/media-files",
      mediaFileData,
    );
    return response.data;
  },

  getProjectMediaFiles: async (
    projectId: string,
    params?: { skip?: number; limit?: number },
  ): Promise<MediaFile[]> => {
    const response = await apiClient.get<MediaFile[]>(
      `/projects/${projectId}/media-files`,
      { params },
    );
    return response.data;
  },

  getMediaFile: async (mediaFileId: string): Promise<MediaFile> => {
    const response = await apiClient.get<MediaFile>(
      `/media-files/${mediaFileId}`,
    );
    return response.data;
  },

  updateMediaFile: async (
    mediaFileId: string,
    mediaFileData: MediaFileUpdate,
  ): Promise<MediaFile> => {
    const response = await apiClient.put<MediaFile>(
      `/media-files/${mediaFileId}`,
      mediaFileData,
    );
    return response.data;
  },

  deleteMediaFile: async (mediaFileId: string): Promise<void> => {
    await apiClient.delete(`/media-files/${mediaFileId}`);
  },

  // Interview endpoints
  createInterview: async (
    interviewData: InterviewCreate,
  ): Promise<Interview> => {
    const response = await apiClient.post<Interview>(
      "/interviews",
      interviewData,
    );
    return response.data;
  },

  getProjectInterviews: async (
    projectId: string,
    params?: {
      skip?: number;
      limit?: number;
      interview_type?: string;
      status?: string;
    },
  ): Promise<Interview[]> => {
    const response = await apiClient.get<Interview[]>(
      `/projects/${projectId}/interviews`,
      { params },
    );
    return response.data;
  },

  getInterview: async (interviewId: string): Promise<Interview> => {
    const response = await apiClient.get<Interview>(
      `/interviews/${interviewId}`,
    );
    return response.data;
  },

  updateInterview: async (
    interviewId: string,
    interviewData: InterviewUpdate,
  ): Promise<Interview> => {
    const response = await apiClient.put<Interview>(
      `/interviews/${interviewId}`,
      interviewData,
    );
    return response.data;
  },

  deleteInterview: async (interviewId: string): Promise<void> => {
    await apiClient.delete(`/interviews/${interviewId}`);
  },

  // Inspection endpoints
  createInspection: async (
    inspectionData: InspectionCreate,
  ): Promise<Inspection> => {
    const response = await apiClient.post<Inspection>(
      "/inspections",
      inspectionData,
    );
    return response.data;
  },

  getProjectInspections: async (
    projectId: string,
    params?: {
      skip?: number;
      limit?: number;
      inspection_type?: string;
      status?: string;
    },
  ): Promise<Inspection[]> => {
    const response = await apiClient.get<Inspection[]>(
      `/projects/${projectId}/inspections`,
      { params },
    );
    return response.data;
  },

  getInspection: async (inspectionId: string): Promise<Inspection> => {
    const response = await apiClient.get<Inspection>(
      `/inspections/${inspectionId}`,
    );
    return response.data;
  },

  updateInspection: async (
    inspectionId: string,
    inspectionData: InspectionUpdate,
  ): Promise<Inspection> => {
    const response = await apiClient.put<Inspection>(
      `/inspections/${inspectionId}`,
      inspectionData,
    );
    return response.data;
  },

  deleteInspection: async (inspectionId: string): Promise<void> => {
    await apiClient.delete(`/inspections/${inspectionId}`);
  },

  // Inspection Item endpoints
  createInspectionItem: async (
    inspectionItemData: InspectionItemCreate,
  ): Promise<InspectionItem> => {
    const response = await apiClient.post<InspectionItem>(
      "/inspection-items",
      inspectionItemData,
    );
    return response.data;
  },

  getInspectionItems: async (
    inspectionId: string,
    params?: { skip?: number; limit?: number; item_type?: string },
  ): Promise<InspectionItem[]> => {
    const response = await apiClient.get<InspectionItem[]>(
      `/inspections/${inspectionId}/items`,
      { params },
    );
    return response.data;
  },

  getInspectionItem: async (
    inspectionItemId: string,
  ): Promise<InspectionItem> => {
    const response = await apiClient.get<InspectionItem>(
      `/inspection-items/${inspectionItemId}`,
    );
    return response.data;
  },

  updateInspectionItem: async (
    inspectionItemId: string,
    inspectionItemData: InspectionItemUpdate,
  ): Promise<InspectionItem> => {
    const response = await apiClient.put<InspectionItem>(
      `/inspection-items/${inspectionItemId}`,
      inspectionItemData,
    );
    return response.data;
  },

  deleteInspectionItem: async (inspectionItemId: string): Promise<void> => {
    await apiClient.delete(`/inspection-items/${inspectionItemId}`);
  },

  // Evidence endpoints
  createEvidence: async (evidenceData: EvidenceCreate): Promise<Evidence> => {
    const response = await apiClient.post<Evidence>("/evidence", evidenceData);
    return response.data;
  },

  getProjectEvidence: async (
    projectId: string,
    params?: { skip?: number; limit?: number; evidence_type?: string },
  ): Promise<Evidence[]> => {
    const response = await apiClient.get<Evidence[]>(
      `/projects/${projectId}/evidence`,
      { params },
    );
    return response.data;
  },

  getEvidence: async (evidenceId: string): Promise<Evidence> => {
    const response = await apiClient.get<Evidence>(`/evidence/${evidenceId}`);
    return response.data;
  },

  updateEvidence: async (
    evidenceId: string,
    evidenceData: EvidenceUpdate,
  ): Promise<Evidence> => {
    const response = await apiClient.put<Evidence>(
      `/evidence/${evidenceId}`,
      evidenceData,
    );
    return response.data;
  },

  deleteEvidence: async (evidenceId: string): Promise<void> => {
    await apiClient.delete(`/evidence/${evidenceId}`);
  },
};

export default apiClient;
