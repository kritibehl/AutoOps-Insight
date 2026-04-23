import { useEffect, useMemo, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
} from "recharts";
import "./index.css";

const API_BASE = "http://127.0.0.1:8001";

function MetricCard({ title, value, subtitle }) {
  return (
    <div className="card metric-card">
      <div className="metric-title">{title}</div>
      <div className="metric-value">{value}</div>
      {subtitle ? <div className="metric-subtitle">{subtitle}</div> : null}
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div className="card section-card">
      <div className="section-title">{title}</div>
      {children}
    </div>
  );
}

export default function App() {
  const [metrics, setMetrics] = useState(null);
  const [summary, setSummary] = useState(null);
  const [incidents, setIncidents] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const [metricsRes, summaryRes, incidentsRes] = await Promise.all([
          fetch(`${API_BASE}/metrics`),
          fetch(`${API_BASE}/dashboard/summary`),
          fetch(`${API_BASE}/incidents`),
        ]);

        if (!metricsRes.ok || !summaryRes.ok || !incidentsRes.ok) {
          throw new Error("Failed to fetch dashboard data");
        }

        const metricsJson = await metricsRes.json();
        const summaryJson = await summaryRes.json();
        const incidentsJson = await incidentsRes.json();

        setMetrics(metricsJson);
        setSummary(summaryJson);
        setIncidents(incidentsJson.items || []);
      } catch (e) {
        setError(e.message || "Unknown error");
      }
    }

    load();
  }, []);

  const actionData = useMemo(() => {
    if (!summary?.action_summary) return [];
    return Object.entries(summary.action_summary).map(([name, value]) => ({
      name,
      value,
    }));
  }, [summary]);

  const topFailureData = summary?.top_failures || [];
  const rows = incidents || [];

  return (
    <div className="page">
      <div className="hero">
        <div>
          <div className="eyebrow">AutoOps-Insight</div>
          <h1>Production Signal Intelligence Dashboard</h1>
          <p>
            CI failures transformed into structured incidents, recurrence
            signals, and release actions.
          </p>
        </div>
        <div className="hero-pill">Live from FastAPI endpoints</div>
      </div>

      {error ? (
        <div className="card error-card">
          <strong>Dashboard error:</strong> {error}
        </div>
      ) : null}

      <div className="metrics-grid">
        <MetricCard
          title="Total Incidents"
          value={metrics?.total_analyses ?? "-"}
          subtitle="All analyzed CI failures"
        />
        <MetricCard
          title="Hold Releases"
          value={metrics?.hold_release_count ?? "-"}
          subtitle="Incidents blocking ship"
        />
        <MetricCard
          title="Investigate"
          value={metrics?.investigate_count ?? "-"}
          subtitle="Needs operator review"
        />
        <MetricCard
          title="Top Failure"
          value={metrics?.top_failure_family ?? "-"}
          subtitle="Most common incident family"
        />
      </div>

      <div className="charts-grid">
        <Section title="Failure Trends">
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={topFailureData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="failure_family" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Section>

        <Section title="Action Summary">
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={actionData}
                  dataKey="value"
                  nameKey="name"
                  outerRadius={90}
                  label
                >
                  {actionData.map((_, index) => (
                    <Cell key={index} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Section>
      </div>

      <div className="bottom-grid">
        <Section title="Noisy Services">
          <ul className="simple-list">
            {(summary?.noisy_services || []).map((item, idx) => (
              <li key={idx}>
                <span>{item.service}</span>
                <strong>{item.count}</strong>
              </li>
            ))}
          </ul>
        </Section>

        <Section title="Recurrence Heatmap">
          <ul className="simple-list">
            {(summary?.recurrence_heatmap || []).map((item, idx) => (
              <li key={idx}>
                <span>
                  {item.repo_name} · {item.failure_family}
                </span>
                <strong>{item.count}</strong>
              </li>
            ))}
          </ul>
        </Section>
      </div>

      <Section title="Incident Feed">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Repo</th>
                <th>Incident</th>
                <th>Confidence</th>
                <th>Action</th>
                <th>Root Cause</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id}>
                  <td>{row.repo_name}</td>
                  <td>{row.incident_type}</td>
                  <td>{row.confidence}</td>
                  <td>{row.action}</td>
                  <td>{row.root_cause}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>
    </div>
  );
}
