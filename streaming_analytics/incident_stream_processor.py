import json
from collections import Counter, defaultdict, deque
from pathlib import Path

SAMPLE_EVENTS = [
    {"timestamp": "2026-05-16T14:00:00Z", "service": "checkout-api", "issue_family": "latency_spike", "severity": "sev2", "escalated": False},
    {"timestamp": "2026-05-16T14:01:00Z", "service": "checkout-api", "issue_family": "latency_spike", "severity": "sev1", "escalated": True},
    {"timestamp": "2026-05-16T14:02:00Z", "service": "checkout-api", "issue_family": "latency_spike", "severity": "sev1", "escalated": True},
    {"timestamp": "2026-05-16T14:03:00Z", "service": "payment-api", "issue_family": "dependency_timeout", "severity": "sev2", "escalated": False},
    {"timestamp": "2026-05-16T14:04:00Z", "service": "checkout-api", "issue_family": "latency_spike", "severity": "sev1", "escalated": True},
    {"timestamp": "2026-05-16T14:05:00Z", "service": "payment-api", "issue_family": "dependency_timeout", "severity": "sev1", "escalated": True},
    {"timestamp": "2026-05-16T14:06:00Z", "service": "search-api", "issue_family": "tool_failure", "severity": "sev3", "escalated": False},
    {"timestamp": "2026-05-16T14:07:00Z", "service": "checkout-api", "issue_family": "latency_spike", "severity": "sev1", "escalated": True}
]

def analyze_stream(events, window_size=3):
    rolling_window = deque(maxlen=window_size)
    window_metrics = []
    service_counts = Counter()
    family_counts = Counter()
    escalation_bursts = []
    spike_windows = []

    for idx, event in enumerate(events):
        rolling_window.append(event)
        service_counts[event["service"]] += 1
        family_counts[event["issue_family"]] += 1

        window_services = Counter(e["service"] for e in rolling_window)
        window_families = Counter(e["issue_family"] for e in rolling_window)
        escalations = sum(1 for e in rolling_window if e["escalated"])
        sev1_count = sum(1 for e in rolling_window if e["severity"] == "sev1")

        metric = {
            "window_index": idx,
            "window_size": len(rolling_window),
            "dominant_service": window_services.most_common(1)[0][0],
            "dominant_issue_family": window_families.most_common(1)[0][0],
            "sev1_count": sev1_count,
            "escalation_count": escalations,
            "moving_avg_escalations": round(escalations / len(rolling_window), 2),
            "spike_detected": sev1_count >= 2 or escalations >= 2,
        }

        if metric["spike_detected"]:
            spike_windows.append(metric)

        if escalations >= 2:
            escalation_bursts.append(metric)

        window_metrics.append(metric)

    return {
        "events_processed": len(events),
        "window_size": window_size,
        "spike_windows_detected": len(spike_windows),
        "escalation_bursts_detected": len(escalation_bursts),
        "top_services": dict(service_counts),
        "top_issue_families": dict(family_counts),
        "window_metrics": window_metrics,
        "spike_windows": spike_windows,
        "escalation_bursts": escalation_bursts,
        "stream_status": "PASS",
    }

def main():
    summary = analyze_stream(SAMPLE_EVENTS)

    Path("streaming_analytics/stream_window_metrics.json").write_text(
        json.dumps(summary, indent=2)
    )

    report = f"""# Rolling Failure Analysis

## Summary

- Events processed: {summary["events_processed"]}
- Window size: {summary["window_size"]}
- Spike windows detected: {summary["spike_windows_detected"]}
- Escalation bursts detected: {summary["escalation_bursts_detected"]}

## Top services

{json.dumps(summary["top_services"], indent=2)}

## Top issue families

{json.dumps(summary["top_issue_families"], indent=2)}

## Operational interpretation

The stream processor detects rolling failure spikes, recurring issue-family surges, escalation bursts, and moving-average escalation trends from structured incident telemetry.
"""

    Path("streaming_analytics/rolling_failure_analysis.md").write_text(report)

    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
