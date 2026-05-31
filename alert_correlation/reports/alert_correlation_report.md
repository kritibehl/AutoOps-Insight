# Alert Correlation Report

## Summary

- Alerts received: 4
- Incident families detected: 2
- Correlation status: PASS

## Incident families

[
  {
    "incident_family": "service_degradation",
    "alert_count": 3,
    "services": [
      "checkout-api",
      "payment-api"
    ],
    "severities": [
      "sev1",
      "sev2"
    ],
    "alert_types": [
      "dependency_failure",
      "latency_spike",
      "retry_storm"
    ],
    "recommended_review": "open sev1 incident review"
  },
  {
    "incident_family": "incident_escalation",
    "alert_count": 1,
    "services": [
      "checkout-api"
    ],
    "severities": [
      "sev1"
    ],
    "alert_types": [
      "escalation_burst"
    ],
    "recommended_review": "monitor"
  }
]

## Operational value

This workflow groups latency spikes, retry storms, dependency failures, and escalation bursts into incident families for operational review.
