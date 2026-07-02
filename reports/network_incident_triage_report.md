# Network Incident Triage Report

## Summary

- Network incidents reviewed: 3
- Triage status: PASS

## Triage table

| Incident | Failure family | Severity | Affected service | SLO impact |
|---|---|---|---|---|
| NET-301 | dns_resolution_failure | sev2 | checkout-api | medium |
| NET-302 | tcp_timeout | sev1 | partner-reporting-api | high |
| NET-303 | tls_handshake_failure | sev2 | agentgrid | medium |

## Supported failure families

- connection_refused
- dns_resolution_failure
- http_5xx_spike
- packet_loss
- routing_or_reachability_issue
- tcp_timeout
- tls_handshake_failure

## Operational value

This report classifies network-style incidents, estimates severity from SLO impact, recommends first diagnostic commands, and routes incidents through support/SRE/NPE escalation paths.
