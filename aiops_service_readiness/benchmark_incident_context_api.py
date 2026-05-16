import json
import time
import statistics
import urllib.request
from pathlib import Path

AUTOOPS_URL = "https://autoops-api-126325674316.us-central1.run.app"
ENDPOINT = f"{AUTOOPS_URL}/aiops/incident-context/demo"

REQUIRED_FIELDS = [
    "incident_id",
    "triage_summary",
    "probable_root_cause_hypotheses",
    "historical_context",
    "recommended_next_actions",
]

def fetch_once():
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(ENDPOINT, timeout=10) as response:
            body = response.read().decode("utf-8")
            latency_ms = (time.perf_counter() - start) * 1000
            data = json.loads(body)
            return {
                "success": response.status == 200,
                "latency_ms": round(latency_ms, 2),
                "data": data,
                "error": None,
            }
    except Exception as exc:
        latency_ms = (time.perf_counter() - start) * 1000
        return {
            "success": False,
            "latency_ms": round(latency_ms, 2),
            "data": None,
            "error": str(exc),
        }

def schema_valid(data):
    if not isinstance(data, dict):
        return False
    return all(field in data for field in REQUIRED_FIELDS)

def percentile(values, p):
    if not values:
        return None
    sorted_values = sorted(values)
    idx = int(round((p / 100) * (len(sorted_values) - 1)))
    return round(sorted_values[idx], 2)

def run_benchmark(total_requests=10):
    results = [fetch_once() for _ in range(total_requests)]

    successful = [r for r in results if r["success"]]
    latencies = [r["latency_ms"] for r in successful]
    schema_valid_count = sum(1 for r in successful if schema_valid(r["data"]))

    required_fields_present = {
        field: sum(
            1 for r in successful
            if isinstance(r["data"], dict) and field in r["data"]
        )
        for field in REQUIRED_FIELDS
    }

    summary = {
        "endpoint": ENDPOINT,
        "total_requests": total_requests,
        "successful_responses": len(successful),
        "failed_requests": total_requests - len(successful),
        "schema_valid_responses": schema_valid_count,
        "p50_latency_ms": percentile(latencies, 50),
        "p95_latency_ms": percentile(latencies, 95),
        "max_latency_ms": round(max(latencies), 2) if latencies else None,
        "health_check_success_rate": round(len(successful) / total_requests, 2),
        "required_fields_present": required_fields_present,
        "readiness_status": "PASS" if len(successful) == total_requests and schema_valid_count == total_requests else "REVIEW",
        "failed_errors": [r["error"] for r in results if r["error"]],
    }

    return summary

def main():
    summary = run_benchmark()

    out = Path("aiops_service_readiness/incident_context_benchmark_summary.json")
    out.write_text(json.dumps(summary, indent=2))

    report = f"""# AIOps Incident Context Service Readiness Report

## Endpoint

{summary["endpoint"]}

## Benchmark summary

| Metric | Value |
|---|---:|
| total_requests | {summary["total_requests"]} |
| successful_responses | {summary["successful_responses"]} |
| failed_requests | {summary["failed_requests"]} |
| schema_valid_responses | {summary["schema_valid_responses"]} |
| p50_latency_ms | {summary["p50_latency_ms"]} |
| p95_latency_ms | {summary["p95_latency_ms"]} |
| max_latency_ms | {summary["max_latency_ms"]} |
| health_check_success_rate | {summary["health_check_success_rate"]} |
| readiness_status | {summary["readiness_status"]} |

## Required fields checked

{json.dumps(summary["required_fields_present"], indent=2)}

## Operational interpretation

This benchmark validates that the live AIOps incident-context endpoint returns successful responses, required incident-context fields, and latency summaries suitable for service-readiness review.
"""

    Path("aiops_service_readiness/incident_context_service_readiness_report.md").write_text(report)

    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
