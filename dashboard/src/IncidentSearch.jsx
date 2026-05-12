import { useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_AUTOOPS_API_URL || "https://autoops-api-126325674316.us-central1.run.app";

export default function IncidentSearch() {
  const [filters, setFilters] = useState({
    service: "",
    owner: "",
    severity: "",
    status: "",
    issue_family: "",
  });
  const [data, setData] = useState(null);
  const [owners, setOwners] = useState(null);
  const [timeline, setTimeline] = useState(null);

  const load = async () => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => {
      if (v) params.set(k, v);
    });

    const res = await fetch(`${API_BASE}/incidents/search?${params.toString()}`);
    setData(await res.json());

    const ownerRes = await fetch(`${API_BASE}/service-owners/dashboard`);
    setOwners(await ownerRes.json());
  };

  const loadTimeline = async (incidentId) => {
    const res = await fetch(`${API_BASE}/incidents/${incidentId}/timeline`);
    setTimeline(await res.json());
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div style={{ padding: "24px", fontFamily: "system-ui" }}>
      <h1>AutoOps Incident Search</h1>
      <p>Search incidents by service, owner, severity, status, and issue family.</p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "8px", marginBottom: "12px" }}>
        {Object.keys(filters).map((key) => (
          <input
            key={key}
            placeholder={key}
            value={filters[key]}
            onChange={(e) => setFilters({ ...filters, [key]: e.target.value })}
            style={{ padding: "8px" }}
          />
        ))}
      </div>

      <button onClick={load} style={{ padding: "8px 12px", marginBottom: "24px" }}>
        Search
      </button>

      <h2>Results ({data?.count || 0})</h2>
      <div style={{ display: "grid", gap: "12px" }}>
        {data?.items?.map((item) => (
          <div key={item.incident_id} style={{ border: "1px solid #ddd", borderRadius: "12px", padding: "16px" }}>
            <b>{item.incident_id}</b> — {item.service} — {item.severity} — {item.status}
            <div>Owner: {item.owner}</div>
            <div>Issue: {item.issue_family}</div>
            <div>Action: {item.action}</div>
            <button onClick={() => loadTimeline(item.incident_id)} style={{ marginTop: "8px" }}>
              View Timeline
            </button>
          </div>
        ))}
      </div>

      <h2>Service Owner Dashboard</h2>
      <pre style={{ background: "#f7f7f7", padding: "12px", borderRadius: "8px" }}>
        {JSON.stringify(owners, null, 2)}
      </pre>

      {timeline && (
        <>
          <h2>Incident Timeline: {timeline.incident_id}</h2>
          <pre style={{ background: "#f7f7f7", padding: "12px", borderRadius: "8px" }}>
            {JSON.stringify(timeline, null, 2)}
          </pre>
        </>
      )}
    </div>
  );
}
