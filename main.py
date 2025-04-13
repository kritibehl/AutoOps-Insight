from fastapi.middleware.cors import CORSMiddleware
from ml_predictor import predict_log_issue
from fastapi import FastAPI, UploadFile, File
from prometheus_client import Counter, generate_latest
from fastapi.responses import PlainTextResponse
from genai_summarizer import summarize_log

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
logs_processed = Counter("logs_processed_total", "Number of logs processed")

@app.get("/")
def root():
    return {"message": "AutoOps Insight is running!"}

@app.post("/predict")
async def predict_log(file: UploadFile = File(...)):
    logs_processed.inc()
    content = await file.read()
    text = content.decode("utf-8")
    result = predict_log_issue(text)
    return result

@app.post("/summarize")
async def summarize_log_endpoint(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8")
    summary = summarize_log(text)
    return {"summary": summary}

@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return generate_latest()
