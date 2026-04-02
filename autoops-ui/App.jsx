import React, { useEffect, useMemo, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8001";

function Badge({ children, tone = "default" }) {
  const styles = {
    default: { background: "#1f2937", color: "#e5e7eb" },
    high: { background: "#7f1d1d", color: "#fecaca" },
    medium: { background: "#78350f", color: "#fde68a" },
    low: { background: "#064e3b", color: "#d1fae5" },
    open: { background: "#1d4ed8", color: "#dbeafe" },
    resolved: { background: "#166534", color: "#dcfce7" },
  };
  return (
    <span style={{
      ...styles[tone],
      borderRadius: 999,
      padding: "4px 10px",
      fontSize: 12,
      fontWeight: 700,
      display: "inline-block",
    }}>
      {children}
    </span>
  );
}

function Card({ title, value, subtitle }) {
  return (
    <div style={{
      background: "#111827",
      border: "1px solid #1f2937",
      borderRadius: 16,
      padding: 18,
      minHeight: 110,
    }}>
      <div style={{ color: "#9ca3af", fontSize: 13, marginBottom: 8 }}>{title}</div>
      <div style={{ color: "#f9fafb", fontSize: 28, fontWeight: 800 }}>{value}</div>
      {subtitle ? <div style={{ color: "#6b7280", fontSize: 12, marginTop: 8 }}>{subtitle}</div> : null}
    </div>
  );
}

export default function App() {
  const [incidents, setIncidents] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [selected, setSelected] = useState(null);
  const [selectedDetail, setSelectedDetail] = useState(null);
  const [feedbackNotes, setFeedbackNotes] = useState("");
  const [filter, setFilter] = useState("all");

  async function loadInbox() {
    const url = filter === "all" ? `${API_BASE}/incident-inbox` : `${API_BASE}/incident-inbox?status=${filter}`;
    const res = await fetch(url);
    const data = await res.json();
    setIncidents(data.items || []);
  }

  async function loadAnalytics() {
    const res = await fetch(`${API_BASE}/incident-analytics`);
    const data = await res.json();
    setAnalytics(data);
  }

  async function loadIncidentDetail(id) {
    const res = await fetch(`${API_BASE}/incidents/${id}`);
    const data = await res.json();
    setSelectedDetail(data);
  }

  useEffect(() => {
    loadInbox();
  }, [filter]);

  useEffect(() => {
    loadAnalytics();
  }, []);

  async function resolveIncident(id) {
    await fetch(`${API_BASE}/incidents/${id}/status`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: "resolved", final_resolution: "operator_resolved" }),
    });
    await loadInbox();
    await loadAnalytics();
    if (selected === id) await loadIncidentDetail(id);
  }

  async function submitFeedback(id, classificationCorrect, suggestionUseful) {
    await fetch(`${API_BASE}/incidents/${id}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        classification_correct: classificationCorrect,
        suggestion_useful: suggestionUseful,
        final_resolution: null,
        notes: feedbackNotes || null,
      }),
    });
    setFeedbackNotes("");
    if (selected === id) await loadIncidentDetail(id);
    await loadAnalytics();
  }

  const trendText = useMemo(() => {
    if (!analytics?.incidents_over_time?.length) return "No trend data yet";
    const latest = analytics.incidents_over_time[analytics.incidents_over_time.length - 1];
    if (latest.delta_pct == null) return `Latest day: ${latest.count} incidents`;
    const direction = latest.delta_pct > 0 ? "increased" : "changed";
    return `${latest.count} incidents on ${latest.day} (${direction} ${latest.delta_pct}%)`;
  }, [analytics]);

  return (
    <div style={{
      background: "#030712",
      minHeight: "100vh",
      color: "#f9fafb",
      fontFamily: "Inter, system-ui, sans-serif",
      padding: 24,
    }}>
      <div style={{ maxWidth: 1400, margin: "0 auto" }}>
        <div style={{ marginBottom: 24 }}>
          <div style={{ color: "#60a5fa", fontSize: 13, fontWeight: 800, letterSpacing: 0.5 }}>
            AUTOOPS INSIGHT
          </div>
          <h1 style={{ fontSize: 36, margin: "6px 0 8px 0" }}>
            Internal Incident Triage & Operations Platform
          </h1>
          <p style={{ color: "#9ca3af", maxWidth: 980, lineHeight: 1.6 }}>
            Turn raw workflow events, logs, and alerts into grouped incidents with likely cause,
            suggested fix, replay visibility, trend reporting, operator feedback, and action-ready triage.
          </p>
        </div>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
          gap: 16,
          marginBottom: 24,
        }}>
          <Card title="Open incidents" value={analytics?.open_incidents ?? 0} subtitle="operator inbox" />
          <Card title="Resolution rate" value={analytics ? `${Math.round((analytics.resolution_rate || 0) * 100)}%` : "0%"} subtitle="resolved / total" />
          <Card title="Rule hit rate" value={analytics ? `${Math.round((analytics.rule_hit_rate || 0) * 100)}%` : "0%"} subtitle="feedback-backed usefulness" />
          <Card title="Incident trend" value={analytics?.summary_cards?.total_incidents ?? 0} subtitle={trendText} />
        </div>

        <div style={{
          display: "grid",
          gridTemplateColumns: "2fr 1fr",
          gap: 18,
          alignItems: "start",
        }}>
          <div style={{
            background: "#111827",
            border: "1px solid #1f2937",
            borderRadius: 18,
            padding: 18,
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
              <div>
                <h2 style={{ margin: 0 }}>Incident Inbox</h2>
                <div style={{ color: "#9ca3af", fontSize: 13, marginTop: 4 }}>
                  Main operator view: one row per incident.
                </div>
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                {["all", "open", "resolved"].map((opt) => (
                  <button
                    key={opt}
                    onClick={() => setFilter(opt)}
                    style={{
                      background: filter === opt ? "#2563eb" : "#1f2937",
                      color: "#fff",
                      border: "none",
                      borderRadius: 10,
                      padding: "8px 12px",
                      cursor: "pointer",
                      fontWeight: 700,
                    }}
                  >
                    {opt.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                <thead>
                  <tr style={{ color: "#9ca3af", textAlign: "left", borderBottom: "1px solid #1f2937" }}>
                    <th style={{ padding: "10px 8px" }}>Incident ID</th>
                    <th style={{ padding: "10px 8px" }}>Failure Type</th>
                    <th style={{ padding: "10px 8px" }}>Severity</th>
                    <th style={{ padding: "10px 8px" }}>Source</th>
                    <th style={{ padding: "10px 8px" }}>Confidence</th>
                    <th style={{ padding: "10px 8px" }}>Suggested Cause</th>
                    <th style={{ padding: "10px 8px" }}>Suggested Fix</th>
                    <th style={{ padding: "10px 8px" }}>Status</th>
                    <th style={{ padding: "10px 8px" }}>Replay</th>
                    <th style={{ padding: "10px 8px" }}>Act</th>
                  </tr>
                </thead>
                <tbody>
                  {incidents.map((row) => (
                    <tr
                      key={row.id}
                      onClick={() => {
                        setSelected(row.id);
                        loadIncidentDetail(row.id);
                      }}
                      style={{
                        borderBottom: "1px solid #1f2937",
                        cursor: "pointer",
                        background: selected === row.id ? "#0f172a" : "transparent",
                      }}
                    >
                      <td style={{ padding: "12px 8px", fontWeight: 700 }}>#{row.id}</td>
                      <td style={{ padding: "12px 8px" }}>{row.failure_type}</td>
                      <td style={{ padding: "12px 8px" }}><Badge tone={row.severity}>{row.severity}</Badge></td>
                      <td style={{ padding: "12px 8px" }}>{row.source}</td>
                      <td style={{ padding: "12px 8px" }}>{Number(row.confidence).toFixed(2)}</td>
                      <td style={{ padding: "12px 8px", maxWidth: 220 }}>{row.suggested_cause}</td>
                      <td style={{ padding: "12px 8px", maxWidth: 220 }}>{row.suggested_fix}</td>
                      <td style={{ padding: "12px 8px" }}><Badge tone={row.status}>{row.status}</Badge></td>
                      <td style={{ padding: "12px 8px" }}>{row.replay_available ? "yes" : "no"}</td>
                      <td style={{ padding: "12px 8px" }}>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            resolveIncident(row.id);
                          }}
                          style={{
                            background: "#166534",
                            color: "white",
                            border: "none",
                            borderRadius: 8,
                            padding: "8px 10px",
                            cursor: "pointer",
                          }}
                        >
                          Resolve
                        </button>
                      </td>
                    </tr>
                  ))}
                  {!incidents.length && (
                    <tr>
                      <td colSpan="10" style={{ padding: 20, color: "#9ca3af" }}>
                        No incidents yet. Ingest logs, alerts, or Faultline events.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div style={{ display: "grid", gap: 18 }}>
            <div style={{
              background: "#111827",
              border: "1px solid #1f2937",
              borderRadius: 18,
              padding: 18,
            }}>
              <h3 style={{ marginTop: 0 }}>Analytics Dashboard</h3>
              <div style={{ color: "#9ca3af", fontSize: 13, marginBottom: 12 }}>
                Top failure categories, repeat incidents, and rule effectiveness.
              </div>

              <div style={{ marginBottom: 16 }}>
                <div style={{ fontWeight: 700, marginBottom: 8 }}>Top failure categories</div>
                {(analytics?.top_failure_categories || []).map(([name, count]) => (
                  <div key={name} style={{ display: "flex", justifyContent: "space-between", padding: "6px 0", borderBottom: "1px solid #1f2937" }}>
                    <span>{name}</span>
                    <span>{count}</span>
                  </div>
                ))}
              </div>

              <div>
                <div style={{ fontWeight: 700, marginBottom: 8 }}>Repeat incidents</div>
                {(analytics?.repeat_incidents || []).slice(0, 5).map((item) => (
                  <div key={item.incident_id} style={{ padding: "8px 0", borderBottom: "1px solid #1f2937" }}>
                    #{item.incident_id} · {item.failure_type} · {item.event_count} events
                  </div>
                ))}
              </div>
            </div>

            <div style={{
              background: "#111827",
              border: "1px solid #1f2937",
              borderRadius: 18,
              padding: 18,
            }}>
              <h3 style={{ marginTop: 0 }}>Incident Detail</h3>
              {!selectedDetail?.incident ? (
                <div style={{ color: "#9ca3af" }}>Select an incident from the inbox.</div>
              ) : (
                <>
                  <div style={{ marginBottom: 10 }}>
                    <div style={{ fontSize: 13, color: "#9ca3af" }}>Likely cause</div>
                    <div>{selectedDetail.incident.suggested_cause}</div>
                  </div>
                  <div style={{ marginBottom: 10 }}>
                    <div style={{ fontSize: 13, color: "#9ca3af" }}>Suggested fix</div>
                    <div>{selectedDetail.runbook?.suggested_fix}</div>
                  </div>
                  <div style={{ marginBottom: 10 }}>
                    <div style={{ fontSize: 13, color: "#9ca3af" }}>Escalation route</div>
                    <div>{selectedDetail.runbook?.escalation_route}</div>
                  </div>
                  <div style={{ marginBottom: 10 }}>
                    <div style={{ fontSize: 13, color: "#9ca3af" }}>Mitigation sequence</div>
                    <ol style={{ paddingLeft: 18 }}>
                      {(selectedDetail.runbook?.mitigation_sequence || []).map((step, idx) => (
                        <li key={idx} style={{ marginBottom: 4 }}>{step}</li>
                      ))}
                    </ol>
                  </div>

                  <div style={{ marginTop: 14 }}>
                    <div style={{ fontSize: 13, color: "#9ca3af", marginBottom: 6 }}>Feedback loop</div>
                    <textarea
                      value={feedbackNotes}
                      onChange={(e) => setFeedbackNotes(e.target.value)}
                      placeholder="operator notes / final resolution"
                      rows={3}
                      style={{
                        width: "100%",
                        background: "#0b1220",
                        color: "#f9fafb",
                        border: "1px solid #1f2937",
                        borderRadius: 10,
                        padding: 10,
                        marginBottom: 10,
                      }}
                    />
                    <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                      <button onClick={() => submitFeedback(selectedDetail.incident.id, true, true)} style={btnStyle("#2563eb")}>
                        Classification correct + useful
                      </button>
                      <button onClick={() => submitFeedback(selectedDetail.incident.id, false, false)} style={btnStyle("#7c2d12")}>
                        Classification incorrect + not useful
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function btnStyle(bg) {
  return {
    background: bg,
    color: "#fff",
    border: "none",
    borderRadius: 10,
    padding: "8px 12px",
    cursor: "pointer",
    fontWeight: 700,
  };
}
