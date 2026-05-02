import { useEffect, useState } from "react";
import "./index.css";

const API_BASE = "http://127.0.0.1:8001";

export default function SupportMetrics() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/support/metrics`)
      .then((res) => res.json())
      .then(setData)
      .catch(console.error);
  }, []);

  if (!data) return <div className="page">Loading support metrics...</div>;

  const topIssue = data.top_issue_family?.[0];

  return (
    <div className="page">
      <div className="hero">
        <div>
          <div className="eyebrow">AUTOOPS SUPPORT INTELLIGENCE</div>
          <h1>AI Product Support Metrics</h1>
          <p>AgentGrid and AI product failures converted into support actions, escalations, and recurring blocker intelligence.</p>
        </div>
        <div className="hero-pill">Live from /support/metrics</div>
      </div>

      <div className="metrics-grid">
        <div className="card metric-card">
          <div className="metric-title">Support Incidents</div>
          <div className="metric-value">{data.total_support_incidents}</div>
          <div className="metric-subtitle">Synthetic scale proof</div>
        </div>

        <div className="card metric-card">
          <div className="metric-title">Escalations</div>
          <div className="metric-value">{data.escalation_count}</div>
          <div className="metric-subtitle">Cases requiring escalation</div>
        </div>

        <div className="card metric-card">
          <div className="metric-title">AgentGrid Events</div>
          <div className="metric-value">{data.agentgrid_events_ingested}</div>
          <div className="metric-subtitle">Hold / escalate events ingested</div>
        </div>

        <div className="card metric-card">
          <div className="metric-title">Top Issue</div>
          <div className="metric-value">{topIssue?.issue_family || "-"}</div>
          <div className="metric-subtitle">{topIssue?.count || 0} cases</div>
        </div>
      </div>

      <div className="bottom-grid">
        <div className="card section-card">
          <div className="section-title">Top Issue Families</div>
          <ul className="simple-list">
            {data.top_issue_family.map((item) => (
              <li key={item.issue_family}>
                <span>{item.issue_family}</span>
                <strong>{item.count}</strong>
              </li>
            ))}
          </ul>
        </div>

        <div className="card section-card">
          <div className="section-title">Recommended Action Distribution</div>
          <ul className="simple-list">
            {data.action_counts.map((item) => (
              <li key={item.action}>
                <span>{item.action}</span>
                <strong>{item.count}</strong>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="bottom-grid">
        <div className="card section-card">
          <div className="section-title">AgentGrid Hold / Escalate Breakdown</div>
          <ul className="simple-list">
            {(data.agentgrid_decision_breakdown || []).map((item, idx) => (
              <li key={idx}>
                <span>{item.agent_decision || "unknown"}</span>
                <strong>{item.count}</strong>
              </li>
            ))}
          </ul>
        </div>

        <div className="card section-card">
          <div className="section-title">Recurring Customer Blockers</div>
          <ul className="simple-list">
            {data.recurring_customer_blockers.map((item) => (
              <li key={item.signature}>
                <span>{item.issue_family}</span>
                <strong>{item.recurrence_total}</strong>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
