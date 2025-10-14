import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import * as matchers from "@testing-library/jest-dom/matchers";
import CommunicationLog from "../components/CommunicationLog";

// Extend expect with jest-dom matchers
expect.extend(matchers);

// Mock the API service
vi.mock("../services/api", () => ({
  apiService: {
    getProjectCommunications: vi.fn(),
    createCommunication: vi.fn(),
    updateCommunication: vi.fn(),
    deleteCommunication: vi.fn(),
  },
}));

// Mock window.alert
Object.defineProperty(window, "alert", {
  writable: true,
  value: vi.fn(),
});

import { apiService } from "../services/api";

describe("CommunicationLog", () => {
  const mockApiService = vi.mocked(apiService);

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders communication log correctly", async () => {
    mockApiService.getProjectCommunications.mockResolvedValue([]);

    render(
      <BrowserRouter>
        <CommunicationLog projectId="test-project-id" />
      </BrowserRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText("Communication Log")).toBeTruthy();
    });
    expect(screen.getByText("Add New Communication")).toBeTruthy();
    expect(screen.getByText("Filter by type")).toBeTruthy();
  });

  it("loads existing communications on mount", async () => {
    const mockCommunications = [
      {
        id: "comm-1",
        project_id: "test-project-id",
        communication_type: "email",
        direction: "outbound",
        contact_name: "John Doe",
        contact_method: "email",
        subject: "Budget Update",
        content: "Here is the latest budget information.",
        attachments: [],
        follow_up_required: true,
        follow_up_date: "2024-01-22",
        follow_up_notes: "Follow up needed",
        status: "sent",
        tags: ["budget", "urgent"],
        created_at: "2024-01-15T10:00:00Z",
        updated_at: "2024-01-15T10:00:00Z",
      },
    ];

    mockApiService.getProjectCommunications.mockResolvedValue(
      mockCommunications,
    );

    render(
      <BrowserRouter>
        <CommunicationLog projectId="test-project-id" />
      </BrowserRouter>,
    );

    await waitFor(() => {
      expect(mockApiService.getProjectCommunications).toHaveBeenCalledWith(
        "test-project-id",
      );
    });

    expect(screen.getByText("Budget Update")).toBeTruthy();
    expect(screen.getByText("John Doe")).toBeTruthy();
    expect(screen.getByText("email")).toBeTruthy();
  });

  it("adds new communication successfully", async () => {
    mockApiService.createCommunication.mockResolvedValue({
      id: "new-comm-id",
      project_id: "test-project-id",
      communication_type: "email",
      direction: "outbound",
      contact_name: "Jane Smith",
      contact_method: "email",
      subject: "New Communication",
      content: "This is a test message.",
      attachments: [],
      follow_up_required: false,
      follow_up_date: "",
      follow_up_notes: "",
      status: "draft",
      tags: [],
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z",
    });
    mockApiService.getProjectCommunications.mockResolvedValue([]);

    render(
      <BrowserRouter>
        <CommunicationLog projectId="test-project-id" />
      </BrowserRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText("Communication Log")).toBeTruthy();
    });

    // Click "Add New Communication" to show the form
    const addButton = screen.getByText("Add New Communication");
    fireEvent.click(addButton);

    // Fill form fields
    const typeSelect = screen.getByLabelText("Communication Type");
    const directionSelect = screen.getByLabelText("Direction");
    const contactNameInput = screen.getByPlaceholderText("Contact name");
    const subjectInput = screen.getByPlaceholderText(
      "Enter communication subject",
    );
    const contentTextarea = screen.getByPlaceholderText(
      "Enter the full message or communication details",
    );
    const submitButton = screen.getByText("Add Communication");

    fireEvent.change(typeSelect, { target: { value: "email" } });
    fireEvent.change(directionSelect, { target: { value: "outbound" } });
    fireEvent.change(contactNameInput, { target: { value: "Jane Smith" } });
    fireEvent.change(subjectInput, { target: { value: "New Communication" } });
    fireEvent.change(contentTextarea, {
      target: { value: "This is a test message." },
    });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockApiService.createCommunication).toHaveBeenCalledWith({
        project_id: "test-project-id",
        communication_type: "email",
        direction: "outbound",
        contact_name: "Jane Smith",
        contact_method: "",
        subject: "New Communication",
        content: "This is a test message.",
        attachments: [],
        follow_up_required: false,
        follow_up_date: undefined,
        follow_up_notes: "",
        status: "draft",
        tags: [],
        related_meeting_id: undefined,
        related_component_id: undefined,
      });
    });

    expect(screen.getByText("Communication Log")).toBeTruthy();
  });

  it("filters communications by type", async () => {
    const mockCommunications = [
      {
        id: "comm-1",
        project_id: "test-project-id",
        communication_type: "email",
        direction: "outbound",
        contact_name: "John",
        subject: "Email Communication",
        content: "Email content",
        status: "sent",
        created_at: "2024-01-15T10:00:00Z",
        updated_at: "2024-01-15T10:00:00Z",
      },
      {
        id: "comm-2",
        project_id: "test-project-id",
        communication_type: "phone",
        direction: "outbound",
        contact_name: "Jane",
        subject: "Phone Call",
        content: "Call content",
        status: "sent",
        created_at: "2024-01-16T10:00:00Z",
        updated_at: "2024-01-16T10:00:00Z",
      },
    ];

    mockApiService.getProjectCommunications.mockResolvedValue(
      mockCommunications,
    );

    render(
      <BrowserRouter>
        <CommunicationLog projectId="test-project-id" />
      </BrowserRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText("Email Communication")).toBeTruthy();
      expect(screen.getByText("Phone Call")).toBeTruthy();
    });

    // Filter by email
    const filterSelect = screen.getByLabelText("Filter by type");
    fireEvent.change(filterSelect, { target: { value: "email" } });

    expect(screen.getByText("Email Communication")).toBeTruthy();
    expect(screen.queryByText("Phone Call")).toBeFalsy();
  });

  it("marks communication as requiring response", async () => {
    mockApiService.getProjectCommunications.mockResolvedValue([]);
    mockApiService.createCommunication.mockResolvedValue({
      id: "new-comm-id",
      project_id: "test-project-id",
      communication_type: "email",
      direction: "outbound",
      contact_name: "Manager",
      subject: "Response Required",
      content: "Please respond.",
      follow_up_required: true,
      follow_up_date: "2024-01-22",
      status: "sent",
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z",
    });

    render(
      <BrowserRouter>
        <CommunicationLog projectId="test-project-id" />
      </BrowserRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText("Communication Log")).toBeTruthy();
    });

    // Click "Add New Communication" to show the form
    const addButton = screen.getByText("Add New Communication");
    fireEvent.click(addButton);

    // Fill required fields and check response required
    const subjectInput = screen.getByPlaceholderText(
      "Enter communication subject",
    );
    const messageTextarea = screen.getByPlaceholderText(
      "Enter the full message or communication details",
    );
    const contactNameInput = screen.getByPlaceholderText("Contact name");
    const senderInput = screen.getByPlaceholderText(
      "Who sent this communication?",
    );
    const recipientInput = screen.getByPlaceholderText(
      "Who received this communication?",
    );
    const responseRequiredCheckbox = screen.getByLabelText("Response Required");
    const submitButton = screen.getByText("Add Communication");

    fireEvent.change(subjectInput, { target: { value: "Response Required" } });
    fireEvent.change(messageTextarea, { target: { value: "Please respond." } });
    fireEvent.change(contactNameInput, { target: { value: "Manager" } });
    fireEvent.change(senderInput, { target: { value: "Manager" } });
    fireEvent.change(recipientInput, { target: { value: "Team" } });
    fireEvent.click(responseRequiredCheckbox);

    const responseDeadlineInput =
      await screen.findByLabelText("Response Deadline");
    fireEvent.change(responseDeadlineInput, {
      target: { value: "2024-01-22" },
    });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockApiService.createCommunication).toHaveBeenCalledWith(
        expect.objectContaining({
          follow_up_required: true,
          follow_up_date: "2024-01-22",
        }),
      );
    });
  });

  it("displays response deadline warning", async () => {
    const mockCommunications = [
      {
        id: "comm-1",
        project_id: "test-project-id",
        communication_type: "email",
        direction: "outbound",
        contact_name: "Client",
        subject: "Urgent Response Needed",
        content: "Please respond ASAP.",
        follow_up_required: true,
        follow_up_date: "2024-01-16", // Past due
        status: "sent",
        tags: ["urgent"],
        created_at: "2024-01-10T10:00:00Z",
        updated_at: "2024-01-10T10:00:00Z",
      },
    ];

    mockApiService.getProjectCommunications.mockResolvedValue(
      mockCommunications,
    );

    render(
      <BrowserRouter>
        <CommunicationLog projectId="test-project-id" />
      </BrowserRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText("Urgent Response Needed")).toBeTruthy();
    });

    // Should show overdue warning (assuming current date is after 2024-01-16)
    expect(screen.getByText(/Overdue/)).toBeTruthy();
  });

  it("allows editing communication status", async () => {
    const mockCommunication = {
      id: "comm-1",
      project_id: "test-project-id",
      communication_type: "email",
      direction: "outbound",
      contact_name: "Manager",
      subject: "Status Update",
      content: "Status update message.",
      status: "draft",
      created_at: "2024-01-15T10:00:00Z",
      updated_at: "2024-01-15T10:00:00Z",
    };

    mockApiService.getProjectCommunications.mockResolvedValue([
      mockCommunication,
    ]);
    mockApiService.updateCommunication.mockResolvedValue({
      ...mockCommunication,
      status: "sent",
    });

    render(
      <BrowserRouter>
        <CommunicationLog projectId="test-project-id" />
      </BrowserRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText("Status Update")).toBeTruthy();
    });

    // Find and change status
    const statusSelect = screen.getByLabelText("Communication status");
    fireEvent.change(statusSelect, { target: { value: "sent" } });

    await waitFor(() => {
      expect(mockApiService.updateCommunication).toHaveBeenCalledWith(
        "comm-1",
        {
          status: "sent",
        },
      );
    });
  });
});
