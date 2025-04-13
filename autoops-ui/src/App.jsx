import { useState } from 'react';
import axios from 'axios';

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState('');
  const [predictResult, setPredictResult] = useState(null);
  const [summaryResult, setSummaryResult] = useState(null);

  const handleFileChange = async (e) => {
    const uploadedFile = e.target.files[0];
    setFile(uploadedFile);
    const text = await uploadedFile.text();
    setPreview(text.slice(0, 2000));
  };

  const handleUpload = async () => {
    if (!file) return alert("Please upload a log file.");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const predict = await axios.post("https://autoops-insight.onrender.com/predict", formData);
      const summary = await axios.post("https://autoops-insight.onrender.com/summarize", formData);

      setPredictResult(predict.data);
      setSummaryResult(summary.data);
    } catch (err) {
      console.error(err);
      alert("Upload failed. Is backend running?");
    }
  };

  return (
    <div className="min-h-screen bg-blue-50 text-blue-900 font-sans px-6 py-10 flex items-start justify-center">
      <div className="w-full max-w-3xl space-y-8">
        <h1 className="text-4xl font-bold text-center">🚀 AutoOps Insight</h1>

        <div className="bg-white p-6 rounded-xl shadow-lg space-y-6">
          <div className="flex flex-col items-center space-y-4">
            <label className="text-sm font-semibold">Upload CI/CD Log File:</label>
            <input
              type="file"
              accept=".txt"
              onChange={handleFileChange}
              className="text-sm file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:bg-blue-600 file:text-white hover:file:bg-blue-700"
            />
            <button
              onClick={handleUpload}
              className="bg-blue-700 hover:bg-blue-800 text-white font-semibold px-6 py-2 rounded-lg transition"
            >
              Analyze Log
            </button>
          </div>

          {preview && (
            <div>
              <h2 className="text-lg font-semibold mb-2">📝 Log Preview</h2>
              <pre className="bg-blue-100 text-sm p-4 rounded-md max-h-64 overflow-auto whitespace-pre-wrap border border-blue-200">
                {preview}
              </pre>
            </div>
          )}
        </div>

        {predictResult && (
          <div className="bg-white p-6 rounded-xl shadow space-y-2 border-t-4 border-blue-600">
            <h3 className="text-xl font-bold">🔍 Predicted Issue</h3>
            <p className="text-base">
              <strong>{predictResult.predicted_issue}</strong> (Confidence: {predictResult.confidence})
            </p>
          </div>
        )}

        {summaryResult && (
          <div className="bg-white p-6 rounded-xl shadow space-y-2 border-t-4 border-blue-600">
            <h3 className="text-xl font-bold">📄 Log Summary</h3>
            <pre className="bg-blue-100 text-sm p-4 rounded whitespace-pre-wrap border border-blue-200">
              {summaryResult.summary}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
