import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { apiService } from "../services/api";
import type {
  Component,
  Category,
  ComponentCatalog,
  CostAnalysis,
} from "../services/api";

interface ComponentFormData {
  name: string;
  category: string;
  base_cost: number;
  useful_life: number;
  current_age_years: number;
  description?: string;
}

export default function ComponentManager() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [components, setComponents] = useState<Component[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [componentCatalog, setComponentCatalog] = useState<ComponentCatalog[]>(
    [],
  );
  const [costAnalysis, setCostAnalysis] = useState<CostAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingComponent, setEditingComponent] = useState<Component | null>(
    null,
  );
  const [formData, setFormData] = useState<ComponentFormData>({
    name: "",
    category: "",
    base_cost: 0,
    useful_life: 20,
    current_age_years: 0,
    description: "",
  });

  const loadData = useCallback(async () => {
    if (!projectId) return;

    try {
      setLoading(true);
      const [componentsData, categoriesData, catalogData, costData] =
        await Promise.all([
          apiService.getProjectComponents(projectId),
          apiService.getProjectCategories(projectId),
          apiService.getComponentCatalog(),
          apiService.getCostAnalysis(projectId).catch(() => null),
        ]);

      setComponents(componentsData);
      setCategories(categoriesData);
      setComponentCatalog(catalogData);
      setCostAnalysis(costData);
    } catch (error) {
      console.error("Failed to load component data:", error);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleCreateComponent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId) return;

    try {
      const componentData = {
        name: formData.name,
        category: formData.category,
        base_cost: formData.base_cost,
        useful_life: formData.useful_life,
        current_age_years: formData.current_age_years,
        custom_fields: {
          description: formData.description,
        },
      };

      const newComponent = await apiService.createComponent(
        projectId,
        componentData,
      );
      setComponents((prev) => [...prev, newComponent]);
      resetForm();
      setShowCreateForm(false);
      // Reload cost analysis
      loadData();
    } catch (error) {
      console.error("Failed to create component:", error);
      alert("Failed to create component. Please try again.");
    }
  };

  const handleUpdateComponent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId || !editingComponent) return;

    try {
      const componentData = {
        name: formData.name,
        category: formData.category,
        base_cost: formData.base_cost,
        useful_life: formData.useful_life,
        current_age_years: formData.current_age_years,
        custom_fields: {
          description: formData.description,
        },
      };

      const updatedComponent = await apiService.updateComponent(
        projectId,
        editingComponent.id!,
        componentData,
      );
      setComponents((prev) =>
        prev.map((c) => (c.id === editingComponent.id ? updatedComponent : c)),
      );
      resetForm();
      setEditingComponent(null);
      // Reload cost analysis
      loadData();
    } catch (error) {
      console.error("Failed to update component:", error);
      alert("Failed to update component. Please try again.");
    }
  };

  const handleDeleteComponent = async (componentId: string) => {
    if (!projectId) return;

    if (window.confirm("Are you sure you want to delete this component?")) {
      try {
        await apiService.deleteComponent(projectId, componentId);
        setComponents((prev) => prev.filter((c) => c.id !== componentId));
        // Reload cost analysis
        loadData();
      } catch (error) {
        console.error("Failed to delete component:", error);
        alert("Failed to delete component. Please try again.");
      }
    }
  };

  const handleEditComponent = (component: Component) => {
    setEditingComponent(component);
    setFormData({
      name: component.name,
      category: component.category || "",
      base_cost: component.base_cost || 0,
      useful_life: component.useful_life || 20,
      current_age_years: component.current_age_years || 0,
      description: component.custom_fields?.description || "",
    });
  };

  const resetForm = () => {
    setFormData({
      name: "",
      category: "",
      base_cost: 0,
      useful_life: 20,
      current_age_years: 0,
      description: "",
    });
  };

  const loadFromCatalog = (catalogItem: ComponentCatalog) => {
    setFormData({
      name: catalogItem.name,
      category: catalogItem.category,
      base_cost: catalogItem.typical_cost || 0,
      useful_life: catalogItem.useful_life_years || 20,
      current_age_years: 0,
      description: catalogItem.description || "",
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner-lg mx-auto mb-4"></div>
          <p className="text-gray-600">Loading components...</p>
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
            <button
              onClick={() => navigate("/dashboard")}
              className="text-blue-600 hover:text-blue-800 mb-2"
            >
              ← Back to Projects
            </button>
            <h1 className="text-3xl font-bold text-gray-900">
              Component Manager
            </h1>
            <p className="text-gray-600 mt-2">
              Manage components for your reserve study
            </p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-medium"
            >
              + Add Component
            </button>
          </div>
        </div>

        {/* Cost Analysis Summary */}
        {costAnalysis && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Project Summary</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {costAnalysis.total_components}
                </div>
                <div className="text-gray-600">Total Components</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  ${costAnalysis.total_value.toLocaleString()}
                </div>
                <div className="text-gray-600">Total Value</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  ${costAnalysis.average_cost.toLocaleString()}
                </div>
                <div className="text-gray-600">Average Cost</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {Object.keys(costAnalysis.categories_breakdown).length}
                </div>
                <div className="text-gray-600">Categories</div>
              </div>
            </div>
          </div>
        )}

        {/* Create/Edit Form */}
        {(showCreateForm || editingComponent) && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">
              {editingComponent ? "Edit Component" : "Add New Component"}
            </h2>

            {/* Component Catalog */}
            {!editingComponent && (
              <div className="mb-6">
                <h3 className="text-lg font-medium mb-3">
                  Quick Add from Catalog
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {componentCatalog.slice(0, 6).map((item) => (
                    <button
                      key={item.id}
                      onClick={() => loadFromCatalog(item)}
                      className="p-3 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 text-left"
                    >
                      <div className="font-medium text-gray-900">
                        {item.name}
                      </div>
                      <div className="text-sm text-gray-600">
                        {item.category}
                      </div>
                      <div className="text-sm text-green-600">
                        ${item.typical_cost?.toLocaleString()}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            <form
              onSubmit={
                editingComponent ? handleUpdateComponent : handleCreateComponent
              }
              className="space-y-4"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Component Name *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) =>
                      setFormData((prev) => ({ ...prev, name: e.target.value }))
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter component name"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Category
                  </label>
                  <select
                    value={formData.category}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        category: e.target.value,
                      }))
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select Category</option>
                    {categories.map((category) => (
                      <option key={category.id} value={category.name}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Base Cost ($)
                  </label>
                  <input
                    type="number"
                    value={formData.base_cost}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        base_cost: parseFloat(e.target.value) || 0,
                      }))
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter base cost"
                    min="0"
                    step="0.01"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Useful Life (Years)
                  </label>
                  <input
                    type="number"
                    value={formData.useful_life}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        useful_life: parseInt(e.target.value) || 20,
                      }))
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter useful life in years"
                    min="1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Current Age (Years)
                  </label>
                  <input
                    type="number"
                    value={formData.current_age_years}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        current_age_years: parseInt(e.target.value) || 0,
                      }))
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter current age in years"
                    min="0"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      description: e.target.value,
                    }))
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter component description"
                  rows={3}
                />
              </div>

              <div className="flex space-x-3">
                <button
                  type="submit"
                  className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
                >
                  {editingComponent ? "Update Component" : "Add Component"}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    resetForm();
                    setShowCreateForm(false);
                    setEditingComponent(null);
                  }}
                  className="bg-gray-300 text-gray-700 px-6 py-2 rounded hover:bg-gray-400"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Components List */}
        <div className="bg-white rounded-lg shadow-md">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold">
              Components ({components.length})
            </h2>
          </div>

          {components.length === 0 ? (
            <div className="p-8 text-center">
              <div className="text-gray-400 text-6xl mb-4">🔧</div>
              <h3 className="text-xl font-medium text-gray-900 mb-2">
                No components yet
              </h3>
              <p className="text-gray-600 mb-6">
                Add your first component to start building your reserve study
              </p>
              <button
                onClick={() => setShowCreateForm(true)}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-medium"
              >
                Add Your First Component
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Component
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Category
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Cost
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Life Cycle
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {components.map((component) => (
                    <tr key={component.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {component.name}
                        </div>
                        {component.custom_fields?.description && (
                          <div className="text-sm text-gray-500">
                            {component.custom_fields.description}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="inline-flex px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                          {component.category || "Uncategorized"}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${component.base_cost?.toLocaleString() || "0"}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {component.current_age_years || 0} /{" "}
                        {component.useful_life || 20} years
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                        <button
                          onClick={() => handleEditComponent(component)}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() =>
                            component.id && handleDeleteComponent(component.id)
                          }
                          className="text-red-600 hover:text-red-900"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
