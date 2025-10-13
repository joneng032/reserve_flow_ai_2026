import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { apiService } from "../services/api";
import type {
  Project,
  Component,
  CostAnalysis,
  ReserveAnalysis,
} from "../services/api";
import ProjectForm from "./ProjectForm";

interface ProjectFormData {
  name: string;
  client_name: string;
  client_contact_name?: string;
  client_email?: string;
  client_phone?: string;
  address: string;
  property_type?: string;
  property_size?: number;
  property_size_unit?: string;
  ownership_structure?: string;
  current_reserve_balance: number;
  target_funding_percentage?: number;
  project_status?: string;
  project_description?: string;
  custom_fields: Record<string, unknown>;
}

export default function ProjectDetails() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  const [project, setProject] = useState<Project | null>(null);
  const [components, setComponents] = useState<Component[]>([]);
  const [costAnalysis, setCostAnalysis] = useState<CostAnalysis | null>(null);
  const [reserveAnalysis, setReserveAnalysis] =
    useState<ReserveAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);

  const loadProjectData = useCallback(async () => {
    if (!projectId) return;

    try {
      setLoading(true);
      const [projectData, componentsData, costData, reserveData] =
        await Promise.all([
          apiService.getProject(projectId),
          apiService.getProjectComponents(projectId),
          apiService.getCostAnalysis(projectId).catch(() => null),
          apiService.getReserveAnalysis(projectId).catch(() => null),
        ]);

      setProject(projectData);
      setComponents(componentsData);
      setCostAnalysis(costData);
      setReserveAnalysis(reserveData);
    } catch (error) {
      console.error("Failed to load project data:", error);
      alert("Failed to load project data. Please try again.");
      navigate("/projects");
    } finally {
      setLoading(false);
    }
  }, [projectId, navigate]);

  useEffect(() => {
    if (projectId) {
      loadProjectData();
    }
  }, [projectId, loadProjectData]);

  const handleSaveProject = async (formData: ProjectFormData) => {
    if (!projectId) return;

    try {
      const updatedProject = await apiService.updateProject(projectId, {
        name: formData.name,
        client_name: formData.client_name,
        address: formData.address,
        current_reserve_balance: formData.current_reserve_balance,
        custom_fields: {
          ...formData.custom_fields,
          client_contact_name: formData.client_contact_name,
          client_email: formData.client_email,
          client_phone: formData.client_phone,
          property_type: formData.property_type,
          property_size: formData.property_size,
          property_size_unit: formData.property_size_unit,
          ownership_structure: formData.ownership_structure,
          target_funding_percentage: formData.target_funding_percentage,
          project_status: formData.project_status,
          project_description: formData.project_description,
        },
      });

      setProject(updatedProject);
      setEditing(false);
    } catch (error) {
      console.error("Failed to update project:", error);
      throw error;
    }
  };

  const handleDeleteProject = async () => {
    if (!projectId) return;

    if (
      window.confirm(
        `Are you sure you want to delete "${project?.name}"? This action cannot be undone.`,
      )
    ) {
      try {
        await apiService.deleteProject(projectId);
        navigate("/projects");
      } catch (error) {
        console.error("Failed to delete project:", error);
        alert("Failed to delete project. Please try again.");
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner-lg mx-auto mb-4"></div>
          <p className="text-gray-600">Loading project details...</p>
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-xl font-medium text-gray-900 mb-2">
            Project Not Found
          </h3>
          <p className="text-gray-600 mb-6">
            The requested project could not be found.
          </p>
          <button
            onClick={() => navigate("/projects")}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-medium"
          >
            Back to Projects
          </button>
        </div>
      </div>
    );
  }

  if (editing) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-6">
            <button
              onClick={() => setEditing(false)}
              className="text-blue-600 hover:text-blue-800 flex items-center"
            >
              ← Back to Project Details
            </button>
          </div>
          <ProjectForm
            project={project}
            onSave={handleSaveProject}
            onCancel={() => setEditing(false)}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex justify-between items-start mb-8">
          <div>
            <div className="flex items-center space-x-4 mb-2">
              <button
                onClick={() => navigate("/projects")}
                className="text-blue-600 hover:text-blue-800"
              >
                ← Projects
              </button>
              <span className="text-gray-400">/</span>
              <h1 className="text-3xl font-bold text-gray-900">
                {project.name}
              </h1>
            </div>
            {project.custom_fields?.project_description && (
              <p className="text-gray-600 mt-2">
                {project.custom_fields.project_description}
              </p>
            )}
          </div>
          <div className="flex space-x-3">
            <button
              onClick={() => setEditing(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Edit Project
            </button>
            <button
              onClick={handleDeleteProject}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            >
              Delete Project
            </button>
          </div>
        </div>

        {/* Project Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="text-2xl mr-3">🏢</div>
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <p className="text-lg font-semibold">
                  {project.custom_fields?.project_status || "Planning"}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="text-2xl mr-3">💰</div>
              <div>
                <p className="text-sm text-gray-600">Reserve Balance</p>
                <p className="text-lg font-semibold">
                  ${project.current_reserve_balance?.toLocaleString() || "0"}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="text-2xl mr-3">🔧</div>
              <div>
                <p className="text-sm text-gray-600">Components</p>
                <p className="text-lg font-semibold">{components.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="text-2xl mr-3">📊</div>
              <div>
                <p className="text-sm text-gray-600">Target Funding</p>
                <p className="text-lg font-semibold">
                  {project.custom_fields?.target_funding_percentage || 100}%
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Project Information */}
          <div className="lg:col-span-2 space-y-6">
            {/* Client Information */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Client Information</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Client Name
                  </label>
                  <p className="text-gray-900">{project.client_name}</p>
                </div>
                {project.custom_fields?.client_contact_name && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Contact Name
                    </label>
                    <p className="text-gray-900">
                      {project.custom_fields.client_contact_name}
                    </p>
                  </div>
                )}
                {project.custom_fields?.client_email && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Email
                    </label>
                    <p className="text-gray-900">
                      {project.custom_fields.client_email}
                    </p>
                  </div>
                )}
                {project.custom_fields?.client_phone && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Phone
                    </label>
                    <p className="text-gray-900">
                      {project.custom_fields.client_phone}
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Property Information */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">
                Property Information
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Address
                  </label>
                  <p className="text-gray-900">{project.address}</p>
                </div>
                {project.custom_fields?.property_type && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Property Type
                    </label>
                    <p className="text-gray-900">
                      {project.custom_fields.property_type}
                    </p>
                  </div>
                )}
                {project.custom_fields?.ownership_structure && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Ownership Structure
                    </label>
                    <p className="text-gray-900">
                      {project.custom_fields.ownership_structure}
                    </p>
                  </div>
                )}
                {project.custom_fields?.property_size && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Property Size
                    </label>
                    <p className="text-gray-900">
                      {project.custom_fields.property_size}{" "}
                      {project.custom_fields.property_size_unit}
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Reserve Analysis */}
            {reserveAnalysis && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">Reserve Analysis</h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Percent Funded</span>
                    <span className="font-semibold text-lg">
                      {reserveAnalysis.percent_funded.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full">
                    {(() => {
                      const pct = Math.min(
                        Math.max(Math.round(reserveAnalysis.percent_funded), 0),
                        100,
                      );
                      const colorClass =
                        pct >= 100
                          ? "bg-green-600"
                          : pct >= 75
                          ? "bg-blue-600"
                          : pct >= 50
                          ? "bg-yellow-600"
                          : "bg-red-600";
                      return (
                        <progress
                          value={pct}
                          max={100}
                          className={`w-full h-3 rounded-full ${colorClass}`}
                          aria-label={`Percent funded: ${pct}%`}
                        />
                      );
                    })()}
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Total Liability:</span>
                      <span className="font-medium ml-2">
                        ${reserveAnalysis.total_liability.toLocaleString()}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">Funding Gap:</span>
                      <span className="font-medium ml-2">
                        ${reserveAnalysis.funding_gap.toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Cost Analysis */}
            {costAnalysis && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">Cost Analysis</h2>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-blue-50 p-4 rounded">
                    <div className="text-sm text-blue-600">Total Value</div>
                    <div className="text-2xl font-bold text-blue-900">
                      ${costAnalysis.total_value.toLocaleString()}
                    </div>
                  </div>
                  <div className="bg-green-50 p-4 rounded">
                    <div className="text-sm text-green-600">Average Cost</div>
                    <div className="text-2xl font-bold text-green-900">
                      ${costAnalysis.average_cost.toLocaleString()}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Quick Actions Sidebar */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <Link
                  to={`/projects/${projectId}/components`}
                  className="block w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-center"
                >
                  Manage Components
                </Link>
                <Link
                  to={`/projects/${projectId}/inspections`}
                  className="block w-full bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 text-center"
                >
                  Field Inspections
                </Link>
                <Link
                  to={`/projects/${projectId}/reports`}
                  className="block w-full bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 text-center"
                >
                  Generate Report
                </Link>
                <Link
                  to={`/projects/${projectId}/meetings`}
                  className="block w-full bg-orange-600 text-white px-4 py-2 rounded hover:bg-orange-700 text-center"
                >
                  Meeting Notes
                </Link>
              </div>
            </div>

            {/* Recent Components */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Recent Components</h3>
              {components.length === 0 ? (
                <p className="text-gray-500 text-sm">No components added yet</p>
              ) : (
                <div className="space-y-2">
                  {components.slice(0, 5).map((component) => (
                    <div
                      key={component.id}
                      className="flex justify-between items-center py-2 border-b border-gray-100 last:border-b-0"
                    >
                      <div>
                        <p className="font-medium text-sm">{component.name}</p>
                        <p className="text-xs text-gray-500">
                          {component.category}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-sm">
                          ${component.base_cost?.toLocaleString()}
                        </p>
                        <p className="text-xs text-gray-500">
                          {component.useful_life} yrs
                        </p>
                      </div>
                    </div>
                  ))}
                  {components.length > 5 && (
                    <Link
                      to={`/projects/${projectId}/components`}
                      className="text-blue-600 hover:text-blue-800 text-sm block mt-3"
                    >
                      View all {components.length} components →
                    </Link>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
