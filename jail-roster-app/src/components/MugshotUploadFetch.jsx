import React, { useRef, useState } from "react";

export function MugshotUploadFetch({ recordId, onUploaded }) {
  const fileInputRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const handleClick = () => fileInputRef.current?.click();

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`/api/roster/${recordId}/photo`, {
        method: "POST",
        body: formData,
        credentials: "include",
      });

      const data = await res.json();

      if (!res.ok) throw new Error(data.error || "Upload failed");

      onUploaded?.();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div style={{ display: "inline-flex", flexDirection: "column", gap: 4 }}>
      <button
        onClick={handleClick}
        disabled={uploading}
        style={{
          padding: "4px 8px",
          fontSize: 12,
          borderRadius: 4,
          border: "1px solid #ccc",
          background: uploading ? "#ccc" : "#f5f5f5",
        }}
      >
        {uploading ? "Uploading..." : "Upload Photo"}
      </button>

      <input
        type="file"
        accept="image/*"
        ref={fileInputRef}
        style={{ display: "none" }}
        onChange={handleFileChange}
      />

      {error && <span style={{ color: "red", fontSize: 11 }}>{error}</span>}
    </div>
  );
}
