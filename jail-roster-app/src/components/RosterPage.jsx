// src/components/RosterPage.jsx
import React, { useEffect, useState } from "react";
import { apiFetchJson } from "../lib/api";
import RosterRow from "./RosterRow";

export default function RosterPage() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadRoster = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await apiFetchJson("/api/roster", {
        method: "GET",
      });

      // Handle either [] or {items: []}
      const list = Array.isArray(data) ? data : data.items || [];
      setRecords(list);
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to load roster");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRoster();
  }, []);

  return (
    <div style={{ padding: 16 }}>
      <h2>Jail Roster</h2>

      {loading && <p>Loading…</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {!loading && !error && (
        <table
          style={{
            borderCollapse: "collapse",
            width: "100%",
            marginTop: 12,
          }}
        >
          <thead>
            <tr>
              <th style={{ textAlign: "left", padding: 8 }}>Photo</th>
              <th style={{ textAlign: "left", padding: 8 }}>Name</th>
              <th style={{ textAlign: "left", padding: 8 }}>DOB</th>
              <th style={{ textAlign: "left", padding: 8 }}>OCA #</th>
              <th style={{ textAlign: "left", padding: 8 }}>Charges</th>
            </tr>
          </thead>
          <tbody>
            {records.map((rec) => (
              <RosterRow
                key={rec.id}
                record={rec}
                onReload={loadRoster}
              />
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
