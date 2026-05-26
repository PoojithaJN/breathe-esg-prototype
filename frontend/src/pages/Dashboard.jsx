import { useEffect, useState } from "react";
import api from "../api/client";
import Navbar from "../components/Navbar";

function Dashboard() {
  const [summary, setSummary] = useState(null);

  const fetchSummary = async () => {
    try {
      const response = await api.get("/dashboard/summary/");
      setSummary(response.data);
    } catch (error) {
      console.error("Failed to fetch dashboard summary", error);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  if (!summary) {
    return (
      <>
        <Navbar />
        <main className="container">
          <p>Loading dashboard...</p>
        </main>
      </>
    );
  }

  return (
    <>
      <Navbar />

      <main className="container">
        <h1>Analyst Dashboard</h1>
        <p>
          Overview of uploaded, suspicious, approved, and locked ESG activity
          data.
        </p>

        <div className="grid">
          <div className="card">
            <h3>Total Rows</h3>
            <h2>{summary.total}</h2>
          </div>

          <div className="card">
            <h3>Needs Review</h3>
            <h2>{summary.needs_review}</h2>
          </div>

          <div className="card">
            <h3>Suspicious</h3>
            <h2>{summary.suspicious}</h2>
          </div>

          <div className="card">
            <h3>Approved</h3>
            <h2>{summary.approved}</h2>
          </div>

          <div className="card">
            <h3>Rejected</h3>
            <h2>{summary.rejected}</h2>
          </div>

          <div className="card">
            <h3>Locked</h3>
            <h2>{summary.locked}</h2>
          </div>
        </div>

        <h2>Source Breakdown</h2>

        <div className="grid">
          <div className="card">
            <h3>SAP</h3>
            <h2>{summary.sap}</h2>
          </div>

          <div className="card">
            <h3>Utility</h3>
            <h2>{summary.utility}</h2>
          </div>

          <div className="card">
            <h3>Travel</h3>
            <h2>{summary.travel}</h2>
          </div>
        </div>
      </main>
    </>
  );
}

export default Dashboard;