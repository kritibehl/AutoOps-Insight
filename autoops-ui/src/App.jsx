import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import "./App.css";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function JsonBlock({ data }) {
  return (
    <pre className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-xs overflow-auto whitespace-pre-wrap">
      {JSON.stringify(data, null, 2)}
    </pre>
  );
}

function SectionCard({ title, children }) {
  return (
    <section className="bg-white border border-slate-200 rounded-2xl shadow-sm p-5 space-y-4">
      <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
      {children}
    </section>
  );
}

export default function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [reportSummary, setReportSummary] = useState(null);
  const [auditItems, setAuditItems] = useState([]);
  const [selectedAudit, setSelectedAudit] = useState(null);
  const [rollbackPreview, setRollbackPreview] = useState(null);
  const [loading, setLoading] = useState(false);

  const hasAuditItems = auditItems.length > 0;

  const stats = useMemo(() => {
    if (!reportSummary) return null;
    return [
      { label: "Release Risk", value: reportSummary.release_risk || "unknown" },
      { label: "Total Analyses", value: reportSummary.total_analyses ?? 0 },
      { label: "Release Blockers", value: reportSummary.release_blockers ?? 0 },
      {
        label: "Recurring Signatures",
        value: reportSummary.top_recurring_signatures?.length ?? 0,
      },
    ];
  }, [reportSummary]);

  async function refreshReport() {
    const { data } = await axios.get(`${API_BASE_URL}/reports/summary`);
    setReportSummary(data);
  }

  async function refreshAudit() {
    const { data } = await axios.get(`${API_BASE_URL}/audit/recent`);
    setAuditItems(data.items || []);
  }

  useEffect(() => {
    refreshReport().catch(console.error);
    refreshAudit().catch(console.error);
  }, []);

  async function handleFileChange(e) {
    const uploadedFile = e.target.files?.[0];
    if (!uploadedFile) return;
    setFile(uploadedFile);
    const text = await uploadedFile.text();
    setPreview(text.slice(0, 3000));
  }

  async function handleAnalyze() {
    if (!file) {
      alert("Please select a log file first.");
      return;
    }
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const { data } = await axios.post(`${API_BASE_URL}/analyze`, formData);
      setAnalysis(data);

      await refreshReport();
      await refreshAudit();
    } catch (err) {
      console.error(err);
      alert("Analyze request failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSelectAudit(auditId) {
    try {
      const { data } = await axios.get(`${API_BASE_URL}/audit/${auditId}`);
      setSelectedAudit(data);
      setRollbackPreview(null);
    } catch (err) {
      console.error(err);
      alert("Failed to load audit event.");
    }
  }

  async function handleRollbackPreview(auditId) {
    try {
      const { data } = await axios.get(
        `${API_BASE_URL}/audit/${auditId}/rollback-preview`
      );
      setRollbackPreview(data);
    } catch (err) {
      console.error(err);
      alert("Failed to load rollback preview.");
    }
  }

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <div className="max-w-7xl mx-auto px-6 py-8 space-y-6">
        <header className="space-y-2">
          <h1 className="text-3xl font-bold">AutoOps-Insight</h1>
          <p className="text-slate-600">
            Reliability analytics for CI and infrastructure failures with audit-backed rule previews.
          </p>
        </header>

        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {stats.map((item) => (
              <div
                key={item.label}
                className="bg-white border border-slate-200 rounded-2xl shadow-sm p-4"
              >
                <div className="text-sm text-slate-500">{item.label}</div>
                <div className="text-2xl font-semibold mt-2">{item.value}</div>
              </div>
            ))}
          </div>
        )}

        <SectionCard title="Analyze Log">
          <div className="flex flex-col md:flex-row gap-3 md:items-center">
            <input
              type="file"
              accept=".log,.txt"
              onChange={handleFileChange}
              className="block w-full text-sm"
            />
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="px-4 py-2 rounded-xl bg-slate-900 text-white disabled:opacity-50"
            >
              {loading ? "Analyzing..." : "Analyze"}
            </button>
          </div>

          {preview && (
            <div>
              <h3 className="font-medium mb-2">Log Preview</h3>
              <pre className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-xs overflow-auto whitespace-pre-wrap">
                {preview}
              </pre>
            </div>
          )}

          {analysis && (
            <div className="space-y-3">
              <h3 className="font-medium">Latest Incident</h3>
              <JsonBlock data={analysis} />
            </div>
          )}
        </SectionCard>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <SectionCard title="Audit History">
            {!hasAuditItems ? (
              <p className="text-sm text-slate-500">No audit events yet.</p>
            ) : (
              <div className="space-y-3">
                {auditItems.map((item) => (
                  <div
                    key={item.id}
                    className="border border-slate-200 rounded-xl p-4 bg-slate-50 space-y-2"
                  >
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-2">
                      <div>
                        <div className="font-medium">
                          {item.event_type} · {item.rule_id}
                        </div>
                        <div className="text-sm text-slate-500">
                          actor={item.actor} · {item.timestamp}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleSelectAudit(item.id)}
                          className="px-3 py-1.5 rounded-lg border border-slate-300 bg-white text-sm"
                        >
                          View Diff
                        </button>
                        <button
                          onClick={() => handleRollbackPreview(item.id)}
                          className="px-3 py-1.5 rounded-lg bg-slate-900 text-white text-sm"
                        >
                          Rollback Preview
                        </button>
                      </div>
                    </div>
                    <div className="text-sm text-slate-600">
                      {item.change_summary}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </SectionCard>

          <SectionCard title="Rule Diff / Rollback Preview">
            {selectedAudit ? (
              <div className="space-y-4">
                <div>
                  <div className="font-medium">Selected Audit Event</div>
                  <div className="text-sm text-slate-500">
                    audit_id={selectedAudit.id} · rule_id={selectedAudit.rule_id}
                  </div>
                </div>
                <div>
                  <h3 className="font-medium mb-2">Field Diff</h3>
                  <JsonBlock data={selectedAudit.diff || {}} />
                </div>
              </div>
            ) : (
              <p className="text-sm text-slate-500">
                Select an audit event to inspect the rule diff.
              </p>
            )}

            {rollbackPreview && (
              <div className="space-y-2">
                <h3 className="font-medium">Rollback Impact Preview</h3>
                <JsonBlock data={rollbackPreview} />
              </div>
            )}
          </SectionCard>
        </div>
      </div>
    </div>
  );
}
