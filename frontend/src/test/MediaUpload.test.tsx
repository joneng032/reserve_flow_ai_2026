import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { vi, describe, it, expect, beforeEach } from "vitest";
import * as matchers from "@testing-library/jest-dom/matchers";
import MediaUpload from "../components/MediaUpload";

// Extend expect with jest-dom matchers
expect.extend(matchers);

// Mock the API service
vi.mock("../services/api", () => ({
  apiService: {
    createMediaFile: vi.fn(),
  },
}));

import { apiService } from "../services/api";

describe("MediaUpload", () => {
  const mockApiService = vi.mocked(apiService);
  const mockProjectId = "test-project-123";
  const mockOnUpload = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockOnUpload.mockClear();
  });

  it("renders upload area correctly", () => {
    render(<MediaUpload projectId={mockProjectId} onUpload={mockOnUpload} />);

    expect(screen.getByText("Upload Media Files")).toBeTruthy();
    expect(screen.getByText("Drop files here or click to browse")).toBeTruthy();
    expect(
      screen.getByText(
        "Supports images, PDFs, documents, spreadsheets, and text files",
      ),
    ).toBeTruthy();
    expect(
      screen.getByRole("button", { name: /upload 0 files/i }),
    ).toBeTruthy();
    expect(
      screen.getByPlaceholderText("Add a description for these files..."),
    ).toBeTruthy();
    expect(screen.getByLabelText("Add tag")).toBeTruthy();
  });

  it("handles file selection via click", async () => {
    const mockFile = new File(["test content".repeat(100)], "test.pdf", {
      type: "application/pdf",
    });
    const mockUploadResponse = {
      id: "uploaded-file-1",
      file_name: "test.pdf",
      file_path: "uploads/123-test.pdf",
      file_type: "document",
      mime_type: "application/pdf",
      file_size: 1200,
      project_id: mockProjectId,
      uploaded_at: "2024-01-15T10:30:00Z",
    };

    mockApiService.createMediaFile.mockResolvedValue(mockUploadResponse);

    // Mock window.alert
    const alertMock = vi.spyOn(window, "alert").mockImplementation(() => {});

    render(<MediaUpload projectId={mockProjectId} onUpload={mockOnUpload} />);

    // Find the file input by its id
    const fileInput = document.getElementById(
      "file-upload",
    ) as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [mockFile] } });

    // File should appear in the selected files list
    expect(screen.getByText("test.pdf")).toBeTruthy();
    expect(screen.getByText("1.17 KB • application/pdf")).toBeTruthy();

    // Click upload button
    const uploadButton = screen.getByRole("button", { name: /upload 1 file/i });
    fireEvent.click(uploadButton);

    // Should show uploading state
    await waitFor(() => {
      expect(screen.getByText("Uploading...")).toBeTruthy();
    });

    alertMock.mockRestore();
  });

  it("handles drag and drop file upload", async () => {
    const mockFile = new File(["test content".repeat(100)], "test.jpg", {
      type: "image/jpeg",
    });
    const mockUploadResponse = {
      id: "uploaded-file-2",
      file_name: "test.jpg",
      file_path: "uploads/123-test.jpg",
      file_type: "image",
      mime_type: "image/jpeg",
      file_size: 1200,
      project_id: mockProjectId,
      uploaded_at: "2024-01-15T10:30:00Z",
    };

    mockApiService.createMediaFile.mockResolvedValue(mockUploadResponse);

    // Mock window.alert
    const alertMock = vi.spyOn(window, "alert").mockImplementation(() => {});

    render(<MediaUpload projectId={mockProjectId} onUpload={mockOnUpload} />);

    const dropZone = screen
      .getByText("Drop files here or click to browse")
      .closest("div");

    // Simulate drag over
    fireEvent.dragOver(dropZone!);
    // Just check that drag over doesn't break anything

    // Simulate drop
    fireEvent.drop(dropZone!, {
      dataTransfer: {
        files: [mockFile],
      },
    });

    // File should appear in the selected files list
    expect(screen.getByText("test.jpg")).toBeTruthy();

    // Click upload button
    const uploadButton = screen.getByRole("button", { name: /upload 1 file/i });
    fireEvent.click(uploadButton);

    // Should show uploading state
    await waitFor(() => {
      expect(screen.getByText("Uploading...")).toBeTruthy();
    });

    alertMock.mockRestore();
  });

  it("shows upload progress", async () => {
    const mockFile = new File(["test content".repeat(100)], "large-file.zip", {
      type: "application/zip",
    });

    // Mock window.alert
    const alertMock = vi.spyOn(window, "alert").mockImplementation(() => {});

    render(<MediaUpload projectId={mockProjectId} onUpload={mockOnUpload} />);

    const fileInput = document.getElementById(
      "file-upload",
    ) as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [mockFile] } });

    // Click upload button
    const uploadButton = screen.getByRole("button", { name: /upload 1 file/i });
    fireEvent.click(uploadButton);

    // Should show uploading state and progress
    expect(screen.getByText("Uploading...")).toBeTruthy();
    expect(screen.getByText("large-file.zip")).toBeTruthy();

    alertMock.mockRestore();
  });

  it("handles upload errors gracefully", async () => {
    const mockFile = new File(["test content"], "error-file.jpg", {
      type: "image/jpeg",
    });
    const errorMessage = "Upload failed: Network error";

    mockApiService.createMediaFile.mockRejectedValue(new Error(errorMessage));

    // Mock window.alert
    const alertMock = vi.spyOn(window, "alert").mockImplementation(() => {});

    render(<MediaUpload projectId={mockProjectId} onUpload={mockOnUpload} />);

    const fileInput = document.getElementById(
      "file-upload",
    ) as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [mockFile] } });

    const uploadButton = screen.getByRole("button", { name: /upload 1 file/i });
    fireEvent.click(uploadButton);

    await waitFor(
      () => {
        expect(alertMock).toHaveBeenCalledWith(
          "Some files failed to upload. Please try again.",
        );
      },
      { timeout: 5000 },
    );

    alertMock.mockRestore();
  });

  it("allows removing selected files", () => {
    const mockFile = new File(["test content"], "test.pdf", {
      type: "application/pdf",
    });

    render(<MediaUpload projectId={mockProjectId} onUpload={mockOnUpload} />);

    const fileInput = document.getElementById(
      "file-upload",
    ) as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [mockFile] } });

    // File should appear
    expect(screen.getByText("test.pdf")).toBeTruthy();

    // Click remove button
    const removeButton = screen.getByRole("button", { name: /remove/i });
    fireEvent.click(removeButton);

    // File should be removed
    expect(screen.queryByText("test.pdf")).toBeNull();
  });

  it("handles tags functionality", () => {
    render(<MediaUpload projectId={mockProjectId} onUpload={mockOnUpload} />);

    const tagInput = screen.getByLabelText("Add tag");
    const addButton = screen.getByRole("button", { name: /add/i });

    // Add a tag
    fireEvent.change(tagInput, { target: { value: "important" } });
    fireEvent.click(addButton);

    expect(screen.getByText("important")).toBeTruthy();

    // Try to add duplicate tag (should not work)
    fireEvent.change(tagInput, { target: { value: "important" } });
    fireEvent.click(addButton);

    // Should still only have one tag
    expect(screen.getAllByText("important")).toHaveLength(1);
  });

  it("shows related items info when provided", () => {
    render(
      <MediaUpload
        projectId={mockProjectId}
        relatedMeetingId="meeting-123"
        relatedCommunicationId="comm-456"
        onUpload={mockOnUpload}
      />,
    );

    expect(screen.getByText("Related Items")).toBeTruthy();
    expect(screen.getByText("Meeting: meeting-123")).toBeTruthy();
    expect(screen.getByText("Communication: comm-456")).toBeTruthy();
  });
});
