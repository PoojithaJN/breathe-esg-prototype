import { useState } from "react";
import api from "../api/client";
import Navbar from "../components/Navbar";

function Upload() {
  const [sourceType, setSourceType] = useState("SAP");
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleUpload = async (e) => {
    e.preventDefault();
    setError("");
    setResult(null);

    if (!file) {
      setError("Please select a CSV file");
      return;
    }

    const formData = new FormData();
    formData.append("source_type", sourceType);
    formData.append("file", file);

    try {
      const response = await api.post("/uploads/file/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setResult(response.data);
    } catch (err) {
      setError("Upload failed. Check file format and backend server.");
    }
  };

  return (
    <>
      <Navbar />

      <main className="container">
        <h1>Upload Source Data</h1>
        <p>
          Upload SAP, utility, or travel CSV files for ingestion and analyst
          review.
        </p>

        <form className="card" onSubmit={handleUpload}>
          <label>Source Type</label>
          <select
            value={sourceType}
            onChange={(e) => setSourceType(e.target.value)}
          >
            <option value="SAP">SAP Fuel & Procurement</option>
            <option value="UTILITY">Utility Electricity</option>
            <option value="TRAVEL">Corporate Travel</option>
          </select>

          <label>CSV File</label>
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setFile(e.target.files[0])}
          />

          <button type="submit">Upload and Process</button>
        </form>

        {error && <div className="error">{error}</div>}

        {result && (
          <div className="card success">
            <h2>Upload Processed</h2>
            <p>Total rows: {result.total_rows}</p>
            <p>Successful rows: {result.successful_rows}</p>
            <p>Failed rows: {result.failed_rows}</p>
            <p>Suspicious rows: {result.suspicious_rows}</p>
          </div>
        )}
      </main>
    </>
  );
}

export default Upload;