import json
from pathlib import Path
from statistics import mean

from streaming_analytics.kafka_style_event_processor import EVENTS

def aggregate_batch_metrics(events):
    services = sorted({e["service"] for e in events})
    rows = []

    for service in services:
        service_events = [e for e in events if e["service"] == service]
        rows.append({
            "service": service,
            "event_count": len(service_events),
            "avg_latency_ms": round(mean(e["latency_ms"] for e in service_events), 2),
            "avg_error_rate": round(mean(e["error_rate"] for e in service_events), 2),
            "anomaly_events": sum(1 for e in service_events if e["latency_ms"] > 3000 or e["error_rate"] > 5)
        })

    return {
        "batch_rows": len(rows),
        "aggregations": rows,
        "batch_status": "PASS"
    }

def main():
    metrics = aggregate_batch_metrics(EVENTS)
    Path("streaming_analytics/batch_metrics_summary.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()
