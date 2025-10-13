import { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import { apiService } from "../services/api";
import type {
  Project,
  ProjectCreate,
  Component,
  CostAnalysis,
  ReserveAnalysis,
} from "../types/api";
import ProjectForm from "./ProjectForm";
import MeetingNotes from "./MeetingNotes";
import CommunicationLog from "./CommunicationLog";
import MediaUpload from "./MediaUpload";

interface ProjectCardProps {
  project: Project;
  onDelete: (projectId: string) => void;
  onOpenMeetingNotes: (projectId: string, meetingId?: string) => void;
  onOpenCommunicationLog: (projectId: string, communicationId?: string) => void;
  onOpenMediaUpload: (projectId: string) => void;
}

function ProjectCard({
  project,
  onDelete,
  onOpenMeetingNotes,
  onOpenCommunicationLog,
  onOpenMediaUpload,
}: ProjectCardProps) {
  const [components, setComponents] = useState<Component[]>([]);
  const [costAnalysis, setCostAnalysis] = useState<CostAnalysis | null>(null);
  const [reserveAnalysis, setReserveAnalysis] =
    useState<ReserveAnalysis | null>(null);
  const [loading, setLoading] = useState(true);

  const loadProjectData = useCallback(async () => {
    if (!project.id) return;

    try {
      setLoading(true);
      const [componentsData, costData, reserveData] = await Promise.all([
        apiService.getProjectComponents(project.id),
        apiService.getCostAnalysis(project.id).catch(() => null),
        apiService.getReserveAnalysis(project.id).catch(() => null),
      ]);

      setComponents(componentsData);
      setCostAnalysis(costData);
      setReserveAnalysis(reserveData);
    } catch (error) {
      console.error("Failed to load project data:", error);
    } finally {
      setLoading(false);
    }
  }, [project.id]);

  useEffect(() => {
    loadProjectData();
  }, [loadProjectData]);

  const handleDelete = async () => {
    if (!project.id) return;

    if (window.confirm(`Are you sure you want to delete "${project.name}"?`)) {
      try {
        await apiService.deleteProject(project.id);
        onDelete(project.id);
      } catch (error) {
        console.error("Failed to delete project:", error);
        alert("Failed to delete project. Please try again.");
      }
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            {project.name}
          </h3>
          {project.client_name && (
            <p className="text-gray-600 mb-1">Client: {project.client_name}</p>
          )}
          {project.address && (
            <p className="text-gray-600 mb-2">Address: {project.address}</p>
          )}
        </div>
        <button
          onClick={handleDelete}
          className="text-red-600 hover:text-red-800 p-2"
          title="Delete project"
        >
          🗑️
        </button>
      </div>

      {loading ? (
        <div className="text-center py-4">
          <div className="loading-spinner mx-auto mb-2"></div>
          <p className="text-gray-500">Loading project data...</p>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Project Stats */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="bg-blue-50 p-3 rounded">
              <div className="font-medium text-blue-900">Components</div>
              <div className="text-2xl font-bold text-blue-600">
                {components.length}
              </div>
            </div>
            <div className="bg-green-50 p-3 rounded">
              <div className="font-medium text-green-900">Reserve Balance</div>
              <div className="text-2xl font-bold text-green-600">
                ${project.current_reserve_balance?.toLocaleString() || "0"}
              </div>
            </div>
          </div>

          {/* Analytics */}
          {costAnalysis && (
            <div className="border-t pt-4">
              <h4 className="font-medium text-gray-900 mb-2">Cost Analysis</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Total Value:</span>
                  <span className="font-medium ml-2">
                    ${costAnalysis.total_value.toLocaleString()}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Average Cost:</span>
                  <span className="font-medium ml-2">
                    ${costAnalysis.average_cost.toLocaleString()}
                  </span>
                </div>
              </div>
            </div>
          )}

          {reserveAnalysis && (
            <div className="border-t pt-4">
              <h4 className="font-medium text-gray-900 mb-2">
                Reserve Analysis
              </h4>
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <div className="flex justify-between text-sm mb-1">
                    <span>Percent Funded</span>
                    <span className="font-medium">
                      {reserveAnalysis.percent_funded.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full">
                    {(() => {
                      const pct = Math.min(
                        Math.max(Math.round(reserveAnalysis.percent_funded), 0),
                        100,
                      );
                      return (
                        <progress
                          value={pct}
                          max={100}
                          className="w-full h-2 rounded-full bg-gray-200"
                          aria-label={`Percent funded: ${pct}%`}
                        />
                      );
                    })()}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex space-x-2 pt-4 border-t">
            <Link
              to={`/projects/${project.id}`}
              className="flex-1 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-center"
            >
              View Details
            </Link>
            <Link
              to={`/projects/${project.id}/components`}
              className="flex-1 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 text-center"
            >
              Manage Components
            </Link>
          </div>

          {/* Data Collection Actions */}
          <div className="flex flex-wrap gap-2 pt-2">
            <button
              onClick={() => onOpenMeetingNotes(project.id)}
              className="px-3 py-1 bg-purple-600 text-white text-sm rounded hover:bg-purple-700"
              title="Add Meeting Notes"
            >
              📝 Meeting
            </button>
            <button
              onClick={() => onOpenCommunicationLog(project.id)}
              className="px-3 py-1 bg-indigo-600 text-white text-sm rounded hover:bg-indigo-700"
              title="Log Communication"
            >
              💬 Communication
            </button>
            <button
              onClick={() => onOpenMediaUpload(project.id)}
              className="px-3 py-1 bg-orange-600 text-white text-sm rounded hover:bg-orange-700"
              title="Upload Media"
            >
              📎 Media
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function ProjectDashboard() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [activeDataCollection, setActiveDataCollection] = useState<{
    type: "meeting" | "communication" | "media" | null;
    projectId: string;
    itemId?: string;
  }>({ type: null, projectId: "" });

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const projectsData = await apiService.getProjects();
      setProjects(projectsData);
    } catch (error) {
      console.error("Failed to load projects:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (formData: ProjectCreate) => {
    try {
      const projectData = {
        name: formData.name,
        client_name: formData.client_name,
        address: formData.address,
        current_reserve_balance: formData.current_reserve_balance,
        custom_fields: {
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
          ...formData.custom_fields,
        },
      };

      const createdProject = await apiService.createProject(projectData);
      setProjects((prev) => [...prev, createdProject]);
      setShowCreateForm(false);
    } catch (error) {
      console.error("Failed to create project:", error);
      alert("Failed to create project. Please try again.");
    }
  };

  const handleDeleteProject = (projectId: string) => {
    setProjects((prev) => prev.filter((p) => p.id !== projectId));
  };

  const handleOpenMeetingNotes = (projectId: string, meetingId?: string) => {
    setActiveDataCollection({ type: "meeting", projectId, itemId: meetingId });
  };

  const handleOpenCommunicationLog = (
    projectId: string,
    communicationId?: string,
  ) => {
    setActiveDataCollection({
      type: "communication",
      projectId,
      itemId: communicationId,
    });
  };

  const handleOpenMediaUpload = (projectId: string) => {
    setActiveDataCollection({ type: "media", projectId });
  };

  const handleDataCollectionSave = () => {
    setActiveDataCollection({ type: null, projectId: "" });
    // Optionally refresh project data if needed
  };

  const handleDataCollectionCancel = () => {
    setActiveDataCollection({ type: null, projectId: "" });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner-lg mx-auto mb-4"></div>
          <p className="text-gray-600">Loading projects...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Reserve Study Projects
            </h1>
            <p className="text-gray-600 mt-2">
              Manage your reserve study projects and components
            </p>
          </div>
          <button
            onClick={() => setShowCreateForm(true)}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-medium"
          >
            + New Project
          </button>
        </div>

        {/* Create Project Form */}
        {showCreateForm && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <ProjectForm
              onSave={handleCreateProject}
              onCancel={() => setShowCreateForm(false)}
            />
          </div>
        )}

        {/* Projects Grid */}
        {projects.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 text-6xl mb-4">📊</div>
            <h3 className="text-xl font-medium text-gray-900 mb-2">
              No projects yet
            </h3>
            <p className="text-gray-600 mb-6">
              Create your first reserve study project to get started
            </p>
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-medium"
            >
              Create Your First Project
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                onDelete={handleDeleteProject}
                onOpenMeetingNotes={handleOpenMeetingNotes}
                onOpenCommunicationLog={handleOpenCommunicationLog}
                onOpenMediaUpload={handleOpenMediaUpload}
              />
            ))}
          </div>
        )}
      </div>

      {/* Data Collection Components */}
      {activeDataCollection.type === "meeting" && (
        <div className="mt-8">
          <MeetingNotes
            projectId={activeDataCollection.projectId}
            meetingId={activeDataCollection.itemId}
            onSave={handleDataCollectionSave}
            onCancel={handleDataCollectionCancel}
          />
        </div>
      )}

      {activeDataCollection.type === "communication" && (
        <div className="mt-8">
          <CommunicationLog
            projectId={activeDataCollection.projectId}
            communicationId={activeDataCollection.itemId}
            onSave={handleDataCollectionSave}
            onCancel={handleDataCollectionCancel}
          />
        </div>
      )}

      {activeDataCollection.type === "media" && (
        <div className="mt-8">
          <MediaUpload
            projectId={activeDataCollection.projectId}
            onUpload={handleDataCollectionSave}
            onCancel={handleDataCollectionCancel}
          />
        </div>
      )}
    </div>
  );
}
