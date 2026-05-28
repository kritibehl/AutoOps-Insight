import json
from pathlib import Path
from collections import Counter

EVENTS = [
    {"event_id": "k-001", "service": "checkout-api", "event_type": "latency_spike", "latency_ms": 4200, "error_rate": 8.4, "region": "us-west", "timestamp": "2026-05-16T14:00:00Z"},
    {"event_id": "k-002", "service": "checkout-api", "event_type": "retry_spike", "latency_ms": 3900, "error_rate": 7.1, "region": "us-west", "timestamp": "2026-05-16T14:01:00Z"},
    {"event_id": "k-003", "service": "payment-api", "event_type": "dependency_timeout", "latency_ms": 3100, "error_rate": 5.5, "region": "us-west", "timestamp": "2026-05-16T14:02:00Z"},
    {"event_id": "k-004", "service": "search-api", "event_type": "normal", "latency_ms": 180, "error_rate": 0.2, "region": "us-east", "timestamp": "2026-05-16T14:03:00Z"}
]

def process_events(events):
    service_counts = Counter(e["service"] for e in events)
    event_type_counts = Counter(e["event_type"] for e in events)
    anomalies = [
        e for e in events
        if e["latency_ms"] > 3000 or e["error_rate"] > 5
    ]

    return {
        "events_ingested": len(events),
        "service_counts": dict(service_counts),
        "event_type_counts": dict(event_type_counts),
        "anomaly_count": len(anomalies),
        "anomalies": anomalies,
        "stream_status": "PASS"
    }

def main():
    summary = process_events(EVENTS)
    Path("streaming_analytics/kafka_event_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
