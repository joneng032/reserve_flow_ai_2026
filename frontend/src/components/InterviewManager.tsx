import { useState, useEffect, useCallback } from "react";
import { apiService } from "../services/api";
import type { Interview, InterviewCreate, InterviewUpdate } from "../types/api";

interface InterviewManagerProps {
  projectId: string;
  interviewId?: string;
  onSave?: (interview: Interview) => void;
  onCancel?: () => void;
}

interface QuestionResponse {
  question: string;
  answer: string;
  notes?: string;
}

export default function InterviewManager({
  projectId,
  interviewId,
  onSave,
  onCancel,
}: InterviewManagerProps) {
  const [interview, setInterview] = useState<Partial<Interview>>({
    interviewee_name: "",
    interviewee_role: "",
    interviewee_contact: "",
    interview_type: "initial",
    scheduled_date: new Date().toISOString().split("T")[0],
    location: "",
    status: "scheduled",
    question_template: "",
    responses: {},
    notes: "",
    follow_up_required: false,
    follow_up_date: "",
    attachments: [],
    tags: [],
  });

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [newAttachment, setNewAttachment] = useState("");
  const [newTag, setNewTag] = useState("");
  const [questionResponses, setQuestionResponses] = useState<
    QuestionResponse[]
  >([]);
  const [newQuestion, setNewQuestion] = useState("");
  const [newAnswer, setNewAnswer] = useState("");

  const loadInterview = useCallback(async () => {
    if (!interviewId) return;

    try {
      setLoading(true);
      const interviewData = await apiService.getInterview(interviewId);
      setInterview(interviewData);

      // Convert responses object to question responses array for editing
      if (interviewData.responses) {
        const responses = Object.entries(interviewData.responses).map(
          ([question, data]: [string, unknown]) => ({
            question,
            answer: (data as { answer?: string }).answer || "",
            notes: (data as { notes?: string }).notes || "",
          }),
        );
        setQuestionResponses(responses);
      }
    } catch (error) {
      console.error("Failed to load interview:", error);
      alert("Failed to load interview data");
    } finally {
      setLoading(false);
    }
  }, [interviewId]);

  useEffect(() => {
    if (interviewId) {
      loadInterview();
    }
  }, [interviewId, loadInterview]);

  const handleSave = async () => {
    if (!interview.interviewee_name || !interview.scheduled_date) {
      alert(
        "Please fill in the required fields: Interviewee Name and Scheduled Date",
      );
      return;
    }

    try {
      setSaving(true);

      // Convert question responses back to responses object
      const responses: Record<
        string,
        { answer: string; notes?: string; order: number }
      > = {};
      questionResponses.forEach((qr, index) => {
        responses[qr.question] = {
          answer: qr.answer,
          notes: qr.notes,
          order: index,
        };
      });

      const interviewData = {
        ...interview,
        project_id: projectId,
        scheduled_date: interview.scheduled_date,
        completed_date: interview.completed_date || undefined,
        follow_up_date: interview.follow_up_date || undefined,
        responses,
      } as InterviewCreate | InterviewUpdate;

      let savedInterview: Interview;
      if (interviewId) {
        savedInterview = await apiService.updateInterview(
          interviewId,
          interviewData,
        );
      } else {
        savedInterview = await apiService.createInterview(
          interviewData as InterviewCreate,
        );
      }

      onSave?.(savedInterview);
    } catch (error) {
      console.error("Failed to save interview:", error);
      alert("Failed to save interview");
    } finally {
      setSaving(false);
    }
  };

  const addAttachment = () => {
    if (newAttachment.trim()) {
      setInterview((prev) => ({
        ...prev,
        attachments: [...(prev.attachments || []), newAttachment.trim()],
      }));
      setNewAttachment("");
    }
  };

  const removeAttachment = (index: number) => {
    setInterview((prev) => ({
      ...prev,
      attachments: prev.attachments?.filter((_, i) => i !== index) || [],
    }));
  };

  const addTag = () => {
    if (newTag.trim()) {
      setInterview((prev) => ({
        ...prev,
        tags: [...(prev.tags || []), newTag.trim()],
      }));
      setNewTag("");
    }
  };

  const removeTag = (index: number) => {
    setInterview((prev) => ({
      ...prev,
      tags: prev.tags?.filter((_, i) => i !== index) || [],
    }));
  };

  const addQuestionResponse = () => {
    if (newQuestion.trim()) {
      setQuestionResponses((prev) => [
        ...prev,
        {
          question: newQuestion.trim(),
          answer: newAnswer.trim(),
          notes: "",
        },
      ]);
      setNewQuestion("");
      setNewAnswer("");
    }
  };

  const updateQuestionResponse = (
    index: number,
    field: keyof QuestionResponse,
    value: string,
  ) => {
    setQuestionResponses((prev) =>
      prev.map((qr, i) => (i === index ? { ...qr, [field]: value } : qr)),
    );
  };

  const removeQuestionResponse = (index: number) => {
    setQuestionResponses((prev) => prev.filter((_, i) => i !== index));
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
        <span className="ml-2">Loading interview...</span>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">
          {interviewId ? "Edit Interview" : "Schedule New Interview"}
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
            {saving ? "Saving..." : "Save Interview"}
          </button>
        </div>
      </div>

      <div className="space-y-6">
        {/* Interviewee Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Interviewee Name *
            </label>
            <input
              type="text"
              value={interview.interviewee_name}
              onChange={(e) =>
                setInterview((prev) => ({
                  ...prev,
                  interviewee_name: e.target.value,
                }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Full name of interviewee"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Role/Position
            </label>
            <input
              type="text"
              value={interview.interviewee_role || ""}
              onChange={(e) =>
                setInterview((prev) => ({
                  ...prev,
                  interviewee_role: e.target.value,
                }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., Property Manager, Board President"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Contact Information
            </label>
            <input
              type="text"
              value={interview.interviewee_contact || ""}
              onChange={(e) =>
                setInterview((prev) => ({
                  ...prev,
                  interviewee_contact: e.target.value,
                }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Phone, email, or other contact info"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Interview Type
            </label>
            <select
              value={interview.interview_type}
              onChange={(e) =>
                setInterview((prev) => ({
                  ...prev,
                  interview_type: e.target.value,
                }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="Interview type"
            >
              <option value="initial">Initial Interview</option>
              <option value="follow_up">Follow-up Interview</option>
              <option value="clarification">Clarification Interview</option>
              <option value="exit">Exit Interview</option>
            </select>
          </div>
        </div>

        {/* Scheduling Information */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Scheduled Date *
            </label>
            <input
              type="date"
              value={interview.scheduled_date}
              onChange={(e) =>
                setInterview((prev) => ({
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
              value={interview.completed_date || ""}
              onChange={(e) =>
                setInterview((prev) => ({
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
              Status
            </label>
            <select
              value={interview.status}
              onChange={(e) =>
                setInterview((prev) => ({ ...prev, status: e.target.value }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="Interview status"
            >
              <option value="scheduled">Scheduled</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
        </div>

        {/* Location */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Location
          </label>
          <input
            type="text"
            value={interview.location || ""}
            onChange={(e) =>
              setInterview((prev) => ({ ...prev, location: e.target.value }))
            }
            className="w-full md:w-1/2 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Interview location or virtual meeting link"
          />
        </div>

        {/* Question Template */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Question Template
          </label>
          <select
            value={interview.question_template || ""}
            onChange={(e) =>
              setInterview((prev) => ({
                ...prev,
                question_template: e.target.value,
              }))
            }
            className="w-full md:w-1/2 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Question template"
          >
            <option value="">Select a template...</option>
            <option value="property_manager">Property Manager Interview</option>
            <option value="board_member">Board Member Interview</option>
            <option value="resident">Resident Interview</option>
            <option value="contractor">Contractor Interview</option>
            <option value="custom">Custom Questions</option>
          </select>
        </div>

        {/* Question Responses */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Interview Questions & Responses
          </label>

          {/* Add new question */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-4 p-4 bg-gray-50 rounded">
            <input
              type="text"
              value={newQuestion}
              onChange={(e) => setNewQuestion(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && addQuestionResponse()}
              className="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter question"
              aria-label="New question"
            />
            <div className="flex space-x-2">
              <input
                type="text"
                value={newAnswer}
                onChange={(e) => setNewAnswer(e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter response"
                aria-label="New answer"
              />
              <button
                onClick={addQuestionResponse}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
              >
                Add
              </button>
            </div>
          </div>

          {/* Existing questions */}
          <div className="space-y-3">
            {questionResponses.map((qr, index) => (
              <div key={index} className="p-4 border border-gray-200 rounded">
                <div className="flex justify-between items-start mb-2">
                  <strong className="text-gray-900">{qr.question}</strong>
                  <button
                    onClick={() => removeQuestionResponse(index)}
                    className="text-red-600 hover:text-red-800"
                  >
                    Remove
                  </button>
                </div>
                <textarea
                  value={qr.answer}
                  onChange={(e) =>
                    updateQuestionResponse(index, "answer", e.target.value)
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 mb-2"
                  rows={2}
                  placeholder="Response..."
                />
                <input
                  type="text"
                  value={qr.notes || ""}
                  onChange={(e) =>
                    updateQuestionResponse(index, "notes", e.target.value)
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Additional notes..."
                />
              </div>
            ))}
          </div>
        </div>

        {/* Interview Notes */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Interview Notes
          </label>
          <textarea
            value={interview.notes || ""}
            onChange={(e) =>
              setInterview((prev) => ({ ...prev, notes: e.target.value }))
            }
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="General notes and observations from the interview..."
          />
        </div>

        {/* Follow-up Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="follow_up_required"
              checked={interview.follow_up_required}
              onChange={(e) =>
                setInterview((prev) => ({
                  ...prev,
                  follow_up_required: e.target.checked,
                }))
              }
              className="rounded"
            />
            <label
              htmlFor="follow_up_required"
              className="text-sm font-medium text-gray-700"
            >
              Follow-up Required
            </label>
          </div>

          {interview.follow_up_required && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Follow-up Date
              </label>
              <input
                type="date"
                value={interview.follow_up_date || ""}
                onChange={(e) =>
                  setInterview((prev) => ({
                    ...prev,
                    follow_up_date: e.target.value,
                  }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          )}
        </div>

        {/* Attachments */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Attachments
          </label>
          <div className="flex space-x-2 mb-2">
            <input
              type="text"
              value={newAttachment}
              onChange={(e) => setNewAttachment(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && addAttachment()}
              className="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Add attachment URL or file reference"
              aria-label="New attachment"
            />
            <button
              onClick={addAttachment}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Add
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {interview.attachments?.map((attachment, index) => (
              <span
                key={index}
                className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
              >
                {attachment}
                <button
                  onClick={() => removeAttachment(index)}
                  className="ml-2 text-blue-600 hover:text-blue-800"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
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
              aria-label="New tag"
            />
            <button
              onClick={addTag}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Add
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {interview.tags?.map((tag, index) => (
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

        {/* Status Display */}
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-gray-700">
            Current Status:
          </span>
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(
              interview.status || "scheduled",
            )}`}
          >
            {interview.status?.replace("_", " ").toUpperCase()}
          </span>
        </div>
      </div>
    </div>
  );
}
