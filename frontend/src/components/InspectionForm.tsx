import { useState, useEffect, useCallback } from "react";
import { apiService } from "../services/api";
import type {
  Inspection,
  InspectionCreate,
  InspectionUpdate,
  InspectionItem,
  InspectionItemCreate,
  InspectionItemUpdate,
} from "../types/api";

interface InspectionFormProps {
  projectId: string;
  inspectionId?: string;
  onSave?: (inspection: Inspection) => void;
  onCancel?: () => void;
}

interface NewInspectionItem {
  item_name: string;
  item_type: string;
  location: string;
  condition_rating: number;
  condition_description: string;
  measurement_value: number;
  measurement_unit: string;
  notes: string;
  priority: string;
  estimated_replacement_cost: number;
  estimated_remaining_life: number;
}

export default function InspectionForm({
  projectId,
  inspectionId,
  onSave,
  onCancel,
}: InspectionFormProps) {
  const [inspection, setInspection] = useState<Partial<Inspection>>({
    inspection_type: "building_exterior",
    scheduled_date: new Date().toISOString().split("T")[0],
    location: "",
    weather_conditions: "",
    temperature: undefined,
    status: "scheduled",
    overall_condition: "",
    priority_findings: "",
    recommendations: "",
    estimated_cost: undefined,
  });

  const [inspectionItems, setInspectionItems] = useState<InspectionItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editingItemId, setEditingItemId] = useState<string | null>(null);
  const [editingItem, setEditingItem] = useState<Partial<NewInspectionItem>>(
    {},
  );
  const [newItem, setNewItem] = useState<NewInspectionItem>({
    item_name: "",
    item_type: "condition",
    location: "",
    condition_rating: 3,
    condition_description: "",
    measurement_value: 0,
    measurement_unit: "",
    notes: "",
    priority: "medium",
    estimated_replacement_cost: 0,
    estimated_remaining_life: 0,
  });

  const loadInspection = useCallback(async () => {
    if (!inspectionId) return;

    try {
      setLoading(true);
      const inspectionData = await apiService.getInspection(inspectionId);
      setInspection(inspectionData);

      // Load inspection items
      const items = await apiService.getInspectionItems(inspectionId);
      setInspectionItems(items);
    } catch (error) {
      console.error("Failed to load inspection:", error);
      alert("Failed to load inspection data");
    } finally {
      setLoading(false);
    }
  }, [inspectionId]);

  useEffect(() => {
    if (inspectionId) {
      loadInspection();
    }
  }, [inspectionId, loadInspection]);

  const handleSave = async () => {
    if (!inspection.scheduled_date) {
      alert("Please fill in the required fields: Scheduled Date");
      return;
    }

    try {
      setSaving(true);
      const inspectionData = {
        ...inspection,
        project_id: projectId,
        scheduled_date: inspection.scheduled_date,
        completed_date: inspection.completed_date || undefined,
        temperature: inspection.temperature || undefined,
        estimated_cost: inspection.estimated_cost || undefined,
      } as InspectionCreate | InspectionUpdate;

      let savedInspection: Inspection;
      if (inspectionId) {
        savedInspection = await apiService.updateInspection(
          inspectionId,
          inspectionData,
        );
      } else {
        savedInspection = await apiService.createInspection(
          inspectionData as InspectionCreate,
        );
      }

      onSave?.(savedInspection);
    } catch (error) {
      console.error("Failed to save inspection:", error);
      alert("Failed to save inspection");
    } finally {
      setSaving(false);
    }
  };

  const addInspectionItem = async () => {
    if (!newItem.item_name.trim()) {
      alert("Please enter an item name");
      return;
    }

    if (!inspectionId) {
      // For new inspections, just add to local state
      const tempItem: InspectionItem = {
        ...newItem,
        id: `temp-${Date.now()}`,
        inspection_id: "temp",
        created_at: new Date().toISOString(),
      };
      setInspectionItems((prev) => [...prev, tempItem]);
      setNewItem({
        item_name: "",
        item_type: "condition",
        location: "",
        condition_rating: 3,
        condition_description: "",
        measurement_value: 0,
        measurement_unit: "",
        notes: "",
        priority: "medium",
        estimated_replacement_cost: 0,
        estimated_remaining_life: 0,
      });
      return;
    }

    try {
      const itemData: InspectionItemCreate = {
        ...newItem,
        inspection_id: inspectionId,
        measurement_value: newItem.measurement_value || undefined,
        estimated_replacement_cost:
          newItem.estimated_replacement_cost || undefined,
        estimated_remaining_life: newItem.estimated_remaining_life || undefined,
      };

      const savedItem = await apiService.createInspectionItem(itemData);
      setInspectionItems((prev) => [...prev, savedItem]);
      setNewItem({
        item_name: "",
        item_type: "condition",
        location: "",
        condition_rating: 3,
        condition_description: "",
        measurement_value: 0,
        measurement_unit: "",
        notes: "",
        priority: "medium",
        estimated_replacement_cost: 0,
        estimated_remaining_life: 0,
      });
    } catch (error) {
      console.error("Failed to add inspection item:", error);
      alert("Failed to add inspection item");
    }
  };

  const updateInspectionItem = async (
    itemId: string,
    updates: Partial<InspectionItemUpdate>,
  ) => {
    try {
      const updatedItem = await apiService.updateInspectionItem(
        itemId,
        updates,
      );
      setInspectionItems((prev) =>
        prev.map((item) => (item.id === itemId ? updatedItem : item)),
      );
    } catch (error) {
      console.error("Failed to update inspection item:", error);
      alert("Failed to update inspection item");
    }
  };

  const startEditingItem = (item: InspectionItem) => {
    setEditingItemId(item.id);
    setEditingItem({
      item_name: item.item_name,
      item_type: item.item_type,
      location: item.location || "",
      condition_rating: item.condition_rating || 3,
      condition_description: item.condition_description || "",
      measurement_value: item.measurement_value || 0,
      measurement_unit: item.measurement_unit || "",
      notes: item.notes || "",
      priority: item.priority || "medium",
      estimated_replacement_cost: item.estimated_replacement_cost || 0,
      estimated_remaining_life: item.estimated_remaining_life || 0,
    });
  };

  const saveItemEdit = async () => {
    if (!editingItemId || !editingItem.item_name?.trim()) return;

    try {
      const updates: Partial<InspectionItemUpdate> = {
        item_name: editingItem.item_name,
        item_type: editingItem.item_type,
        location: editingItem.location || undefined,
        condition_rating: editingItem.condition_rating,
        condition_description: editingItem.condition_description || undefined,
        measurement_value: editingItem.measurement_value || undefined,
        measurement_unit: editingItem.measurement_unit || undefined,
        notes: editingItem.notes || undefined,
        priority: editingItem.priority,
        estimated_replacement_cost:
          editingItem.estimated_replacement_cost || undefined,
        estimated_remaining_life:
          editingItem.estimated_remaining_life || undefined,
      };

      await updateInspectionItem(editingItemId, updates);
      setEditingItemId(null);
      setEditingItem({});
    } catch (error) {
      console.error("Failed to update inspection item:", error);
      alert("Failed to update inspection item");
    }
  };

  const cancelItemEdit = () => {
    setEditingItemId(null);
    setEditingItem({});
  };

  const removeInspectionItem = async (itemId: string) => {
    if (!inspectionId) {
      setInspectionItems((prev) => prev.filter((item) => item.id !== itemId));
      return;
    }

    try {
      await apiService.deleteInspectionItem(itemId);
      setInspectionItems((prev) => prev.filter((item) => item.id !== itemId));
    } catch (error) {
      console.error("Failed to remove inspection item:", error);
      alert("Failed to remove inspection item");
    }
  };

  const getConditionColor = (rating?: number) => {
    if (!rating) return "bg-gray-100 text-gray-800";
    if (rating >= 4) return "bg-green-100 text-green-800";
    if (rating >= 3) return "bg-yellow-100 text-yellow-800";
    if (rating >= 2) return "bg-orange-100 text-orange-800";
    return "bg-red-100 text-red-800";
  };

  const getPriorityColor = (priority?: string) => {
    switch (priority) {
      case "low":
        return "bg-blue-100 text-blue-800";
      case "medium":
        return "bg-yellow-100 text-yellow-800";
      case "high":
        return "bg-orange-100 text-orange-800";
      case "critical":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "scheduled":
        return "bg-blue-100 text-blue-800";
      case "in_progress":
        return "bg-yellow-100 text-yellow-800";
      case "completed":
        return "bg-green-100 text-green-800";
      case "cancelled":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="loading-spinner-lg mx-auto"></div>
        <span className="ml-2">Loading inspection...</span>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">
          {inspectionId ? "Edit Inspection" : "New Inspection"}
        </h2>
        <div className="flex space-x-2">
          {onCancel && (
            <button
              onClick={onCancel}
              className="px-4 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50"
              disabled={saving}
            >
              Cancel
            </button>
          )}
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save Inspection"}
          </button>
        </div>
      </div>

      <div className="space-y-6">
        {/* Inspection Details */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Inspection Type *
            </label>
            <select
              value={inspection.inspection_type}
              onChange={(e) =>
                setInspection((prev) => ({
                  ...prev,
                  inspection_type: e.target.value,
                }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="Inspection type"
            >
              <option value="building_exterior">Building Exterior</option>
              <option value="building_interior">Building Interior</option>
              <option value="site">Site</option>
              <option value="systems">Systems</option>
              <option value="roof">Roof</option>
              <option value="parking">Parking</option>
              <option value="common_areas">Common Areas</option>
              <option value="units">Units</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Location
            </label>
            <input
              type="text"
              value={inspection.location || ""}
              onChange={(e) =>
                setInspection((prev) => ({ ...prev, location: e.target.value }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Specific location within property"
              aria-label="Inspection location"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Scheduled Date *
            </label>
            <input
              type="date"
              value={inspection.scheduled_date}
              onChange={(e) =>
                setInspection((prev) => ({
                  ...prev,
                  scheduled_date: e.target.value,
                }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="Scheduled date"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Completed Date
            </label>
            <input
              type="date"
              value={inspection.completed_date || ""}
              onChange={(e) =>
                setInspection((prev) => ({
                  ...prev,
                  completed_date: e.target.value,
                }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="Completed date"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Weather Conditions
            </label>
            <input
              type="text"
              value={inspection.weather_conditions || ""}
              onChange={(e) =>
                setInspection((prev) => ({
                  ...prev,
                  weather_conditions: e.target.value,
                }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., Sunny, 72°F"
              aria-label="Weather conditions"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Temperature (°F)
            </label>
            <input
              type="number"
              value={inspection.temperature || ""}
              onChange={(e) =>
                setInspection((prev) => ({
                  ...prev,
                  temperature: e.target.value
                    ? parseFloat(e.target.value)
                    : undefined,
                }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="72"
              aria-label="Temperature"
            />
          </div>
        </div>

        {/* Status and Overall Assessment */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              value={inspection.status}
              onChange={(e) =>
                setInspection((prev) => ({ ...prev, status: e.target.value }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="Inspection status"
            >
              <option value="scheduled">Scheduled</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Overall Condition
            </label>
            <select
              value={inspection.overall_condition || ""}
              onChange={(e) =>
                setInspection((prev) => ({
                  ...prev,
                  overall_condition: e.target.value,
                }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="Overall condition"
            >
              <option value="">Select condition...</option>
              <option value="excellent">Excellent</option>
              <option value="good">Good</option>
              <option value="fair">Fair</option>
              <option value="poor">Poor</option>
              <option value="critical">Critical</option>
            </select>
          </div>
        </div>

        {/* Findings and Recommendations */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Priority Findings
            </label>
            <textarea
              value={inspection.priority_findings || ""}
              onChange={(e) =>
                setInspection((prev) => ({
                  ...prev,
                  priority_findings: e.target.value,
                }))
              }
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Key issues requiring immediate attention..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Recommendations
            </label>
            <textarea
              value={inspection.recommendations || ""}
              onChange={(e) =>
                setInspection((prev) => ({
                  ...prev,
                  recommendations: e.target.value,
                }))
              }
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Suggested actions and improvements..."
            />
          </div>
        </div>

        {/* Estimated Cost */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Estimated Repair/Replacement Cost
          </label>
          <div className="flex">
            <span className="inline-flex items-center px-3 py-2 border border-r-0 border-gray-300 bg-gray-50 text-gray-500 text-sm rounded-l">
              $
            </span>
            <input
              type="number"
              value={inspection.estimated_cost || ""}
              onChange={(e) =>
                setInspection((prev) => ({
                  ...prev,
                  estimated_cost: e.target.value
                    ? parseFloat(e.target.value)
                    : undefined,
                }))
              }
              className="flex-1 px-3 py-2 border border-gray-300 rounded-r focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="0.00"
              min="0"
              step="0.01"
              aria-label="Estimated cost"
            />
          </div>
        </div>

        {/* Inspection Items */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Inspection Items
          </h3>

          {/* Add new item form */}
          <div className="bg-gray-50 p-4 rounded-lg mb-4">
            <h4 className="text-md font-medium text-gray-800 mb-3">
              Add New Inspection Item
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mb-3">
              <input
                type="text"
                value={newItem.item_name}
                onChange={(e) =>
                  setNewItem((prev) => ({ ...prev, item_name: e.target.value }))
                }
                className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Item name"
                aria-label="Item name"
              />

              <select
                value={newItem.item_type}
                onChange={(e) =>
                  setNewItem((prev) => ({ ...prev, item_type: e.target.value }))
                }
                className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="Item type"
              >
                <option value="condition">Condition</option>
                <option value="measurement">Measurement</option>
                <option value="observation">Observation</option>
                <option value="recommendation">Recommendation</option>
              </select>

              <input
                type="text"
                value={newItem.location}
                onChange={(e) =>
                  setNewItem((prev) => ({ ...prev, location: e.target.value }))
                }
                className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Location"
                aria-label="Item location"
              />

              <div className="flex items-center space-x-2">
                <label className="text-sm text-gray-600">Rating:</label>
                <select
                  value={newItem.condition_rating}
                  onChange={(e) =>
                    setNewItem((prev) => ({
                      ...prev,
                      condition_rating: parseInt(e.target.value),
                    }))
                  }
                  className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  aria-label="Condition rating"
                >
                  <option value={1}>1 - Poor</option>
                  <option value={2}>2 - Fair</option>
                  <option value={3}>3 - Good</option>
                  <option value={4}>4 - Very Good</option>
                  <option value={5}>5 - Excellent</option>
                </select>
              </div>

              <select
                value={newItem.priority}
                onChange={(e) =>
                  setNewItem((prev) => ({ ...prev, priority: e.target.value }))
                }
                className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="Priority"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>

              <button
                onClick={addInspectionItem}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
              >
                Add Item
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <textarea
                value={newItem.condition_description}
                onChange={(e) =>
                  setNewItem((prev) => ({
                    ...prev,
                    condition_description: e.target.value,
                  }))
                }
                className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={2}
                placeholder="Condition description..."
              />

              <textarea
                value={newItem.notes}
                onChange={(e) =>
                  setNewItem((prev) => ({ ...prev, notes: e.target.value }))
                }
                className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={2}
                placeholder="Additional notes..."
              />
            </div>
          </div>

          {/* Existing items */}
          <div className="space-y-3">
            {inspectionItems.map((item) => (
              <div key={item.id} className="border border-gray-200 rounded p-4">
                {editingItemId === item.id ? (
                  // Edit mode
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <h4 className="font-semibold text-gray-900">
                        Edit Inspection Item
                      </h4>
                      <div className="flex space-x-2">
                        <button
                          onClick={saveItemEdit}
                          className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
                        >
                          Save
                        </button>
                        <button
                          onClick={cancelItemEdit}
                          className="px-3 py-1 bg-gray-600 text-white rounded hover:bg-gray-700 text-sm"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                      <input
                        type="text"
                        value={editingItem.item_name || ""}
                        onChange={(e) =>
                          setEditingItem((prev) => ({
                            ...prev,
                            item_name: e.target.value,
                          }))
                        }
                        className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Item name"
                        aria-label="Edit item name"
                      />

                      <select
                        value={editingItem.item_type || "condition"}
                        onChange={(e) =>
                          setEditingItem((prev) => ({
                            ...prev,
                            item_type: e.target.value,
                          }))
                        }
                        className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        aria-label="Edit item type"
                      >
                        <option value="condition">Condition</option>
                        <option value="measurement">Measurement</option>
                        <option value="observation">Observation</option>
                        <option value="recommendation">Recommendation</option>
                      </select>

                      <input
                        type="text"
                        value={editingItem.location || ""}
                        onChange={(e) =>
                          setEditingItem((prev) => ({
                            ...prev,
                            location: e.target.value,
                          }))
                        }
                        className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Location"
                        aria-label="Edit item location"
                      />

                      <div className="flex items-center space-x-2">
                        <label className="text-sm text-gray-600">Rating:</label>
                        <select
                          value={editingItem.condition_rating || 3}
                          onChange={(e) =>
                            setEditingItem((prev) => ({
                              ...prev,
                              condition_rating: parseInt(e.target.value),
                            }))
                          }
                          className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                          aria-label="Edit condition rating"
                        >
                          <option value={1}>1 - Poor</option>
                          <option value={2}>2 - Fair</option>
                          <option value={3}>3 - Good</option>
                          <option value={4}>4 - Very Good</option>
                          <option value={5}>5 - Excellent</option>
                        </select>
                      </div>

                      <select
                        value={editingItem.priority || "medium"}
                        onChange={(e) =>
                          setEditingItem((prev) => ({
                            ...prev,
                            priority: e.target.value,
                          }))
                        }
                        className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        aria-label="Edit priority"
                      >
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                        <option value="critical">Critical</option>
                      </select>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <textarea
                        value={editingItem.condition_description || ""}
                        onChange={(e) =>
                          setEditingItem((prev) => ({
                            ...prev,
                            condition_description: e.target.value,
                          }))
                        }
                        className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        rows={2}
                        placeholder="Condition description..."
                      />

                      <textarea
                        value={editingItem.notes || ""}
                        onChange={(e) =>
                          setEditingItem((prev) => ({
                            ...prev,
                            notes: e.target.value,
                          }))
                        }
                        className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        rows={2}
                        placeholder="Additional notes..."
                      />
                    </div>
                  </div>
                ) : (
                  // View mode
                  <>
                    <div className="flex justify-between items-start mb-3">
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900">
                          {item.item_name}
                        </h4>
                        <div className="flex flex-wrap gap-2 mt-1">
                          <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                            {item.item_type}
                          </span>
                          {item.location && (
                            <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded text-xs">
                              {item.location}
                            </span>
                          )}
                          <span
                            className={`px-2 py-1 rounded text-xs ${getConditionColor(
                              item.condition_rating,
                            )}`}
                          >
                            Rating: {item.condition_rating}/5
                          </span>
                          <span
                            className={`px-2 py-1 rounded text-xs ${getPriorityColor(
                              item.priority,
                            )}`}
                          >
                            {item.priority}
                          </span>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => startEditingItem(item)}
                          className="text-blue-600 hover:text-blue-800"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => removeInspectionItem(item.id)}
                          className="text-red-600 hover:text-red-800"
                        >
                          Remove
                        </button>
                      </div>
                    </div>

                    {item.condition_description && (
                      <p className="text-gray-700 mb-2">
                        {item.condition_description}
                      </p>
                    )}

                    {item.notes && (
                      <p className="text-gray-600 text-sm">{item.notes}</p>
                    )}

                    {(item.measurement_value ||
                      item.estimated_replacement_cost ||
                      item.estimated_remaining_life) && (
                      <div className="mt-2 text-sm text-gray-600">
                        {item.measurement_value && (
                          <span>
                            Measurement: {item.measurement_value}{" "}
                            {item.measurement_unit} |{" "}
                          </span>
                        )}
                        {item.estimated_replacement_cost && (
                          <span>
                            Est. Cost: $
                            {item.estimated_replacement_cost.toLocaleString()} |{" "}
                          </span>
                        )}
                        {item.estimated_remaining_life && (
                          <span>
                            Remaining Life: {item.estimated_remaining_life}{" "}
                            years
                          </span>
                        )}
                      </div>
                    )}
                  </>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Status Display */}
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-gray-700">
            Current Status:
          </span>
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(
              inspection.status || "scheduled",
            )}`}
          >
            {inspection.status?.replace("_", " ").toUpperCase()}
          </span>
        </div>
      </div>
    </div>
  );
}
