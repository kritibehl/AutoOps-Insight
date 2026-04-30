# Incident Analytics Pipeline

## Flow

CI failure logs
→ AutoOps ingest API
→ classification + enrichment
→ structured incidents
→ normalization pipeline
→ analytics tables / parquet exports
→ dashboard + metrics APIs

## Outputs

- normalized incident dataset
- failure family trends
- release decision counts
- recurrence-aware analysis

## Why this matters

AutoOps converts raw CI logs into structured, analyzable datasets for:

- release safety
- incident intelligence
- reliability analytics
