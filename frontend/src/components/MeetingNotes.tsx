import { useState, useEffect, useCallback, useId } from "react";
import { apiService } from "../services/api";
import type { Meeting, MeetingCreate, MeetingUpdate } from "../types/api";

interface MeetingNotesProps {
  projectId: string;
  meetingId?: string;
  onSave?: (meeting: Meeting) => void;
  onCancel?: () => void;
}

interface ActionItem {
  description: string;
  assignee?: string;
  due_date?: string;
  status: "pending" | "in_progress" | "completed";
}

export default function MeetingNotes({
  projectId,
  meetingId,
  onSave,
  onCancel,
}: MeetingNotesProps) {
  const [meeting, setMeeting] = useState<Partial<Meeting>>({
    title: "",
    meeting_date: new Date().toISOString().split("T")[0],
    location: "",
    meeting_type: "board_meeting",
    attendees: [],
    facilitator: "",
    note_taker: "",
    agenda_items: [],
    discussion_notes: "",
    decisions: [],
    action_items: [],
    next_meeting_date: "",
    attachments: [],
    tags: [],
  });

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [newAttendee, setNewAttendee] = useState("");
  const [newAgendaItem, setNewAgendaItem] = useState("");
  const [newDecision, setNewDecision] = useState("");
  const [newActionItem, setNewActionItem] = useState<ActionItem>({
    description: "",
    assignee: "",
    due_date: "",
    status: "pending",
  });
  const [newTag, setNewTag] = useState("");
  const id = useId();

  const loadMeeting = useCallback(async () => {
    if (!meetingId) return;

    try {
      setLoading(true);
      const meetingData = await apiService.getMeeting(meetingId);
      setMeeting(meetingData);
    } catch (error) {
      console.error("Failed to load meeting:", error);
      alert("Failed to load meeting data");
    } finally {
      setLoading(false);
    }
  }, [meetingId]);

  useEffect(() => {
    if (meetingId) {
      loadMeeting();
    }
  }, [meetingId, loadMeeting]);

  const handleSave = async () => {
    if (!meeting.title || !meeting.meeting_date) {
      alert("Please fill in the required fields: Title and Meeting Date");
      return;
    }

    try {
      setSaving(true);
      const meetingData = {
        ...meeting,
        project_id: projectId,
        meeting_date: meeting.meeting_date,
        next_meeting_date: meeting.next_meeting_date || undefined,
      } as MeetingCreate | MeetingUpdate;

      let savedMeeting: Meeting;
      if (meetingId) {
        savedMeeting = await apiService.updateMeeting(meetingId, meetingData);
      } else {
        savedMeeting = await apiService.createMeeting(
          meetingData as MeetingCreate,
        );
      }

      onSave?.(savedMeeting);
    } catch (error) {
      console.error("Failed to save meeting:", error);
      alert("Failed to save meeting notes");
    } finally {
      setSaving(false);
    }
  };

  const addAttendee = () => {
    if (newAttendee.trim()) {
      setMeeting((prev) => ({
        ...prev,
        attendees: [...(prev.attendees || []), newAttendee.trim()],
      }));
      setNewAttendee("");
    }
  };

  const removeAttendee = (index: number) => {
    setMeeting((prev) => ({
      ...prev,
      attendees: prev.attendees?.filter((_, i) => i !== index) || [],
    }));
  };

  const addAgendaItem = () => {
    if (newAgendaItem.trim()) {
      setMeeting((prev) => ({
        ...prev,
        agenda_items: [...(prev.agenda_items || []), newAgendaItem.trim()],
      }));
      setNewAgendaItem("");
    }
  };

  const removeAgendaItem = (index: number) => {
    setMeeting((prev) => ({
      ...prev,
      agenda_items: prev.agenda_items?.filter((_, i) => i !== index) || [],
    }));
  };

  const addDecision = () => {
    if (newDecision.trim()) {
      setMeeting((prev) => ({
        ...prev,
        decisions: [...(prev.decisions || []), newDecision.trim()],
      }));
      setNewDecision("");
    }
  };

  const removeDecision = (index: number) => {
    setMeeting((prev) => ({
      ...prev,
      decisions: prev.decisions?.filter((_, i) => i !== index) || [],
    }));
  };

  const addActionItem = () => {
    if (newActionItem.description.trim()) {
      setMeeting((prev) => ({
        ...prev,
        action_items: [...(prev.action_items || []), newActionItem],
      }));
      setNewActionItem({
        description: "",
        assignee: "",
        due_date: "",
        status: "pending",
      });
    }
  };

  const removeActionItem = (index: number) => {
    setMeeting((prev) => ({
      ...prev,
      action_items: prev.action_items?.filter((_, i) => i !== index) || [],
    }));
  };

  const addTag = () => {
    if (newTag.trim()) {
      setMeeting((prev) => ({
        ...prev,
        tags: [...(prev.tags || []), newTag.trim()],
      }));
      setNewTag("");
    }
  };

  const removeTag = (index: number) => {
    setMeeting((prev) => ({
      ...prev,
      tags: prev.tags?.filter((_, i) => i !== index) || [],
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="loading-spinner-lg mx-auto"></div>
        <span className="ml-2">Loading meeting notes...</span>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">
          {meetingId ? "Edit Meeting Notes" : "New Meeting Notes"}
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
            {saving ? "Saving..." : "Save Meeting Notes"}
          </button>
        </div>
      </div>

      <div className="space-y-6">
        {/* Basic Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label
              htmlFor={`${id}-meeting-title`}
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Meeting Title *
            </label>
            <input
              id={`${id}-meeting-title`}
              type="text"
              value={meeting.title}
              onChange={(e) =>
                setMeeting((prev) => ({ ...prev, title: e.target.value }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter meeting title"
            />
          </div>

          <div>
            <label
              htmlFor={`${id}-meeting-date`}
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Meeting Date *
            </label>
            <input
              id={`${id}-meeting-date`}
              type="date"
              value={meeting.meeting_date}
              onChange={(e) =>
                setMeeting((prev) => ({
                  ...prev,
                  meeting_date: e.target.value,
                }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Location
            </label>
            <input
              type="text"
              value={meeting.location || ""}
              onChange={(e) =>
                setMeeting((prev) => ({ ...prev, location: e.target.value }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Meeting location or virtual link"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Meeting Type
            </label>
            <select
              value={meeting.meeting_type}
              onChange={(e) =>
                setMeeting((prev) => ({
                  ...prev,
                  meeting_type: e.target.value,
                }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="Meeting type"
            >
              <option value="board_meeting">Board Meeting</option>
              <option value="committee_meeting">Committee Meeting</option>
              <option value="annual_meeting">Annual Meeting</option>
              <option value="special_meeting">Special Meeting</option>
              <option value="inspection">Inspection</option>
              <option value="consultation">Consultation</option>
              <option value="other">Other</option>
            </select>
          </div>
        </div>

        {/* Facilitator and Note Taker */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Facilitator
            </label>
            <input
              type="text"
              value={meeting.facilitator || ""}
              onChange={(e) =>
                setMeeting((prev) => ({ ...prev, facilitator: e.target.value }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Meeting facilitator"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Note Taker
            </label>
            <input
              type="text"
              value={meeting.note_taker || ""}
              onChange={(e) =>
                setMeeting((prev) => ({ ...prev, note_taker: e.target.value }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Person taking notes"
            />
          </div>
        </div>

        {/* Attendees */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Attendees
          </label>
          <div className="flex space-x-2 mb-2">
            <input
              type="text"
              value={newAttendee}
              onChange={(e) => setNewAttendee(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && addAttendee()}
              className="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Add attendee name"
              aria-label="Add attendee name"
            />
            <button
              onClick={addAttendee}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Add
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {meeting.attendees?.map((attendee, index) => (
              <span
                key={index}
                className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
              >
                {attendee}
                <button
                  onClick={() => removeAttendee(index)}
                  className="ml-2 text-blue-600 hover:text-blue-800"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Agenda Items */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Agenda Items
          </label>
          <div className="flex space-x-2 mb-2">
            <input
              type="text"
              value={newAgendaItem}
              onChange={(e) => setNewAgendaItem(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && addAgendaItem()}
              className="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Add agenda item"
              aria-label="Add agenda item"
            />
            <button
              onClick={addAgendaItem}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Add
            </button>
          </div>
          <ul className="space-y-1">
            {meeting.agenda_items?.map((item, index) => (
              <li key={index} className="flex items-center space-x-2">
                <span className="flex-1 p-2 bg-gray-50 rounded">{item}</span>
                <button
                  onClick={() => removeAgendaItem(index)}
                  className="text-red-600 hover:text-red-800"
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
        </div>

        {/* Discussion Notes */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Discussion Notes
          </label>
          <textarea
            value={meeting.discussion_notes || ""}
            onChange={(e) =>
              setMeeting((prev) => ({
                ...prev,
                discussion_notes: e.target.value,
              }))
            }
            rows={6}
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Detailed notes from the meeting discussion..."
          />
        </div>

        {/* Decisions */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Decisions Made
          </label>
          <div className="flex space-x-2 mb-2">
            <input
              type="text"
              value={newDecision}
              onChange={(e) => setNewDecision(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && addDecision()}
              className="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Add decision or resolution"
              aria-label="Add decision or resolution"
            />
            <button
              onClick={addDecision}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Add
            </button>
          </div>
          <ul className="space-y-1">
            {meeting.decisions?.map((decision, index) => (
              <li key={index} className="flex items-center space-x-2">
                <span className="flex-1 p-2 bg-green-50 rounded">
                  {decision}
                </span>
                <button
                  onClick={() => removeDecision(index)}
                  className="text-red-600 hover:text-red-800"
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
        </div>

        {/* Action Items */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Action Items
          </label>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-2 mb-2">
            <input
              type="text"
              value={newActionItem.description}
              onChange={(e) =>
                setNewActionItem((prev) => ({
                  ...prev,
                  description: e.target.value,
                }))
              }
              className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Action description"
            />
            <input
              type="text"
              value={newActionItem.assignee}
              onChange={(e) =>
                setNewActionItem((prev) => ({
                  ...prev,
                  assignee: e.target.value,
                }))
              }
              className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Assignee"
            />
            <input
              id={`${id}-action-due-date`}
              type="date"
              value={newActionItem.due_date}
              onChange={(e) =>
                setNewActionItem((prev) => ({
                  ...prev,
                  due_date: e.target.value,
                }))
              }
              className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="Action item due date"
            />
            <button
              onClick={addActionItem}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Add Action
            </button>
          </div>
          <div className="space-y-2">
            {meeting.action_items?.map((action, index) => (
              <div
                key={index}
                className="flex items-center space-x-2 p-3 bg-yellow-50 rounded"
              >
                <div className="flex-1">
                  <div className="font-medium">{action.description}</div>
                  <div className="text-sm text-gray-600">
                    {action.assignee && `Assigned to: ${action.assignee}`}
                    {action.due_date && ` | Due: ${action.due_date}`}
                    <span
                      className={`ml-2 px-2 py-1 rounded text-xs ${
                        action.status === "completed"
                          ? "bg-green-200 text-green-800"
                          : action.status === "in_progress"
                          ? "bg-blue-200 text-blue-800"
                          : "bg-gray-200 text-gray-800"
                      }`}
                    >
                      {action.status.replace("_", " ")}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => removeActionItem(index)}
                  className="text-red-600 hover:text-red-800"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Next Meeting Date */}
        <div>
          <label
            htmlFor={`${id}-next-meeting-date`}
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Next Meeting Date
          </label>
          <input
            id={`${id}-next-meeting-date`}
            type="date"
            value={meeting.next_meeting_date || ""}
            onChange={(e) =>
              setMeeting((prev) => ({
                ...prev,
                next_meeting_date: e.target.value,
              }))
            }
            className="w-full md:w-1/2 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Tags */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tags
          </label>
          <div className="flex space-x-2 mb-2">
            <input
              type="text"
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && addTag()}
              className="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Add tag"
              aria-label="Add tag"
            />
            <button
              onClick={addTag}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Add
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {meeting.tags?.map((tag, index) => (
              <span
                key={index}
                className="inline-flex items-center px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm"
              >
                {tag}
                <button
                  onClick={() => removeTag(index)}
                  className="ml-2 text-purple-600 hover:text-purple-800"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
