# AutoOps Insight 🚀

**CI/CD Log Analyzer + Failure Prediction + Summary Generator**

AutoOps Insight is a full-stack DevOps dashboard that analyzes CI/CD logs, predicts failure types using machine learning, and provides human-readable summaries.

## ✨ Features

- Upload `.txt` log files
- 🔍 Predict likely CI/CD failure (e.g. Dependency Error)
- 📄 Summarize build logs using keyword-based or LLM logic
- 🎨 Modern React UI with Tailwind CSS
- 💡 Prometheus metrics for /metrics endpoint
- 🌐 FastAPI backend + React frontend
- 🔐 API key protected via `.env`

## 🛠 Tech Stack

- **Frontend**: React (Vite), Tailwind CSS, Axios
- **Backend**: FastAPI, Python, Scikit-learn, dotenv
- **ML**: Log classifier (TF-IDF + LogisticRegression)
- **Infra**: Prometheus, Docker-ready
- **AI**: Optional OpenAI GenAI summarizer


## 🚀 Local Setup

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/autoops-insight.git
cd autoops-insight
