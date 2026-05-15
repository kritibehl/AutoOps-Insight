#!/usr/bin/env bash
set -euo pipefail

AUTOOPS_URL="${AUTOOPS_URL:-https://autoops-api-126325674316.us-central1.run.app}"

echo "== Health =="
curl -s "$AUTOOPS_URL/" | python3 -m json.tool

echo "== Live Support Metrics =="
curl -s "$AUTOOPS_URL/support/metrics/live" | python3 -m json.tool

echo "== Lifecycle Transition =="
curl -s -X POST \
  "$AUTOOPS_URL/incidents/INC-1001/transition/live?actor=kriti&old_state=new&new_state=triaged&reason=demo_proof" \
  | python3 -m json.tool

echo "== Correlation Demo =="
curl -s "$AUTOOPS_URL/correlation/demo" | python3 -m json.tool

echo "== Correlation Demo =="
curl -s "$AUTOOPS_URL/correlation/demo" | python3 -m json.tool

echo "== Deployment-to-Incident Correlation =="
curl -s "$AUTOOPS_URL/release-correlation/demo" | python3 -m json.tool

echo "== RCA Generator Demo =="
curl -s "$AUTOOPS_URL/rca/demo" | python3 -m json.tool

echo "== Responsible AI Monitoring Summary =="
curl -s "$AUTOOPS_URL/rai/monitoring/summary" | python3 -m json.tool

echo "== Responsible AI Incident Detail =="
curl -s "$AUTOOPS_URL/rai/incidents/RAI-rai-eval-2026-05-15" | python3 -m json.tool
