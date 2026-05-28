from streaming_analytics.kafka_style_event_processor import EVENTS, process_events
from streaming_analytics.spark_style_batch_metrics import aggregate_batch_metrics
from streaming_analytics.incident_stream_processor import analyze_stream, SAMPLE_EVENTS

def test_kafka_style_event_processor_detects_anomalies():
    summary = process_events(EVENTS)

    assert summary["events_ingested"] == 4
    assert summary["anomaly_count"] == 3
    assert summary["stream_status"] == "PASS"

def test_spark_style_batch_metrics():
    metrics = aggregate_batch_metrics(EVENTS)

    assert metrics["batch_status"] == "PASS"
    assert metrics["batch_rows"] == 3
    assert any(row["service"] == "checkout-api" for row in metrics["aggregations"])

def test_existing_streaming_window_analysis():
    summary = analyze_stream(SAMPLE_EVENTS)

    assert summary["events_processed"] == 8
    assert summary["spike_windows_detected"] >= 1
    assert summary["escalation_bursts_detected"] >= 1
