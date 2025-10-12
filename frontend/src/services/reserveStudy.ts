import { apiService } from "./api";
import type {
  Project,
  Component,
  Category,
  CostAnalysis,
  ReserveAnalysis,
} from "./api";

/**
 * Reserve Study Service
 *
 * This service provides high-level functions for reserve study operations,
 * replacing the Dexie-based database operations with API calls.
 */

export class ReserveStudyService {
  // Project operations
  static async getProjects(): Promise<Project[]> {
    try {
      return await apiService.getProjects();
    } catch (error) {
      console.error("Failed to fetch projects:", error);
      throw error;
    }
  }

  static async createProject(projectData: {
    name: string;
    client_name?: string;
    address?: string;
    current_reserve_balance?: number;
    custom_fields?: Record<string, any>;
  }): Promise<Project> {
    try {
      // Get current user profile ID (this would come from auth context)
      const profileId = this.getCurrentProfileId();
      return await apiService.createProject({
        ...projectData,
        profile_id: profileId,
      });
    } catch (error) {
      console.error("Failed to create project:", error);
      throw error;
    }
  }

  static async updateProject(
    projectId: string,
    updates: Partial<Project>,
  ): Promise<Project> {
    try {
      return await apiService.updateProject(projectId, updates);
    } catch (error) {
      console.error("Failed to update project:", error);
      throw error;
    }
  }

  static async deleteProject(projectId: string): Promise<void> {
    try {
      await apiService.deleteProject(projectId);
    } catch (error) {
      console.error("Failed to delete project:", error);
      throw error;
    }
  }

  // Component operations
  static async getProjectComponents(
    projectId: string,
    filters?: {
      category?: string;
      tag?: string;
    },
  ): Promise<Component[]> {
    try {
      return await apiService.getProjectComponents(projectId, filters);
    } catch (error) {
      console.error("Failed to fetch components:", error);
      throw error;
    }
  }

  static async createComponent(
    projectId: string,
    componentData: {
      name: string;
      category?: string;
      base_cost?: number;
      useful_life?: number;
      custom_fields?: Record<string, any>;
    },
  ): Promise<Component> {
    try {
      return await apiService.createComponent(projectId, componentData);
    } catch (error) {
      console.error("Failed to create component:", error);
      throw error;
    }
  }

  static async updateComponent(
    projectId: string,
    componentId: string,
    updates: Partial<Component>,
  ): Promise<Component> {
    try {
      return await apiService.updateComponent(projectId, componentId, updates);
    } catch (error) {
      console.error("Failed to update component:", error);
      throw error;
    }
  }

  static async deleteComponent(
    projectId: string,
    componentId: string,
  ): Promise<void> {
    try {
      await apiService.deleteComponent(projectId, componentId);
    } catch (error) {
      console.error("Failed to delete component:", error);
      throw error;
    }
  }

  // Category operations
  static async getProjectCategories(projectId: string): Promise<Category[]> {
    try {
      return await apiService.getProjectCategories(projectId);
    } catch (error) {
      console.error("Failed to fetch categories:", error);
      throw error;
    }
  }

  static async createCategory(
    projectId: string,
    categoryData: {
      name: string;
      parent_id?: string;
      meta?: Record<string, any>;
    },
  ): Promise<Category> {
    try {
      return await apiService.createCategory(projectId, categoryData);
    } catch (error) {
      console.error("Failed to create category:", error);
      throw error;
    }
  }

  // Analytics operations
  static async getCostAnalysis(projectId: string): Promise<CostAnalysis> {
    try {
      return await apiService.getCostAnalysis(projectId);
    } catch (error) {
      console.error("Failed to get cost analysis:", error);
      throw error;
    }
  }

  static async getReserveAnalysis(projectId: string): Promise<ReserveAnalysis> {
    try {
      return await apiService.getReserveAnalysis(projectId);
    } catch (error) {
      console.error("Failed to get reserve analysis:", error);
      throw error;
    }
  }

  // Utility methods
  static getCurrentProfileId(): string {
    // This would be replaced with actual auth context
    // For now, return a placeholder
    return "current-user-profile-id";
  }

  // Bulk operations
  static async bulkUpdateComponents(
    projectId: string,
    updates: Array<{ id: string; data: Partial<Component> }>,
  ): Promise<Component[]> {
    try {
      const results = await Promise.all(
        updates.map(({ id, data }) =>
          this.updateComponent(projectId, id, data),
        ),
      );
      return results;
    } catch (error) {
      console.error("Failed to bulk update components:", error);
      throw error;
    }
  }

  // Search and filter utilities
  static async searchComponents(
    projectId: string,
    query: string,
    filters?: {
      category?: string;
      minCost?: number;
      maxCost?: number;
      minUsefulLife?: number;
      maxUsefulLife?: number;
    },
  ): Promise<Component[]> {
    try {
      const components = await this.getProjectComponents(projectId);

      return components.filter((component) => {
        // Text search
        const matchesQuery =
          !query ||
          component.name.toLowerCase().includes(query.toLowerCase()) ||
          component.category?.toLowerCase().includes(query.toLowerCase());

        // Apply filters
        const matchesCategory =
          !filters?.category || component.category === filters.category;
        const matchesMinCost =
          !filters?.minCost || (component.base_cost || 0) >= filters.minCost;
        const matchesMaxCost =
          !filters?.maxCost || (component.base_cost || 0) <= filters.maxCost;
        const matchesMinLife =
          !filters?.minUsefulLife ||
          (component.useful_life || 0) >= filters.minUsefulLife;
        const matchesMaxLife =
          !filters?.maxUsefulLife ||
          (component.useful_life || 0) <= filters.maxUsefulLife;

        return (
          matchesQuery &&
          matchesCategory &&
          matchesMinCost &&
          matchesMaxCost &&
          matchesMinLife &&
          matchesMaxLife
        );
      });
    } catch (error) {
      console.error("Failed to search components:", error);
      throw error;
    }
  }

  // Cost calculation utilities
  static calculateComponentValue(
    component: Component,
    metroMultiplier: number = 1.0,
  ): number {
    const baseCost = component.base_cost || 0;
    return baseCost * metroMultiplier;
  }

  static calculateTotalProjectValue(
    components: Component[],
    metroMultiplier: number = 1.0,
  ): number {
    return components.reduce(
      (total, component) =>
        total + this.calculateComponentValue(component, metroMultiplier),
      0,
    );
  }

  static calculatePercentFunded(
    currentBalance: number,
    totalLiability: number,
  ): number {
    if (totalLiability === 0) return 100;
    return Math.min((currentBalance / totalLiability) * 100, 100);
  }

  // Export utilities
  static async exportProjectData(projectId: string): Promise<any> {
    try {
      const [project, components, categories, costAnalysis, reserveAnalysis] =
        await Promise.all([
          apiService.getProject(projectId),
          this.getProjectComponents(projectId),
          this.getProjectCategories(projectId),
          this.getCostAnalysis(projectId),
          this.getReserveAnalysis(projectId),
        ]);

      return {
        project,
        components,
        categories,
        analytics: {
          costAnalysis,
          reserveAnalysis,
        },
        exportedAt: new Date().toISOString(),
      };
    } catch (error) {
      console.error("Failed to export project data:", error);
      throw error;
    }
  }
}

export default ReserveStudyService;
