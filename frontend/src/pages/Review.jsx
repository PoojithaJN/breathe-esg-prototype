import { useEffect, useState } from "react";
import api from "../api/client";
import Navbar from "../components/Navbar";

function Review() {
  const [records, setRecords] = useState([]);
  const [selected, setSelected] = useState(null);
  const [source, setSource] = useState("");
  const [status, setStatus] = useState("");

  const fetchRecords = async () => {
    try {
      const params = new URLSearchParams();

      if (source) params.append("source", source);
      if (status) params.append("status", status);

      const response = await api.get(`/activities/?${params.toString()}`);
      setRecords(response.data);
    } catch (error) {
      console.error("Failed to fetch records", error);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, [source, status]);

  const approve = async (id) => {
    await api.post(`/activities/${id}/approve/`);
    fetchRecords();
  };

  const reject = async (id) => {
    await api.post(`/activities/${id}/reject/`);
    fetchRecords();
  };

  const lock = async (id) => {
    await api.post(`/activities/${id}/lock/`);
    fetchRecords();
  };

  return (
    <>
      <Navbar />

      <main className="container">
        <h1>Review Dashboard</h1>
        <p>
          Review normalized ESG activity rows before they are locked for audit.
        </p>

        <div className="filters">
          <select value={source} onChange={(e) => setSource(e.target.value)}>
            <option value="">All Sources</option>
            <option value="SAP">SAP</option>
            <option value="UTILITY">Utility</option>
            <option value="TRAVEL">Travel</option>
          </select>

          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="">All Status</option>
            <option value="NEEDS_REVIEW">Needs Review</option>
            <option value="APPROVED">Approved</option>
            <option value="REJECTED">Rejected</option>
            <option value="LOCKED">Locked</option>
          </select>
        </div>

        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Source</th>
              <th>Scope</th>
              <th>Category</th>
              <th>Quantity</th>
              <th>Unit</th>
              <th>Status</th>
              <th>Flags</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            {records.map((record) => (
              <tr key={record.id}>
                <td>{record.id}</td>
                <td>{record.source_type}</td>
                <td>{record.scope}</td>
                <td>{record.category}</td>
                <td>{record.normalized_quantity || "-"}</td>
                <td>{record.normalized_unit || "-"}</td>
                <td>
                  <span className={`badge ${record.validation_status.toLowerCase()}`}>
                    {record.validation_status}
                  </span>
                </td>
                <td>
                  {record.suspicious_flags && record.suspicious_flags.length > 0
                    ? record.suspicious_flags.join(", ")
                    : "None"}
                </td>
                <td>
                  <button onClick={() => setSelected(record)}>View</button>
                  <button disabled={record.is_locked} onClick={() => approve(record.id)}>
                    Approve
                  </button>
                  <button disabled={record.is_locked} onClick={() => reject(record.id)}>
                    Reject
                  </button>
                  <button
                    disabled={record.validation_status !== "APPROVED"}
                    onClick={() => lock(record.id)}
                  >
                    Lock
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {selected && (
          <div className="modal-backdrop">
            <div className="modal">
              <button className="close" onClick={() => setSelected(null)}>
                X
              </button>

              <h2>Record Detail</h2>

              <h3>Raw Source Row</h3>
              <pre>{JSON.stringify(selected.raw_payload, null, 2)}</pre>

              <h3>Normalized Row</h3>
              <pre>
                {JSON.stringify(
                  {
                    source: selected.source_type,
                    scope: selected.scope,
                    category: selected.category,
                    quantity: selected.normalized_quantity,
                    unit: selected.normalized_unit,
                    status: selected.validation_status,
                    flags: selected.suspicious_flags,
                  },
                  null,
                  2
                )}
              </pre>

              <h3>Audit Logs</h3>
              {selected.audit_logs && selected.audit_logs.length > 0 ? (
                selected.audit_logs.map((log) => (
                  <div key={log.id} className="audit-item">
                    <b>{log.action}</b> by {log.performed_by_name || "system"}
                  </div>
                ))
              ) : (
                <p>No audit logs</p>
              )}
            </div>
          </div>
        )}
      </main>
    </>
  );
}

export default Review;