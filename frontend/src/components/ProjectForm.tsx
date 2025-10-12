import { useState, useEffect } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import { apiService } from "../services/api";
import type {
  Project,
  Component,
  CostAnalysis,
  ReserveAnalysis,
} from "../services/api";

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
  custom_fields: Record<string, any>;
}

interface Client {
  id: string;
  name: string;
  contact_name?: string;
  email?: string;
  phone?: string;
  address?: string;
}

const PROPERTY_TYPES = [
  "Condominium",
  "Townhouse",
  "Apartment Building",
  "Single Family",
  "Commercial",
  "Mixed Use",
  "Other",
];

const OWNERSHIP_STRUCTURES = [
  "Condominium Association",
  "Homeowners Association",
  "Cooperative",
  "Property Management Company",
  "Individual Owner",
  "Other",
];

const PROJECT_STATUSES = [
  "Planning",
  "Active",
  "Field Work",
  "Analysis",
  "Reporting",
  "Completed",
  "On Hold",
];

function ProjectForm({
  project,
  onSave,
  onCancel,
}: {
  project?: Project;
  onSave: (data: ProjectFormData) => Promise<void>;
  onCancel: () => void;
}) {
  const [formData, setFormData] = useState<ProjectFormData>({
    name: project?.name || "",
    client_name: project?.client_name || "",
    client_contact_name: "",
    client_email: "",
    client_phone: "",
    address: project?.address || "",
    property_type: "Condominium",
    property_size: undefined,
    property_size_unit: "sq ft",
    ownership_structure: "Condominium Association",
    current_reserve_balance: project?.current_reserve_balance || 0,
    target_funding_percentage: 100,
    project_status: "Planning",
    project_description: "",
    custom_fields: project?.custom_fields || {},
  });

  const [loading, setLoading] = useState(false);
  const [clients, setClients] = useState<Client[]>([]);
  const [showNewClientForm, setShowNewClientForm] = useState(false);

  useEffect(() => {
    loadClients();
  }, []);

  const loadClients = async () => {
    try {
      // For now, we'll get unique client names from existing projects
      // In a full implementation, this would be a separate clients table
      const projects = await apiService.getProjects();
      const uniqueClients = Array.from(
        new Set(projects.map((p) => p.client_name).filter(Boolean)),
      ).map((name) => ({ id: name, name }));

      setClients(uniqueClients);
    } catch (error) {
      console.error("Failed to load clients:", error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      alert("Project name is required");
      return;
    }

    if (!formData.client_name.trim()) {
      alert("Client name is required");
      return;
    }

    if (!formData.address.trim()) {
      alert("Property address is required");
      return;
    }

    try {
      setLoading(true);
      await onSave(formData);
    } catch (error) {
      console.error("Failed to save project:", error);
      alert("Failed to save project. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleClientSelect = (clientName: string) => {
    const client = clients.find((c) => c.name === clientName);
    if (client) {
      setFormData((prev) => ({
        ...prev,
        client_name: client.name,
        client_contact_name: client.contact_name || "",
        client_email: client.email || "",
        client_phone: client.phone || "",
      }));
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-6">
        {project ? "Edit Project" : "Create New Project"}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Project Information */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Project Information
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Project Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, name: e.target.value }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Project Description
              </label>
              <textarea
                value={formData.project_description}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    project_description: e.target.value,
                  }))
                }
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Brief description of the project scope and objectives"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Project Status
              </label>
              <select
                value={formData.project_status}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    project_status: e.target.value,
                  }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {PROJECT_STATUSES.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Target Funding Percentage
              </label>
              <input
                type="number"
                value={formData.target_funding_percentage}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    target_funding_percentage:
                      parseFloat(e.target.value) || 100,
                  }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="0"
                max="200"
                step="1"
              />
            </div>
          </div>
        </div>

        {/* Client Information */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Client Information
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Client Name *
              </label>
              <select
                value={formData.client_name}
                onChange={(e) => handleClientSelect(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select existing client...</option>
                {clients.map((client) => (
                  <option key={client.id} value={client.name}>
                    {client.name}
                  </option>
                ))}
              </select>
              <input
                type="text"
                value={formData.client_name}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    client_name: e.target.value,
                  }))
                }
                className="w-full px-3 py-2 mt-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Or enter new client name"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Contact Name
              </label>
              <input
                type="text"
                value={formData.client_contact_name}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    client_contact_name: e.target.value,
                  }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Primary contact person"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                value={formData.client_email}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    client_email: e.target.value,
                  }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Phone
              </label>
              <input
                type="tel"
                value={formData.client_phone}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    client_phone: e.target.value,
                  }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Property Information */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Property Information
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Property Address *
              </label>
              <input
                type="text"
                value={formData.address}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, address: e.target.value }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Property Type
              </label>
              <select
                value={formData.property_type}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    property_type: e.target.value,
                  }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {PROPERTY_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Ownership Structure
              </label>
              <select
                value={formData.ownership_structure}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    ownership_structure: e.target.value,
                  }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {OWNERSHIP_STRUCTURES.map((structure) => (
                  <option key={structure} value={structure}>
                    {structure}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Property Size
              </label>
              <div className="flex space-x-2">
                <input
                  type="number"
                  value={formData.property_size || ""}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      property_size: parseFloat(e.target.value) || undefined,
                    }))
                  }
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  min="0"
                  step="0.01"
                />
                <select
                  value={formData.property_size_unit}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      property_size_unit: e.target.value,
                    }))
                  }
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="sq ft">sq ft</option>
                  <option value="acres">acres</option>
                  <option value="units">units</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Reserve Fund Information */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Reserve Fund Information
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Current Reserve Balance *
              </label>
              <div className="relative">
                <span className="absolute left-3 top-2 text-gray-500">$</span>
                <input
                  type="number"
                  value={formData.current_reserve_balance}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      current_reserve_balance: parseFloat(e.target.value) || 0,
                    }))
                  }
                  className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  min="0"
                  step="0.01"
                  required
                />
              </div>
            </div>
          </div>
        </div>

        {/* Form Actions */}
        <div className="flex space-x-3 pt-4 border-t">
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading
              ? "Saving..."
              : project
              ? "Update Project"
              : "Create Project"}
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="bg-gray-300 text-gray-700 px-6 py-2 rounded hover:bg-gray-400"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

export default ProjectForm;
