// src/components/UploadButton.jsx
import React, { useRef, useState } from "react";
import { apiAxios } from "../lib/api";

export default function UploadButton({ recordId, onUploaded }) {
  const fileInputRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setError("");
    setUploading(true);

    try {
      const formData = new FormData();
      // IMPORTANT: backend expects key "file"
      formData.append("file", file);

      await apiAxios.post(`/roster/${recordId}/photo`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      if (typeof onUploaded === "function") {
        onUploaded();
      }
    } catch (err) {
      console.error(err);
      const msg =
        err.response?.data?.error ||
        err.message ||
        "Upload failed";
      setError(msg);
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  return (
    <div style={{ display: "inline-flex", flexDirection: "column", gap: 4 }}>
      <button
        type="button"
        onClick={handleClick}
        disabled={uploading}
        style={{
          padding: "4px 8px",
          fontSize: 12,
          borderRadius: 4,
          border: "1px solid #ccc",
          backgroundColor: uploading ? "#ddd" : "#f5f5f5",
          cursor: uploading ? "default" : "pointer",
        }}
      >
        {uploading ? "Uploading…" : "Upload Photo"}
      </button>

      <input
        type="file"
        accept="image/png,image/jpeg"
        ref={fileInputRef}
        style={{ display: "none" }}
        onChange={handleFileChange}
      />

      {error && (
        <span style={{ color: "red", fontSize: 11 }}>
          {error}
        </span>
      )}
    </div>
  );
}
