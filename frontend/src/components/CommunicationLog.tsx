import { useState, useEffect, useCallback } from "react";
import { apiService } from "../services/api";
import type { Communication, CommunicationCreate } from "../types/api";

interface CommunicationLogProps {
  projectId: string;
}

export default function CommunicationLog({ projectId }: CommunicationLogProps) {
  const [communications, setCommunications] = useState<Communication[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [filterType, setFilterType] = useState<string>("all");
  const [showForm, setShowForm] = useState(false);

  // Form state for new communication
  const [newCommunication, setNewCommunication] = useState({
    communication_type: "email" as
      | "email"
      | "phone"
      | "meeting"
      | "letter"
      | "text"
      | "video_call"
      | "other",
    direction: "outbound" as "inbound" | "outbound",
    contact_name: "",
    contact_method: "",
    subject: "",
    content: "",
    sender: "",
    recipient: "",
    response_required: false,
    response_deadline: "",
    status: "draft" as "draft" | "sent" | "delivered" | "read" | "responded",
    tags: [] as string[],
  });

  const loadCommunications = useCallback(async () => {
    try {
      setLoading(true);
      const data = await apiService.getProjectCommunications(projectId);
      setCommunications(data);
    } catch (error) {
      console.error("Failed to load communications:", error);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    loadCommunications();
  }, [loadCommunications]);

  const handleAddCommunication = async () => {
    if (
      !newCommunication.contact_name ||
      !newCommunication.subject ||
      !newCommunication.content
    ) {
      alert(
        "Please fill in the required fields: Contact name, Subject, and Message",
      );
      return;
    }

    try {
      setSaving(true);
      const communicationData: CommunicationCreate = {
        project_id: projectId,
        communication_type: newCommunication.communication_type,
        direction: newCommunication.direction,
        contact_name: newCommunication.contact_name,
        contact_method: newCommunication.contact_method,
        subject: newCommunication.subject,
        content: newCommunication.content,
        attachments: [],
        follow_up_required: newCommunication.response_required,
        follow_up_date: newCommunication.response_deadline || undefined,
        follow_up_notes: "",
        status: newCommunication.status,
        tags: newCommunication.tags,
        related_meeting_id: undefined,
        related_component_id: undefined,
      };

      await apiService.createCommunication(communicationData);

      // Reset form and reload communications
      setNewCommunication({
        communication_type: "email",
        direction: "outbound",
        contact_name: "",
        contact_method: "",
        subject: "",
        content: "",
        sender: "",
        recipient: "",
        response_required: false,
        response_deadline: "",
        status: "draft",
        tags: [],
      });
      setShowForm(false);
      await loadCommunications();
    } catch (error) {
      console.error("Failed to add communication:", error);
      alert("Failed to add communication");
    } finally {
      setSaving(false);
    }
  };

  const handleStatusChange = async (
    communicationId: string,
    newStatus: string,
  ) => {
    try {
      await apiService.updateCommunication(communicationId, {
        status: newStatus,
      });
      await loadCommunications();
    } catch (error) {
      console.error("Failed to update communication status:", error);
      alert("Failed to update status");
    }
  };

  const filteredCommunications = communications.filter(
    (comm) => filterType === "all" || comm.communication_type === filterType,
  );

  const isOverdue = (dateString: string) => {
    if (!dateString) return false;
    const deadline = new Date(dateString);
    const today = new Date();
    return deadline < today;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="loading-spinner-lg mx-auto"></div>
        <span className="ml-2">Loading communications...</span>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Communication Log</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          {showForm ? "Cancel" : "Add New Communication"}
        </button>
      </div>

      {/* Filter */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Filter by type
        </label>
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          aria-label="Filter by type"
        >
          <option value="all">All Types</option>
          <option value="email">Email</option>
          <option value="phone">Phone</option>
          <option value="meeting">Meeting</option>
          <option value="letter">Letter</option>
          <option value="text">Text Message</option>
          <option value="video_call">Video Call</option>
          <option value="other">Other</option>
        </select>
      </div>

      {/* Add New Communication Form */}
      {showForm && (
        <div className="mb-8 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-lg font-semibold mb-4">Add New Communication</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Communication Type
              </label>
              <select
                value={newCommunication.communication_type}
                onChange={(e) =>
                  setNewCommunication((prev) => ({
                    ...prev,
                    communication_type: e.target.value as
                      | "email"
                      | "phone"
                      | "meeting"
                      | "letter"
                      | "text"
                      | "video_call"
                      | "other",
                  }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="Communication Type"
              >
                <option value="email">Email</option>
                <option value="phone">Phone Call</option>
                <option value="meeting">In-Person Meeting</option>
                <option value="letter">Letter</option>
                <option value="text">Text Message</option>
                <option value="video_call">Video Call</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Direction
              </label>
              <select
                value={newCommunication.direction}
                onChange={(e) =>
                  setNewCommunication((prev) => ({
                    ...prev,
                    direction: e.target.value as "inbound" | "outbound",
                  }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="Direction"
              >
                <option value="inbound">Inbound (Received)</option>
                <option value="outbound">Outbound (Sent)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Contact name
              </label>
              <input
                type="text"
                value={newCommunication.contact_name}
                onChange={(e) =>
                  setNewCommunication((prev) => ({
                    ...prev,
                    contact_name: e.target.value,
                  }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Contact name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Contact method
              </label>
              <input
                type="text"
                value={newCommunication.contact_method}
                onChange={(e) =>
                  setNewCommunication((prev) => ({
                    ...prev,
                    contact_method: e.target.value,
                  }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Email, phone, etc."
                aria-label="Contact method"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Who sent this communication?
              </label>
              <input
                type="text"
                value={newCommunication.sender}
                onChange={(e) =>
                  setNewCommunication((prev) => ({
                    ...prev,
                    sender: e.target.value,
                  }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Who sent this communication?"
                aria-label="Sender"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Who received this communication?
              </label>
              <input
                type="text"
                value={newCommunication.recipient}
                onChange={(e) =>
                  setNewCommunication((prev) => ({
                    ...prev,
                    recipient: e.target.value,
                  }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Who received this communication?"
                aria-label="Recipient"
              />
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Subject
            </label>
            <input
              type="text"
              value={newCommunication.subject}
              onChange={(e) =>
                setNewCommunication((prev) => ({
                  ...prev,
                  subject: e.target.value,
                }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter communication subject"
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Message
            </label>
            <textarea
              value={newCommunication.content}
              onChange={(e) =>
                setNewCommunication((prev) => ({
                  ...prev,
                  content: e.target.value,
                }))
              }
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter the full message or communication details"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={newCommunication.response_required}
                onChange={(e) =>
                  setNewCommunication((prev) => ({
                    ...prev,
                    response_required: e.target.checked,
                  }))
                }
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                id="response-required"
              />
              <label
                htmlFor="response-required"
                className="ml-2 text-sm font-medium text-gray-700"
              >
                Response Required
              </label>
            </div>

            {newCommunication.response_required && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Response Deadline
                </label>
                <input
                  type="date"
                  value={newCommunication.response_deadline}
                  onChange={(e) =>
                    setNewCommunication((prev) => ({
                      ...prev,
                      response_deadline: e.target.value,
                    }))
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  aria-label="Response Deadline"
                />
              </div>
            )}
          </div>

          <div className="flex justify-end">
            <button
              onClick={handleAddCommunication}
              disabled={saving}
              className="px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
            >
              {saving ? "Adding..." : "Add Communication"}
            </button>
          </div>
        </div>
      )}

      {/* Communications List */}
      <div className="space-y-4">
        {filteredCommunications.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No communications found.
          </div>
        ) : (
          filteredCommunications.map((comm) => (
            <div
              key={comm.id}
              className="border border-gray-200 rounded-lg p-4"
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex-1">
                  <h4 className="font-semibold text-lg">{comm.subject}</h4>
                  <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                    <span>{comm.contact_name}</span>
                    <span>{comm.communication_type}</span>
                    <span>{comm.direction}</span>
                    <span>
                      {new Date(comm.created_at || "").toLocaleDateString()}
                    </span>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <select
                    value={comm.status}
                    onChange={(e) =>
                      handleStatusChange(comm.id, e.target.value)
                    }
                    className="px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    aria-label="Communication status"
                  >
                    <option value="draft">Draft</option>
                    <option value="sent">Sent</option>
                    <option value="delivered">Delivered</option>
                    <option value="read">Read</option>
                    <option value="responded">Responded</option>
                  </select>
                  {comm.follow_up_required && comm.follow_up_date && (
                    <span
                      className={`px-2 py-1 text-xs rounded ${
                        isOverdue(comm.follow_up_date)
                          ? "bg-red-100 text-red-800"
                          : "bg-yellow-100 text-yellow-800"
                      }`}
                    >
                      {isOverdue(comm.follow_up_date)
                        ? "Overdue"
                        : "Follow-up Needed"}
                    </span>
                  )}
                </div>
              </div>

              <div className="text-gray-700 mb-2">
                {comm.content && comm.content.length > 200
                  ? `${comm.content.substring(0, 200)}...`
                  : comm.content || ""}
              </div>

              {comm.tags && comm.tags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {comm.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
