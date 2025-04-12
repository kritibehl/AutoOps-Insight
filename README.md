# 🚀 AutoOps Insight

CI/CD Health & Failure Analyzer built with FastAPI. Analyze build failures, detect flaky pipelines, and integrate intelligent reporting via GitHub Actions and Jenkins.

## 🔧 Features

- Monitor CI/CD pipeline health
- Analyze job failures over time
- AI-driven root cause insights (OpenAI)
- REST API to plug into DevOps workflows

## 📦 Tech Stack

- FastAPI
- GitHub Actions / Jenkins
- OpenAI API
- Python

## ▶️ Getting Started

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
