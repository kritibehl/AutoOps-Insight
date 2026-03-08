import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import "./App.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function Section({ title, children, right }) {
  return (
    <section className="card">
      <div className="section-header">
        <h2>{title}</h2>
        {right ? <div>{right}</div> : null}
      </div>
      {children}
    </section>
  );
}

function StatCard({ label, value, tone = "default" }) {
  return (
    <div className={`stat-card stat-${tone}`}>
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
    </div>
  );
}

function KeyValue({ label, value }) {
  return (
    <div className="kv-row">
      <span className="kv-label">{label}</span>
      <span className="kv-value">{value}</span>
    </div>
  );
}

function Badge({ children, tone = "default" }) {
  return <span className={`badge badge-${tone}`}>{children}</span>;
}

function toneForSeverity(severity) {
  if (severity === "critical") return "critical";
  if (severity === "high") return "high";
  if (severity === "medium") return "medium";
  return "default";
}

function toneForRisk(risk) {
  if (risk === "critical") return "critical";
  if (risk === "high") return "high";
  if (risk === "medium") return "medium";
  return "default";
}

export default function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [analyzeResult, setAnalyzeResult] = useState(null);
  const [reportSummary, setReportSummary] = useState(null);
  const [recentHistory, setRecentHistory] = useState([]);
  const [recurringHistory, setRecurringHistory] = useState([]);
  const [markdownReport, setMarkdownReport] = useState("");
  const [loadingAnalyze, setLoadingAnalyze] = useState(false);
  const [loadingDashboard, setLoadingDashboard] = useState(false);
  const [error, setError] = useState("");

  const releaseRiskTone = useMemo(
    () => toneForRisk(reportSummary?.release_risk),
    [reportSummary]
  );

  async function loadDashboard() {
    setLoadingDashboard(true);
    try {
      const [summaryRes, recentRes, recurringRes, markdownRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/reports/summary`),
        axios.get(`${API_BASE_URL}/history/recent`),
        axios.get(`${API_BASE_URL}/history/recurring`),
        axios.get(`${API_BASE_URL}/reports/markdown`),
      ]);

      setReportSummary(summaryRes.data);
      setRecentHistory(recentRes.data.items || []);
      setRecurringHistory(recurringRes.data.items || []);
      setMarkdownReport(markdownRes.data || "");
    } catch (err) {
      console.error(err);
      setError("Failed to load dashboard data from backend.");
    } finally {
      setLoadingDashboard(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  async function handleFileChange(e) {
    const uploadedFile = e.target.files?.[0];
    setFile(uploadedFile || null);

    if (!uploadedFile) {
      setPreview("");
      return;
    }

    const text = await uploadedFile.text();
    setPreview(text.slice(0, 3000));
  }

  async function handleAnalyze() {
    if (!file) {
      setError("Please choose a log file first.");
      return;
    }

    setError("");
    setLoadingAnalyze(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(`${API_BASE_URL}/analyze`, formData);
      setAnalyzeResult(response.data);
      await loadDashboard();
    } catch (err) {
      console.error(err);
      setError("Analysis failed. Check that the backend is running.");
    } finally {
      setLoadingAnalyze(false);
    }
  }

  return (
    <div className="app-shell">
      <div className="app-container">
        <header className="hero">
          <div>
            <h1>AutoOps Insight</h1>
            <p>
              Reliability analytics for CI and infrastructure failures: structured incident
              analysis, recurring signature tracking, anomaly heuristics, and release-risk
              reporting.
            </p>
          </div>
          <div className="hero-actions">
            <button className="primary-btn" onClick={loadDashboard} disabled={loadingDashboard}>
              {loadingDashboard ? "Refreshing..." : "Refresh Dashboard"}
            </button>
          </div>
        </header>

        {error ? <div className="error-banner">{error}</div> : null}

        <div className="stats-grid">
          <StatCard
            label="Release Risk"
            value={reportSummary?.release_risk || "unknown"}
            tone={releaseRiskTone}
          />
          <StatCard
            label="Total Analyses"
            value={reportSummary?.total_analyses ?? 0}
          />
          <StatCard
            label="Release Blockers"
            value={reportSummary?.release_blockers ?? 0}
            tone="high"
          />
          <StatCard
            label="Recurring Signatures"
            value={recurringHistory.length}
            tone="medium"
          />
        </div>

        <div className="two-col">
          <Section title="Analyze Log">
            <div className="upload-box">
              <input type="file" accept=".txt,.log" onChange={handleFileChange} />
              <button className="primary-btn" onClick={handleAnalyze} disabled={loadingAnalyze}>
                {loadingAnalyze ? "Analyzing..." : "Analyze Log"}
              </button>
            </div>

            {preview ? (
              <>
                <h3 className="subheading">Log Preview</h3>
                <pre className="code-block">{preview}</pre>
              </>
            ) : null}
          </Section>

          <Section
            title="Release Risk Summary"
            right={
              reportSummary?.release_risk ? (
                <Badge tone={releaseRiskTone}>{reportSummary.release_risk}</Badge>
              ) : null
            }
          >
            <div className="kv-list">
              <KeyValue label="Total analyses" value={reportSummary?.total_analyses ?? 0} />
              <KeyValue label="Release blockers" value={reportSummary?.release_blockers ?? 0} />
              <KeyValue
                label="Recent blocker rate"
                value={`${reportSummary?.window_comparison?.recent_release_blocker_rate ?? 0}%`}
              />
              <KeyValue
                label="Baseline blocker rate"
                value={`${reportSummary?.window_comparison?.baseline_release_blocker_rate ?? 0}%`}
              />
            </div>
          </Section>
        </div>

        <div className="two-col">
          <Section title="Current Incident Analysis">
            {analyzeResult ? (
              <>
                <div className="badges-row">
                  <Badge tone={toneForSeverity(analyzeResult.severity)}>
                    severity: {analyzeResult.severity}
                  </Badge>
                  <Badge tone={analyzeResult.release_blocking ? "high" : "default"}>
                    {analyzeResult.release_blocking ? "release-blocking" : "non-blocking"}
                  </Badge>
                  <Badge tone="medium">{analyzeResult.failure_family}</Badge>
                </div>

                <div className="kv-list top-space">
                  <KeyValue label="Predicted issue" value={analyzeResult.predicted_issue} />
                  <KeyValue label="Confidence" value={analyzeResult.confidence} />
                  <KeyValue label="Signature" value={analyzeResult.signature} />
                  <KeyValue
                    label="Recurring"
                    value={analyzeResult.recurrence?.is_recurring ? "yes" : "no"}
                  />
                  <KeyValue
                    label="Occurrence count"
                    value={analyzeResult.recurrence?.total_count ?? 0}
                  />
                  <KeyValue label="Probable owner" value={analyzeResult.probable_owner} />
                </div>

                <h3 className="subheading">Summary</h3>
                <p className="body-copy">{analyzeResult.summary}</p>

                <h3 className="subheading">Recommended Next Steps</h3>
                <ul className="list">
                  <li>{analyzeResult.likely_cause}</li>
                  <li>{analyzeResult.first_remediation_step}</li>
                  <li>{analyzeResult.next_debugging_action}</li>
                </ul>

                <h3 className="subheading">Evidence</h3>
                <div className="stack">
                  {(analyzeResult.evidence || []).map((item, idx) => (
                    <div className="evidence-item" key={`${item.line_number}-${idx}`}>
                      <div className="evidence-line">line {item.line_number}</div>
                      <div className="evidence-text">{item.text}</div>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <p className="muted">
                Analyze a log to see structured incident output, recurrence information, and
                operational recommendations.
              </p>
            )}
          </Section>

          <Section title="Detected Anomalies">
            {reportSummary?.anomalies?.length ? (
              <div className="stack">
                {reportSummary.anomalies.map((item, idx) => (
                  <div className="anomaly-item" key={`${item.type}-${idx}`}>
                    <div className="anomaly-top">
                      <Badge tone={toneForSeverity(item.severity)}>{item.severity}</Badge>
                      <span className="mono">{item.type}</span>
                    </div>
                    <div className="body-copy">{item.message}</div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="muted">No anomaly heuristics triggered.</p>
            )}
          </Section>
        </div>

        <div className="two-col">
          <Section title="Recurring Signatures">
            {recurringHistory.length ? (
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Signature</th>
                      <th>Family</th>
                      <th>Severity</th>
                      <th>Count</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recurringHistory.map((item) => (
                      <tr key={item.signature}>
                        <td className="mono">{item.signature}</td>
                        <td>{item.failure_family}</td>
                        <td>
                          <Badge tone={toneForSeverity(item.severity)}>{item.severity}</Badge>
                        </td>
                        <td>{item.total_count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="muted">No recurring signatures yet.</p>
            )}
          </Section>

          <Section title="Recent Analyses">
            {recentHistory.length ? (
              <div className="stack">
                {recentHistory.slice(0, 8).map((item) => (
                  <div className="history-item" key={item.id}>
                    <div className="history-top">
                      <span className="mono">id={item.id}</span>
                      <Badge tone={toneForSeverity(item.severity)}>{item.severity}</Badge>
                    </div>
                    <div className="body-copy">
                      {item.failure_family} · {item.filename || "unknown file"}
                    </div>
                    <div className="history-meta">
                      <span className="mono">{item.signature}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="muted">No analysis history yet.</p>
            )}
          </Section>
        </div>

        <div className="two-col">
          <Section title="Recent Failure Family Distribution">
            {reportSummary?.recent_failure_family_distribution?.length ? (
              <div className="stack">
                {reportSummary.recent_failure_family_distribution.map((item) => (
                  <div className="dist-row" key={item.failure_family}>
                    <div className="dist-label">{item.failure_family}</div>
                    <div className="dist-bar-wrap">
                      <div
                        className="dist-bar"
                        style={{ width: `${Math.max(item.percentage, 4)}%` }}
                      />
                    </div>
                    <div className="dist-value">{item.percentage}%</div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="muted">No recent distribution available.</p>
            )}
          </Section>

          <Section title="Markdown Report Preview">
            {markdownReport ? (
              <pre className="code-block tall">{markdownReport}</pre>
            ) : (
              <p className="muted">No markdown report generated yet.</p>
            )}
          </Section>
        </div>
      </div>
    </div>
  );
}
