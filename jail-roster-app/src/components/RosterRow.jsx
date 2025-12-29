// src/components/RosterRow.jsx
import React from "react";
import UploadButton from "./UploadButton";

export default function RosterRow({ record, onReload }) {
  const photoUrl = record.photoUrl || `/api/roster/${record.id}/photo`;

  return (
    <tr>
      {/* PHOTO CELL */}
      <td style={{ padding: "8px" }}>
        {record.photoFilename || record.photoUrl ? (
          <img
            src={photoUrl}
            alt={record.name}
            style={{
              width: 48,
              height: 48,
              borderRadius: 4,
              objectFit: "cover",
              display: "block",
            }}
          />
        ) : (
          <div
            style={{
              width: 48,
              height: 48,
              borderRadius: 4,
              background: "#eee",
            }}
          />
        )}

        <div style={{ marginTop: 4 }}>
          <UploadButton recordId={record.id} onUploaded={onReload} />
        </div>
      </td>

      {/* BASIC FIELDS — tweak to match your data */}
      <td style={{ padding: "8px" }}>{record.name}</td>
      <td style={{ padding: "8px" }}>{record.dob}</td>
      <td style={{ padding: "8px" }}>{record.ocaNumber}</td>
      <td style={{ padding: "8px" }}>{record.charges}</td>
    </tr>
  );
}
