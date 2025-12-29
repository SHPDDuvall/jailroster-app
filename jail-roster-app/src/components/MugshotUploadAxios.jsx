import { MugshotUploadFetch } from "../components/MugshotUploadFetch";
// OR axios version:
// import { MugshotUploadAxios } from "../components/MugshotUploadAxios";

function RosterRow({ record, onReload }) {
  return (
    <tr>
      <td>
        {record.photoUrl ? (
          <img
            src={record.photoUrl}
            alt={record.name}
            style={{
              width: 48,
              height: 48,
              borderRadius: 4,
              objectFit: "cover",
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

        {/* Upload button */}
        <MugshotUploadFetch recordId={record.id} onUploaded={onReload} />
      </td>

      {/* ...the rest of your row */}
    </tr>
  );
}
