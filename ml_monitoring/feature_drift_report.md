# ML Feature Drift Report

## Summary

- Models monitored: 3
- Healthy models: 1
- Degraded models: 2
- Feature drift alerts: 2
- Quality regressions: 2
- Latency regressions: 2

## Model-level drift review

- support-priority-classifier: health=degraded, drifted_features=['ticket_length', 'customer_region'], accuracy_drop=0.07
- incident-routing-model: health=healthy, drifted_features=[], accuracy_drop=0.01
- runbook-recommendation-model: health=degraded, drifted_features=['incident_family'], accuracy_drop=0.07

## Operational interpretation

AutoOps tracks model-health signals for support and incident workflows, including feature drift, prediction-quality regression, latency regression, and dashboard-ready model status summaries.
