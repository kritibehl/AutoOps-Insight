# Anomaly Detection Report

## Summary

AutoOps models operational telemetry ingestion and batch aggregation for monitoring workflows.

## Detected anomaly types

- latency spike
- retry spike
- dependency timeout
- elevated error rate

## Monitoring interpretation

The highest-risk service is `checkout-api`, with repeated high-latency and retry-spike events in the same region. These events should be routed into service-health dashboards and incident-response workflows.

## Data engineering value

This workflow demonstrates streaming ingestion, batch aggregation, anomaly detection, and monitoring-ready telemetry outputs.
