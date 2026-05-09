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
