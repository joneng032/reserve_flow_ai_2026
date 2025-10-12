import { describe, it, expect, vi, beforeEach } from "vitest";
import { apiService } from "../services/api";

// Mock the entire api module
vi.mock("../services/api", () => ({
  apiService: {
    register: vi.fn(),
    login: vi.fn(),
    getProtectedData: vi.fn(),
    getUsers: vi.fn(),
    healthCheck: vi.fn(),
    reserveStudiesHealth: vi.fn(),
    createProject: vi.fn(),
    getProjects: vi.fn(),
    getProject: vi.fn(),
    updateProject: vi.fn(),
    deleteProject: vi.fn(),
    createComponent: vi.fn(),
    getProjectComponents: vi.fn(),
    getComponent: vi.fn(),
    updateComponent: vi.fn(),
    deleteComponent: vi.fn(),
    createCategory: vi.fn(),
    getProjectCategories: vi.fn(),
    getCostAnalysis: vi.fn(),
    getReserveAnalysis: vi.fn(),
    getMetroMultipliers: vi.fn(),
    setProjectMetro: vi.fn(),
    getComponentCatalog: vi.fn(),
    getProjectAuditLogs: vi.fn(),
  },
}));

describe("API Service", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Clear localStorage
    localStorage.clear();
    // Set mock token
    localStorage.setItem("token", "mock-token");
  });

  describe("Authentication", () => {
    it("should register a user", async () => {
      const mockResponse = {
        access_token: "test-token",
        token_type: "bearer",
        user: {
          id: 1,
          email: "test@example.com",
          username: "testuser",
          is_active: true,
        },
        message: "User registered successfully",
      };

      vi.mocked(apiService.register).mockResolvedValue(mockResponse);

      const result = await apiService.register({
        email: "test@example.com",
        password: "password123",
        username: "testuser",
      });

      expect(apiService.register).toHaveBeenCalledWith({
        email: "test@example.com",
        password: "password123",
        username: "testuser",
      });
      expect(result).toEqual(mockResponse);
    });

    it("should login a user", async () => {
      const mockResponse = {
        access_token: "test-token",
        token_type: "bearer",
        user: {
          id: 1,
          email: "test@example.com",
          username: "testuser",
          is_active: true,
        },
      };

      vi.mocked(apiService.login).mockResolvedValue(mockResponse);

      const result = await apiService.login({
        email: "test@example.com",
        password: "password123",
      });

      expect(apiService.login).toHaveBeenCalledWith({
        email: "test@example.com",
        password: "password123",
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe("Project Operations", () => {
    it("should create a project", async () => {
      const mockProject = {
        id: "1",
        name: "Test Project",
        client_name: "Test Client",
        current_reserve_balance: 10000,
      };

      vi.mocked(apiService.createProject).mockResolvedValue(mockProject);

      const result = await apiService.createProject({
        name: "Test Project",
        client_name: "Test Client",
        current_reserve_balance: 10000,
      });

      expect(apiService.createProject).toHaveBeenCalledWith({
        name: "Test Project",
        client_name: "Test Client",
        current_reserve_balance: 10000,
      });
      expect(result).toEqual(mockProject);
    });

    it("should get projects", async () => {
      const mockProjects = [
        { id: "1", name: "Project 1" },
        { id: "2", name: "Project 2" },
      ];

      vi.mocked(apiService.getProjects).mockResolvedValue(mockProjects);

      const result = await apiService.getProjects();

      expect(apiService.getProjects).toHaveBeenCalled();
      expect(result).toEqual(mockProjects);
    });

    it("should update a project", async () => {
      const mockProject = { id: "1", name: "Updated Project" };

      vi.mocked(apiService.updateProject).mockResolvedValue(mockProject);

      const result = await apiService.updateProject("1", {
        name: "Updated Project",
      });

      expect(apiService.updateProject).toHaveBeenCalledWith("1", {
        name: "Updated Project",
      });
      expect(result).toEqual(mockProject);
    });

    it("should delete a project", async () => {
      vi.mocked(apiService.deleteProject).mockResolvedValue(undefined);

      await apiService.deleteProject("1");

      expect(apiService.deleteProject).toHaveBeenCalledWith("1");
    });
  });

  describe("Component Operations", () => {
    it("should create a component", async () => {
      const mockComponent = {
        id: "1",
        project_id: "project-1",
        name: "Test Component",
        base_cost: 5000,
      };

      vi.mocked(apiService.createComponent).mockResolvedValue(mockComponent);

      const result = await apiService.createComponent("project-1", {
        name: "Test Component",
        base_cost: 5000,
      });

      expect(apiService.createComponent).toHaveBeenCalledWith("project-1", {
        name: "Test Component",
        base_cost: 5000,
      });
      expect(result).toEqual(mockComponent);
    });

    it("should get project components", async () => {
      const mockComponents = [
        { id: "1", project_id: "project-1", name: "Component 1" },
        { id: "2", project_id: "project-1", name: "Component 2" },
      ];

      vi.mocked(apiService.getProjectComponents).mockResolvedValue(
        mockComponents,
      );

      const result = await apiService.getProjectComponents("project-1");

      expect(apiService.getProjectComponents).toHaveBeenCalledWith("project-1");
      expect(result).toEqual(mockComponents);
    });
  });

  describe("Analytics", () => {
    it("should get cost analysis", async () => {
      const mockAnalysis = {
        total_components: 5,
        total_value: 25000,
        average_cost: 5000,
        categories_breakdown: {},
      };

      vi.mocked(apiService.getCostAnalysis).mockResolvedValue(mockAnalysis);

      const result = await apiService.getCostAnalysis("project-1");

      expect(apiService.getCostAnalysis).toHaveBeenCalledWith("project-1");
      expect(result).toEqual(mockAnalysis);
    });

    it("should get reserve analysis", async () => {
      const mockAnalysis = {
        percent_funded: 75.5,
        total_reserve_balance: 15000,
        total_liability: 20000,
        funding_gap: 5000,
        recommendations: ["Consider additional funding"],
      };

      vi.mocked(apiService.getReserveAnalysis).mockResolvedValue(mockAnalysis);

      const result = await apiService.getReserveAnalysis("project-1");

      expect(apiService.getReserveAnalysis).toHaveBeenCalledWith("project-1");
      expect(result).toEqual(mockAnalysis);
    });
  });
});
