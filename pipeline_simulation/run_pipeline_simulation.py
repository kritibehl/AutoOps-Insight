import json
from pathlib import Path
from statistics import mean

RAW_EVENTS = [
    {"event_id": "evt-001", "service": "checkout-api", "region": "us-west", "latency_ms": 4200, "error_rate": 8.4, "event_type": "latency_spike"},
    {"event_id": "evt-002", "service": "checkout-api", "region": "us-west", "latency_ms": 3900, "error_rate": 7.1, "event_type": "retry_spike"},
    {"event_id": "evt-003", "service": "payment-api", "region": "us-west", "latency_ms": 3100, "error_rate": 5.5, "event_type": "dependency_timeout"},
    {"event_id": "evt-004", "service": "search-api", "region": "us-east", "latency_ms": 180, "error_rate": 0.2, "event_type": "normal"}
]


def ingest(events):
    return {
        "stage": "ingest",
        "records_received": len(events),
        "records_valid": len([e for e in events if "event_id" in e and "service" in e]),
        "records": events,
    }


def aggregate(records):
    services = sorted({r["service"] for r in records})
    rows = []

    for service in services:
        service_records = [r for r in records if r["service"] == service]
        rows.append({
            "service": service,
            "event_count": len(service_records),
            "avg_latency_ms": round(mean(r["latency_ms"] for r in service_records), 2),
            "avg_error_rate": round(mean(r["error_rate"] for r in service_records), 2),
        })

    return {
        "stage": "aggregate",
        "group_by": ["service"],
        "rows": rows,
    }


def warehouse(aggregates):
    return {
        "stage": "warehouse",
        "target_tables": [
            "fact_operational_event",
            "fact_service_health_daily",
            "dim_service",
            "dim_region",
        ],
        "warehouse_rows_ready": len(aggregates["rows"]),
        "rows": aggregates["rows"],
    }


def detect_anomalies(aggregates):
    anomalies = [
        {
            **row,
            "anomaly_reason": "latency_or_error_rate_threshold"
        }
        for row in aggregates["rows"]
        if row["avg_latency_ms"] > 3000 or row["avg_error_rate"] > 5
    ]

    return {
        "stage": "anomaly_detection",
        "anomaly_count": len(anomalies),
        "anomalies": anomalies,
    }


def dashboard(warehouse_output, anomaly_output):
    return {
        "stage": "dashboard",
        "dashboard_tiles": [
            "service_health_summary",
            "regional_latency_trends",
            "anomaly_count",
            "top_impacted_services",
        ],
        "services_visible": [row["service"] for row in warehouse_output["rows"]],
        "anomaly_count": anomaly_output["anomaly_count"],
    }


def run_pipeline(events):
    ingested = ingest(events)
    aggregated = aggregate(ingested["records"])
    warehouse_output = warehouse(aggregated)
    anomaly_output = detect_anomalies(aggregated)
    dashboard_output = dashboard(warehouse_output, anomaly_output)

    return {
        "pipeline_status": "PASS",
        "stages": [
            ingested,
            aggregated,
            warehouse_output,
            anomaly_output,
            dashboard_output,
        ],
        "summary": {
            "records_received": ingested["records_received"],
            "records_valid": ingested["records_valid"],
            "warehouse_rows_ready": warehouse_output["warehouse_rows_ready"],
            "anomaly_count": anomaly_output["anomaly_count"],
            "dashboard_tiles": len(dashboard_output["dashboard_tiles"]),
        }
    }


def main():
    output = run_pipeline(RAW_EVENTS)

    Path("pipeline_simulation/pipeline_output.json").write_text(
        json.dumps(output, indent=2)
    )

    report = f"""# Distributed Analytics Pipeline Simulation

## Pipeline stages

1. ingest
2. aggregate
3. warehouse
4. anomaly detection
5. dashboard

## Summary

- records_received: {output["summary"]["records_received"]}
- records_valid: {output["summary"]["records_valid"]}
- warehouse_rows_ready: {output["summary"]["warehouse_rows_ready"]}
- anomaly_count: {output["summary"]["anomaly_count"]}
- dashboard_tiles: {output["summary"]["dashboard_tiles"]}

## Operational value

This simulation models an end-to-end operational telemetry pipeline from event ingestion through aggregation, warehouse-ready outputs, anomaly detection, and dashboard-facing summaries.
"""

    Path("pipeline_simulation/pipeline_report.md").write_text(report)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
