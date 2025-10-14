import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import * as matchers from "@testing-library/jest-dom/matchers";
import MeetingNotes from "../components/MeetingNotes";

// Extend expect with jest-dom matchers
expect.extend(matchers);

// Mock the API service
vi.mock("../services/api", () => ({
  apiService: {
    getMeeting: vi.fn(),
    createMeeting: vi.fn(),
    updateMeeting: vi.fn(),
  },
}));

import { apiService } from "../services/api";

describe("MeetingNotes", () => {
  const mockApiService = vi.mocked(apiService);

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders new meeting form correctly", () => {
    render(
      <BrowserRouter>
        <MeetingNotes
          projectId="test-project-id"
          onSave={() => {}}
          onCancel={() => {}}
        />
      </BrowserRouter>,
    );

    expect(screen.getByText("New Meeting Notes")).toBeTruthy();
    expect(screen.getByText("Meeting Title *")).toBeTruthy();
    expect(screen.getByText("Meeting Date *")).toBeTruthy();
    expect(screen.getByText("Attendees")).toBeTruthy();
    expect(screen.getByText("Agenda Items")).toBeTruthy();
    expect(screen.getByText("Discussion Notes")).toBeTruthy();
    expect(screen.getByText("Decisions Made")).toBeTruthy();
    expect(screen.getByText("Action Items")).toBeTruthy();
  });

  it("loads existing meeting data when meetingId is provided", async () => {
    const mockMeeting = {
      id: "meeting-1",
      title: "Board Meeting",
      meeting_date: "2024-01-15",
      location: "Conference Room A",
      meeting_type: "board_meeting" as const,
      attendees: ["John Doe", "Jane Smith"],
      facilitator: "John Doe",
      note_taker: "Jane Smith",
      agenda_items: ["Review budget", "Discuss maintenance"],
      discussion_notes: "Good discussion about the budget.",
      decisions: ["Approved budget increase"],
      action_items: [
        {
          description: "Update maintenance schedule",
          assignee: "Mike Johnson",
          due_date: "2024-02-01",
          status: "pending" as const,
        },
      ],
      tags: ["budget", "maintenance"],
      project_id: "test-project-id",
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z",
    };

    mockApiService.getMeeting.mockResolvedValue(mockMeeting);

    render(
      <BrowserRouter>
        <MeetingNotes
          projectId="test-project-id"
          meetingId="meeting-1"
          onSave={() => {}}
          onCancel={() => {}}
        />
      </BrowserRouter>,
    );

    await waitFor(() => {
      expect(mockApiService.getMeeting).toHaveBeenCalledWith("meeting-1");
    });

    expect(screen.getByText("Edit Meeting Notes")).toBeTruthy();

    // Wait for the form to be populated with the loaded data
    await waitFor(() => {
      const titleInput = screen.getByPlaceholderText("Enter meeting title");
      expect((titleInput as HTMLInputElement).value).toBe("Board Meeting");
    });
  });

  it("adds and removes attendees", async () => {
    render(
      <BrowserRouter>
        <MeetingNotes
          projectId="test-project-id"
          onSave={() => {}}
          onCancel={() => {}}
        />
      </BrowserRouter>,
    );

    const attendeeInput = screen.getByLabelText("Add attendee name");
    const addButtons = screen.getAllByText("Add");
    const attendeeAddButton = addButtons[0]; // First "Add" button is for attendees

    // Add attendee
    fireEvent.change(attendeeInput, { target: { value: "John Doe" } });
    fireEvent.click(attendeeAddButton);

    expect(screen.getByText("John Doe")).toBeTruthy();

    // Remove attendee
    const removeButton = screen.getAllByText("×")[0];
    fireEvent.click(removeButton);

    expect(screen.queryByText("John Doe")).toBeFalsy();
  });

  it("adds and removes agenda items", async () => {
    render(
      <BrowserRouter>
        <MeetingNotes
          projectId="test-project-id"
          onSave={() => {}}
          onCancel={() => {}}
        />
      </BrowserRouter>,
    );

    const agendaInput = screen.getByLabelText("Add agenda item");
    const addButtons = screen.getAllByText("Add");
    const agendaAddButton = addButtons[1]; // Second "Add" button is for agenda items

    // Add agenda item
    fireEvent.change(agendaInput, { target: { value: "Review budget" } });
    fireEvent.click(agendaAddButton);

    expect(screen.getByText("Review budget")).toBeTruthy();

    // Remove agenda item
    const removeButton = screen.getAllByText("Remove")[0];
    fireEvent.click(removeButton);

    expect(screen.queryByText("Review budget")).toBeFalsy();
  });

  it("adds action items", async () => {
    render(
      <BrowserRouter>
        <MeetingNotes
          projectId="test-project-id"
          onSave={() => {}}
          onCancel={() => {}}
        />
      </BrowserRouter>,
    );

    const descriptionInput = screen.getByPlaceholderText("Action description");
    const assigneeInput = screen.getByPlaceholderText("Assignee");
    // Find the date input within the action items grid
    const actionItemsLabel = screen.getByText("Action Items");
    const actionItemsSection = actionItemsLabel.closest("div");
    const dateInputs =
      actionItemsSection?.querySelectorAll('input[type="date"]') || [];
    const dueDateInput = dateInputs[0] as HTMLInputElement; // First date input in action items
    const addButton = screen.getByText("Add Action");

    // Add action item
    fireEvent.change(descriptionInput, {
      target: { value: "Update schedule" },
    });
    fireEvent.change(assigneeInput, { target: { value: "Mike Johnson" } });
    fireEvent.change(dueDateInput, { target: { value: "2024-02-01" } });
    fireEvent.click(addButton);

    expect(screen.getByText("Update schedule")).toBeTruthy();
    expect(screen.getByText(/Mike Johnson/)).toBeTruthy();
  });

  it("saves new meeting successfully", async () => {
    const mockMeeting = {
      id: "new-meeting-id",
      title: "New Meeting",
      meeting_date: "2024-01-15",
      location: "",
      meeting_type: "board_meeting" as const,
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
      project_id: "test-project-id",
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z",
    };

    mockApiService.createMeeting.mockResolvedValue(mockMeeting);

    const mockOnSave = vi.fn();

    const { container } = render(
      <BrowserRouter>
        <MeetingNotes
          projectId="test-project-id"
          onSave={mockOnSave}
          onCancel={() => {}}
        />
      </BrowserRouter>,
    );

    // Fill required fields
    const titleInput = screen.getByPlaceholderText("Enter meeting title");
    const dateInput = container.querySelector(
      'input[type="date"]',
    ) as HTMLInputElement;
    expect(dateInput).not.toBeNull();

    fireEvent.change(titleInput, { target: { value: "New Meeting" } });
    fireEvent.change(dateInput, { target: { value: "2024-01-15" } });

    // Fill discussion notes using the rich-text editor
    const editable = container.querySelector(
      '[aria-label="Discussion notes"]',
    ) as HTMLElement;
    // Simulate a simple HTML fragment entry
    editable.innerHTML = "<p>Key notes about budget</p>";
    fireEvent.input(editable);

    // Submit form
    const saveButton = screen.getByText("Save Meeting Notes");
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(mockApiService.createMeeting).toHaveBeenCalledWith({
        title: "New Meeting",
        meeting_date: "2024-01-15",
        location: "",
        meeting_type: "board_meeting",
        attendees: [],
        facilitator: "",
        note_taker: "",
        agenda_items: [],
        discussion_notes: "<p>Key notes about budget</p>",
        decisions: [],
        action_items: [],
        next_meeting_date: undefined,
        attachments: [],
        tags: [],
        project_id: "test-project-id",
      });
    });

    expect(mockOnSave).toHaveBeenCalledWith(mockMeeting);
  });

  it("calls onCancel when cancel button is clicked", () => {
    const mockOnCancel = vi.fn();

    render(
      <BrowserRouter>
        <MeetingNotes
          projectId="test-project-id"
          onSave={() => {}}
          onCancel={mockOnCancel}
        />
      </BrowserRouter>,
    );

    const cancelButton = screen.getByText("Cancel");
    fireEvent.click(cancelButton);

    expect(mockOnCancel).toHaveBeenCalled();
  });
});
