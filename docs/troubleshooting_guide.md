# AutoOps Troubleshooting Guide

## Purpose

This guide documents common failure modes, debugging steps, and recovery actions for the AutoOps API, GraphQL analytics layer, service metrics, and local development workflow.

## 1. API Does Not Start

### Symptom

```text
ModuleNotFoundError
Common Causes
Missing Python dependency
Virtual environment not activated
requirements.txt not installed
Checks
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m py_compile main.py
Recovery

Install the missing package and update requirements.txt.

2. Port Already in Use
Symptom
ERROR: [Errno 48] Address already in use
Check
lsof -nP -iTCP:8001 -sTCP:LISTEN
Recovery
lsof -ti tcp:8001 | xargs kill -9 2>/dev/null || true
uvicorn main:app --reload --port 8001
3. GraphQL Returns Empty Output
Symptom
Expecting value: line 1 column 1
Common Causes
Server is not running
Wrong endpoint path
Redirect from /graphql/ to /graphql
Correct Request
curl -s http://127.0.0.1:8001/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ metricsSummary { totalAnalyses releaseBlockers releaseRisk } }"}' \
  | python3 -m json.tool
4. GraphQL Resolver Error
Symptom
{
  "data": null,
  "errors": [
    {
      "message": "no such column: release_blocking"
    }
  ]
}
Cause

The local SQLite database was created before newer incident fields were added.

Recovery

Resolvers should use safe access patterns and compatibility defaults for optional fields.

Expected approach:

row.get("release_blocking")

instead of:

row["release_blocking"]
5. Dashboard Summary Fails
Symptom
sqlite3.OperationalError: no such column: filename
Cause

get_recent_analyses() or report summary logic expected a newer database schema.

Recovery

Use PRAGMA table_info(analyses) to detect available columns and provide defaults for missing fields.

6. API Tests Fail During Collection
Symptom
RuntimeError: The starlette.testclient module requires the httpx package to be installed.
Recovery
python3 -m pip install httpx pytest
python3 -m pip freeze | grep -E "pytest|httpx"

Ensure requirements.txt includes:

pytest
httpx
7. Merge Conflict Markers
Symptom
SyntaxError: invalid syntax
<<<<<<< HEAD
Check
grep -R -I "<<<<<<<\|=======$\|>>>>>>>" -n . \
  --exclude-dir=.git \
  --exclude-dir=.venv \
  --exclude-dir=venv \
  --exclude-dir=node_modules \
  --exclude-dir=__pycache__
Recovery

Resolve the conflicted file, remove conflict markers, then run:

python3 -m py_compile main.py storage/history.py graphql_api.py
8. Validation Commands

Run after changes:

python3 -m py_compile main.py graphql_api.py storage/history.py
python3 -m pytest -q tests/test_graphql_metrics.py tests/test_service_metrics_api.py tests/test_dashboard_summary.py
Escalation Checklist

Before treating an issue as unresolved, collect:

failing command
full traceback
endpoint path
current branch
git status --short
local DB schema if SQLite-related
dependency versions if test/import-related
