# Prometheus Metrics

AutoOps exposes Prometheus-compatible metrics at:

```text
/prometheusCustom metrics
autoops_support_incidents_total
autoops_escalations_total
autoops_agentgrid_events_ingested_total
autoops_issue_families_total
Why this matters

These metrics make AutoOps observable as an operational service rather than only an API demo. They support dashboards, alerting, SRE workflows, and internal tooling review.
