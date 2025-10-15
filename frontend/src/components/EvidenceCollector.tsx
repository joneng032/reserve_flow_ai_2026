import { useState, useEffect, useCallback } from "react";
import { apiService } from "../services/api";
import type { Evidence, EvidenceCreate } from "../types/api";

interface EvidenceCollectorProps {
  projectId: string;
  relatedInspectionId?: string;
  relatedInspectionItemId?: string;
  relatedComponentId?: string;
  onSave?: (evidence: Evidence) => void;
  onCancel?: () => void;
}

interface GPSCoordinates {
  latitude: number;
  longitude: number;
  altitude?: number;
  accuracy?: number;
  heading?: number;
  speed?: number;
  timestamp: string;
}

interface NewEvidence {
  evidence_type: string;
  file_name: string;
  mime_type: string;
  measurement_value?: number;
  measurement_unit: string;
  notes: string;
  tags: string[];
}

export default function EvidenceCollector({
  projectId,
  relatedInspectionId,
  relatedInspectionItemId,
  relatedComponentId,
  onSave,
  onCancel,
}: EvidenceCollectorProps) {
  const [evidenceList, setEvidenceList] = useState<Evidence[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [gpsEnabled, setGpsEnabled] = useState(false);
  const [gpsCoordinates, setGpsCoordinates] = useState<GPSCoordinates | null>(
    null,
  );
  const [gpsError, setGpsError] = useState<string>("");
  const [newEvidence, setNewEvidence] = useState<NewEvidence>({
    evidence_type: "photo",
    file_name: "",
    mime_type: "",
    measurement_value: undefined,
    measurement_unit: "feet",
    notes: "",
    tags: [],
  });
  const [newTag, setNewTag] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>("");

  const loadEvidence = useCallback(async () => {
    try {
      setLoading(true);
      const evidence = await apiService.getProjectEvidence(projectId, {
        skip: 0,
        limit: 100,
      });

      // Filter by related entities if provided
      let filteredEvidence = evidence;
      if (relatedInspectionId) {
        filteredEvidence = filteredEvidence.filter(
          (e) => e.related_inspection_id === relatedInspectionId,
        );
      }
      if (relatedInspectionItemId) {
        filteredEvidence = filteredEvidence.filter(
          (e) => e.related_inspection_item_id === relatedInspectionItemId,
        );
      }
      if (relatedComponentId) {
        filteredEvidence = filteredEvidence.filter(
          (e) => e.related_component_id === relatedComponentId,
        );
      }

      setEvidenceList(filteredEvidence);
    } catch (error) {
      console.error("Failed to load evidence:", error);
      alert("Failed to load evidence");
    } finally {
      setLoading(false);
    }
  }, [
    projectId,
    relatedInspectionId,
    relatedInspectionItemId,
    relatedComponentId,
  ]);

  useEffect(() => {
    loadEvidence();
  }, [loadEvidence]);

  const requestGPSLocation = () => {
    if (!navigator.geolocation) {
      setGpsError("Geolocation is not supported by your browser");
      return;
    }

    setGpsEnabled(true);
    setGpsError("");

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const coords: GPSCoordinates = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          altitude: position.coords.altitude || undefined,
          accuracy: position.coords.accuracy,
          heading: position.coords.heading || undefined,
          speed: position.coords.speed || undefined,
          timestamp: new Date().toISOString(),
        };
        setGpsCoordinates(coords);
        setGpsError("");
      },
      (error) => {
        setGpsError(`GPS Error: ${error.message}`);
        setGpsEnabled(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      },
    );
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setSelectedFile(file);
    setNewEvidence((prev) => ({
      ...prev,
      file_name: file.name,
      mime_type: file.type,
    }));

    // Create preview for images and videos
    if (file.type.startsWith("image/") || file.type.startsWith("video/")) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    }
  };

  const capturePhoto = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });

      // Create video element to capture frame
      const video = document.createElement("video");
      video.srcObject = stream;
      video.play();

      // Wait for video to load
      await new Promise((resolve) => {
        video.onloadedmetadata = resolve;
      });

      // Create canvas and capture frame
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext("2d");
      ctx?.drawImage(video, 0, 0);

      // Stop video stream
      stream.getTracks().forEach((track) => track.stop());

      // Convert canvas to blob
      canvas.toBlob(
        (blob) => {
          if (blob) {
            const file = new File([blob], `photo_${Date.now()}.jpg`, {
              type: "image/jpeg",
            });
            setSelectedFile(file);
            setNewEvidence((prev) => ({
              ...prev,
              file_name: file.name,
              mime_type: file.type,
              evidence_type: "photo",
            }));
            setPreviewUrl(URL.createObjectURL(blob));
          }
        },
        "image/jpeg",
        0.95,
      );
    } catch (error) {
      console.error("Failed to capture photo:", error);
      alert("Failed to access camera. Please check permissions.");
    }
  };

  const addTag = () => {
    if (newTag.trim() && !newEvidence.tags.includes(newTag.trim())) {
      setNewEvidence((prev) => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()],
      }));
      setNewTag("");
    }
  };

  const removeTag = (tagToRemove: string) => {
    setNewEvidence((prev) => ({
      ...prev,
      tags: prev.tags.filter((tag) => tag !== tagToRemove),
    }));
  };

  const handleSaveEvidence = async () => {
    if (!selectedFile) {
      alert("Please select or capture a file");
      return;
    }

    try {
      setSaving(true);

      // In a real implementation, you would upload the file to storage first
      // For now, we'll simulate with a placeholder path
      const filePath = `/uploads/${projectId}/${selectedFile.name}`;

      const evidenceData: EvidenceCreate = {
        evidence_type: newEvidence.evidence_type,
        file_name: newEvidence.file_name,
        file_path: filePath,
        mime_type: newEvidence.mime_type,
        file_size: selectedFile.size,
        latitude: gpsCoordinates?.latitude,
        longitude: gpsCoordinates?.longitude,
        altitude: gpsCoordinates?.altitude,
        accuracy: gpsCoordinates?.accuracy,
        heading: gpsCoordinates?.heading,
        speed: gpsCoordinates?.speed,
        timestamp: gpsCoordinates?.timestamp || new Date().toISOString(),
        measurement_value: newEvidence.measurement_value,
        measurement_unit: newEvidence.measurement_unit || undefined,
        notes: newEvidence.notes || undefined,
        tags: newEvidence.tags.length > 0 ? newEvidence.tags : undefined,
        related_inspection_id: relatedInspectionId,
        related_inspection_item_id: relatedInspectionItemId,
        related_component_id: relatedComponentId,
        device_info: {
          userAgent: navigator.userAgent,
          platform: navigator.platform,
          language: navigator.language,
        },
        metadata: {
          capturedAt: new Date().toISOString(),
          fileType: selectedFile.type,
          fileSize: selectedFile.size,
        },
        project_id: projectId,
      };

      const savedEvidence = await apiService.createEvidence(evidenceData);
      setEvidenceList((prev) => [savedEvidence, ...prev]);

      // Reset form
      setNewEvidence({
        evidence_type: "photo",
        file_name: "",
        mime_type: "",
        measurement_value: undefined,
        measurement_unit: "feet",
        notes: "",
        tags: [],
      });
      setSelectedFile(null);
      setPreviewUrl("");
      setGpsCoordinates(null);

      onSave?.(savedEvidence);
      alert("Evidence saved successfully!");
    } catch (error) {
      console.error("Failed to save evidence:", error);
      alert("Failed to save evidence");
    } finally {
      setSaving(false);
    }
  };

  const deleteEvidence = async (evidenceId: string) => {
    if (!confirm("Are you sure you want to delete this evidence?")) return;

    try {
      await apiService.deleteEvidence(evidenceId);
      setEvidenceList((prev) => prev.filter((e) => e.id !== evidenceId));
    } catch (error) {
      console.error("Failed to delete evidence:", error);
      alert("Failed to delete evidence");
    }
  };

  const getEvidenceTypeColor = (type: string) => {
    switch (type) {
      case "photo":
        return "bg-blue-100 text-blue-800";
      case "video":
        return "bg-purple-100 text-purple-800";
      case "audio":
        return "bg-green-100 text-green-800";
      case "document":
        return "bg-yellow-100 text-yellow-800";
      case "measurement":
        return "bg-orange-100 text-orange-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return "0 KB";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatCoordinates = (lat?: number, lon?: number) => {
    if (!lat || !lon) return "No GPS data";
    return `${lat.toFixed(6)}, ${lon.toFixed(6)}`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="loading-spinner-lg mx-auto"></div>
        <span className="ml-2">Loading evidence...</span>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Evidence Collector</h2>
        <div className="flex space-x-2">
          {onCancel && (
            <button
              onClick={onCancel}
              className="px-4 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50"
              disabled={saving}
            >
              Close
            </button>
          )}
        </div>
      </div>

      <div className="space-y-6">
        {/* Evidence Capture Section */}
        <div className="bg-gray-50 p-6 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Capture New Evidence
          </h3>

          {/* Evidence Type Selection */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Evidence Type *
            </label>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
              {["photo", "video", "audio", "document", "measurement"].map(
                (type) => (
                  <button
                    key={type}
                    onClick={() =>
                      setNewEvidence((prev) => ({
                        ...prev,
                        evidence_type: type,
                      }))
                    }
                    className={`px-4 py-2 rounded capitalize ${
                      newEvidence.evidence_type === type
                        ? "bg-blue-600 text-white"
                        : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
                    }`}
                  >
                    {type}
                  </button>
                ),
              )}
            </div>
          </div>

          {/* GPS Controls */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-gray-700">
                GPS Location
              </label>
              <button
                onClick={requestGPSLocation}
                className={`px-3 py-1 rounded text-sm ${
                  gpsEnabled
                    ? "bg-green-600 text-white"
                    : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                }`}
              >
                {gpsEnabled ? "✓ GPS Active" : "Enable GPS"}
              </button>
            </div>

            {gpsCoordinates && (
              <div className="bg-green-50 border border-green-200 rounded p-3 text-sm">
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <span className="font-medium">Coordinates:</span>{" "}
                    {formatCoordinates(
                      gpsCoordinates.latitude,
                      gpsCoordinates.longitude,
                    )}
                  </div>
                  <div>
                    <span className="font-medium">Accuracy:</span> ±
                    {gpsCoordinates.accuracy?.toFixed(1)}m
                  </div>
                  {gpsCoordinates.altitude && (
                    <div>
                      <span className="font-medium">Altitude:</span>{" "}
                      {gpsCoordinates.altitude.toFixed(1)}m
                    </div>
                  )}
                  {gpsCoordinates.heading && (
                    <div>
                      <span className="font-medium">Heading:</span>{" "}
                      {gpsCoordinates.heading.toFixed(0)}°
                    </div>
                  )}
                </div>
              </div>
            )}

            {gpsError && (
              <div className="bg-red-50 border border-red-200 rounded p-3 text-sm text-red-700">
                {gpsError}
              </div>
            )}
          </div>

          {/* File Capture/Upload */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              File Capture/Upload *
            </label>
            <div className="flex flex-wrap gap-2 mb-3">
              {newEvidence.evidence_type === "photo" && (
                <button
                  onClick={capturePhoto}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  📷 Capture Photo
                </button>
              )}
              <label className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 cursor-pointer">
                📁 Browse Files
                <input
                  type="file"
                  onChange={handleFileSelect}
                  accept={
                    newEvidence.evidence_type === "photo"
                      ? "image/*"
                      : newEvidence.evidence_type === "video"
                      ? "video/*"
                      : newEvidence.evidence_type === "audio"
                      ? "audio/*"
                      : newEvidence.evidence_type === "document"
                      ? ".pdf,.doc,.docx,.txt"
                      : "*/*"
                  }
                  className="hidden"
                  aria-label="Upload file"
                />
              </label>
            </div>

            {selectedFile && (
              <div className="bg-white border border-gray-200 rounded p-3">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <div className="font-medium text-gray-900">
                      {selectedFile.name}
                    </div>
                    <div className="text-sm text-gray-500">
                      {formatFileSize(selectedFile.size)} • {selectedFile.type}
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setSelectedFile(null);
                      setPreviewUrl("");
                    }}
                    className="text-red-600 hover:text-red-800"
                  >
                    Remove
                  </button>
                </div>

                {/* Preview */}
                {previewUrl && (
                  <div className="mt-3">
                    {selectedFile.type.startsWith("image/") && (
                      <img
                        src={previewUrl}
                        alt="Preview"
                        className="max-w-full max-h-64 rounded"
                      />
                    )}
                    {selectedFile.type.startsWith("video/") && (
                      <video
                        src={previewUrl}
                        controls
                        className="max-w-full max-h-64 rounded"
                      />
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Measurement */}
          {newEvidence.evidence_type === "measurement" && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Measurement Value
                </label>
                <input
                  type="number"
                  value={newEvidence.measurement_value || ""}
                  onChange={(e) =>
                    setNewEvidence((prev) => ({
                      ...prev,
                      measurement_value: e.target.value
                        ? parseFloat(e.target.value)
                        : undefined,
                    }))
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter measurement"
                  step="0.01"
                  aria-label="Measurement value"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Unit
                </label>
                <select
                  value={newEvidence.measurement_unit}
                  onChange={(e) =>
                    setNewEvidence((prev) => ({
                      ...prev,
                      measurement_unit: e.target.value,
                    }))
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  aria-label="Measurement unit"
                >
                  <option value="feet">Feet</option>
                  <option value="inches">Inches</option>
                  <option value="meters">Meters</option>
                  <option value="centimeters">Centimeters</option>
                  <option value="square_feet">Square Feet</option>
                  <option value="square_meters">Square Meters</option>
                  <option value="degrees">Degrees</option>
                  <option value="percent">Percent</option>
                </select>
              </div>
            </div>
          )}

          {/* Notes */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Notes
            </label>
            <textarea
              value={newEvidence.notes}
              onChange={(e) =>
                setNewEvidence((prev) => ({ ...prev, notes: e.target.value }))
              }
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Add notes about this evidence..."
            />
          </div>

          {/* Tags */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tags
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onKeyPress={(e) =>
                  e.key === "Enter" && (e.preventDefault(), addTag())
                }
                className="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Add tag..."
                aria-label="New tag"
              />
              <button
                onClick={addTag}
                className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
              >
                Add Tag
              </button>
            </div>
            {newEvidence.tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {newEvidence.tags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                  >
                    {tag}
                    <button
                      onClick={() => removeTag(tag)}
                      className="ml-2 text-blue-600 hover:text-blue-800"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Save Button */}
          <div className="flex justify-end">
            <button
              onClick={handleSaveEvidence}
              disabled={saving || !selectedFile}
              className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {saving ? "Saving..." : "Save Evidence"}
            </button>
          </div>
        </div>

        {/* Evidence List */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Collected Evidence ({evidenceList.length})
          </h3>

          {evidenceList.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No evidence collected yet. Start by capturing or uploading
              evidence above.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {evidenceList.map((evidence) => (
                <div
                  key={evidence.id}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex justify-between items-start mb-2">
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${getEvidenceTypeColor(
                        evidence.evidence_type,
                      )}`}
                    >
                      {evidence.evidence_type}
                    </span>
                    <button
                      onClick={() => deleteEvidence(evidence.id)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Delete
                    </button>
                  </div>

                  <div className="mb-2">
                    <div className="font-medium text-gray-900 truncate">
                      {evidence.file_name}
                    </div>
                    <div className="text-xs text-gray-500">
                      {formatFileSize(evidence.file_size)} •{" "}
                      {evidence.mime_type}
                    </div>
                  </div>

                  {evidence.notes && (
                    <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                      {evidence.notes}
                    </p>
                  )}

                  {evidence.latitude && evidence.longitude && (
                    <div className="text-xs text-gray-500 mb-2">
                      📍{" "}
                      {formatCoordinates(evidence.latitude, evidence.longitude)}
                      {evidence.accuracy &&
                        ` (±${evidence.accuracy.toFixed(0)}m)`}
                    </div>
                  )}

                  {evidence.measurement_value && (
                    <div className="text-sm text-gray-700 mb-2">
                      📏 {evidence.measurement_value}{" "}
                      {evidence.measurement_unit}
                    </div>
                  )}

                  {evidence.tags && evidence.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-2">
                      {evidence.tags.map((tag) => (
                        <span
                          key={tag}
                          className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded text-xs"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}

                  <div className="text-xs text-gray-400">
                    {new Date(evidence.created_at || "").toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
