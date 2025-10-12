import { useState, useCallback } from "react";
import { apiService } from "../services/api";
import type { MediaFile, MediaFileCreate } from "../types/api";

interface MediaUploadProps {
  projectId: string;
  relatedMeetingId?: string;
  relatedCommunicationId?: string;
  relatedComponentId?: string;
  onUpload?: (mediaFile: MediaFile) => void;
  onCancel?: () => void;
  multiple?: boolean;
}

interface FileWithPreview extends File {
  preview?: string;
}

export default function MediaUpload({
  projectId,
  relatedMeetingId,
  relatedCommunicationId,
  relatedComponentId,
  onUpload,
  onCancel,
  multiple = false,
}: MediaUploadProps) {
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>(
    {},
  );
  const [description, setDescription] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [newTag, setNewTag] = useState("");
  const [dragActive, setDragActive] = useState(false);

  const acceptedFileTypes = [
    "image/*",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/plain",
    "text/csv",
  ];

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);

      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        const droppedFiles = Array.from(
          e.dataTransfer.files,
        ) as FileWithPreview[];
        if (multiple) {
          setFiles((prev) => [...prev, ...droppedFiles]);
        } else {
          setFiles([droppedFiles[0]]);
        }

        // Create previews for images
        droppedFiles.forEach((file) => {
          if (file.type.startsWith("image/")) {
            const reader = new FileReader();
            reader.onload = (e) => {
              file.preview = e.target?.result as string;
              setFiles((prev) => [...prev]); // Trigger re-render
            };
            reader.readAsDataURL(file);
          }
        });
      }
    },
    [multiple],
  );

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFiles = Array.from(e.target.files) as FileWithPreview[];
      if (multiple) {
        setFiles((prev) => [...prev, ...selectedFiles]);
      } else {
        setFiles([selectedFiles[0]]);
      }

      // Create previews for images
      selectedFiles.forEach((file) => {
        if (file.type.startsWith("image/")) {
          const reader = new FileReader();
          reader.onload = (e) => {
            file.preview = e.target?.result as string;
            setFiles((prev) => [...prev]); // Trigger re-render
          };
          reader.readAsDataURL(file);
        }
      });
    }
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const addTag = () => {
    if (newTag.trim() && !tags.includes(newTag.trim())) {
      setTags((prev) => [...prev, newTag.trim()]);
      setNewTag("");
    }
  };

  const removeTag = (index: number) => {
    setTags((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      alert("Please select at least one file to upload");
      return;
    }

    setUploading(true);
    const uploadPromises = files.map(async (file) => {
      try {
        // In a real implementation, you would upload the file to a storage service
        // and get back a file path. For now, we'll simulate this.
        const filePath = `uploads/${Date.now()}-${file.name}`;

        const mediaFileData: MediaFileCreate = {
          file_name: file.name,
          file_path: filePath,
          file_type: getFileType(file.type),
          mime_type: file.type,
          file_size: file.size,
          description: description || undefined,
          tags: tags.length > 0 ? tags : undefined,
          related_meeting_id: relatedMeetingId,
          related_communication_id: relatedCommunicationId,
          related_component_id: relatedComponentId,
          project_id: projectId,
        };

        // Simulate upload progress
        setUploadProgress((prev) => ({ ...prev, [file.name]: 0 }));
        for (let progress = 0; progress <= 100; progress += 10) {
          await new Promise((resolve) => setTimeout(resolve, 100));
          setUploadProgress((prev) => ({ ...prev, [file.name]: progress }));
        }

        const uploadedFile = await apiService.createMediaFile(mediaFileData);
        onUpload?.(uploadedFile);
        return uploadedFile;
      } catch (error) {
        console.error(`Failed to upload ${file.name}:`, error);
        throw error;
      }
    });

    try {
      await Promise.all(uploadPromises);
      alert("Files uploaded successfully!");
      // Reset form
      setFiles([]);
      setDescription("");
      setTags([]);
      setUploadProgress({});
    } catch {
      alert("Some files failed to upload. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  const getFileType = (mimeType: string): string => {
    if (mimeType.startsWith("image/")) return "image";
    if (mimeType === "application/pdf") return "document";
    if (mimeType.includes("word") || mimeType.includes("document"))
      return "document";
    if (mimeType.includes("excel") || mimeType.includes("spreadsheet"))
      return "spreadsheet";
    if (mimeType.startsWith("text/")) return "text";
    return "other";
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Upload Media Files</h2>
        <div className="flex space-x-2">
          {onCancel && (
            <button
              onClick={onCancel}
              className="px-4 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50"
              disabled={uploading}
            >
              Cancel
            </button>
          )}
          <button
            onClick={handleUpload}
            disabled={uploading || files.length === 0}
            className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {uploading
              ? "Uploading..."
              : `Upload ${files.length} File${files.length !== 1 ? "s" : ""}`}
          </button>
        </div>
      </div>

      <div className="space-y-6">
        {/* File Drop Zone */}
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragActive
              ? "border-blue-500 bg-blue-50"
              : "border-gray-300 hover:border-gray-400"
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <div className="space-y-4">
            <div className="text-4xl">📁</div>
            <div>
              <p className="text-lg font-medium text-gray-900">
                Drop files here or click to browse
              </p>
              <p className="text-gray-600">
                Supports images, PDFs, documents, spreadsheets, and text files
              </p>
            </div>
            <input
              type="file"
              multiple={multiple}
              accept={acceptedFileTypes.join(",")}
              onChange={handleFileSelect}
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className="inline-block px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 cursor-pointer"
            >
              Choose Files
            </label>
          </div>
        </div>

        {/* File List */}
        {files.length > 0 && (
          <div className="space-y-3">
            <h3 className="text-lg font-medium text-gray-900">
              Selected Files
            </h3>
            <div className="space-y-2">
              {files.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center space-x-3 p-3 bg-gray-50 rounded"
                >
                  {file.preview ? (
                    <img
                      src={file.preview}
                      alt={file.name}
                      className="w-12 h-12 object-cover rounded"
                    />
                  ) : (
                    <div className="w-12 h-12 bg-gray-200 rounded flex items-center justify-center">
                      📄
                    </div>
                  )}
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">{file.name}</div>
                    <div className="text-sm text-gray-600">
                      {formatFileSize(file.size)} • {file.type}
                    </div>
                    {uploadProgress[file.name] !== undefined && (
                      <div className="mt-1">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${uploadProgress[file.name]}%` }}
                          ></div>
                        </div>
                        <div className="text-xs text-gray-600 mt-1">
                          {uploadProgress[file.name]}% uploaded
                        </div>
                      </div>
                    )}
                  </div>
                  <button
                    onClick={() => removeFile(index)}
                    className="text-red-600 hover:text-red-800"
                    disabled={uploading}
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description (Optional)
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Add a description for these files..."
          />
        </div>

        {/* Tags */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tags (Optional)
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
            {tags.map((tag, index) => (
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

        {/* Related Items Info */}
        {(relatedMeetingId || relatedCommunicationId || relatedComponentId) && (
          <div className="bg-blue-50 p-4 rounded">
            <h4 className="font-medium text-blue-900 mb-2">Related Items</h4>
            <div className="text-sm text-blue-800 space-y-1">
              {relatedMeetingId && <div>Meeting: {relatedMeetingId}</div>}
              {relatedCommunicationId && (
                <div>Communication: {relatedCommunicationId}</div>
              )}
              {relatedComponentId && <div>Component: {relatedComponentId}</div>}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
