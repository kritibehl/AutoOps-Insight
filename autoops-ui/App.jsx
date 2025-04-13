import { useState } from 'react';
import axios from 'axios';

function App() {
  const [file, setFile] = useState(null);
  const [predictResult, setPredictResult] = useState(null);
  const [summaryResult, setSummaryResult] = useState(null);

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleUpload = async () => {
    if (!file) return alert("Please upload a log file.");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const predict = await axios.post("http://127.0.0.1:8000/predict", formData);
      const summary = await axios.post("http://127.0.0.1:8000/summarize", formData);
      setPredictResult(predict.data);
      setSummaryResult(summary.data);
    } catch (err) {
      console.error(err);
      alert("Upload failed. Is the backend running?");
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial, sans-serif" }}>
      <h1 style={{ fontSize: "24px", fontWeight: "bold" }}>AutoOps Insight</h1>
      <input type="file" onChange={handleFileChange} style={{ margin: "1rem 0" }} />
      <br />
      <button onClick={handleUpload} style={{ padding: "0.5rem 1rem", backgroundColor: "#007bff", color: "#fff", border: "none", borderRadius: "4px" }}>
        Analyze Log
      </button>

      {predictResult && (
        <div style={{ marginTop: "2rem" }}>
          <h3>🔍 Predicted Issue:</h3>
          <p><strong>{predictResult.predicted_issue}</strong> (Confidence: {predictResult.confidence})</p>
        </div>
      )}

      {summaryResult && (
        <div style={{ marginTop: "1.5rem" }}>
          <h3>📄 Log Summary:</h3>
          <pre style={{ background: "#f9f9f9", padding: "1rem", borderRadius: "5px" }}>
            {summaryResult.summary}
          </pre>
        </div>
      )}
    </div>
  );
}

export default App;
