# AutoOps Role Matrix

| Role | Ingest Incident | Read Reports | Escalate | Suppress | Resolve | Admin |
|---|---:|---:|---:|---:|---:|---:|
| support_l1 | yes | yes | no | no | no | no |
| service_owner | yes | yes | yes | yes | yes | no |
| admin | yes | yes | yes | yes | yes | yes |

## Purpose

AutoOps uses role-aware support workflows to separate basic support triage from service-owner escalation and admin-level operational controls.

## Operational meaning

- `support_l1`: can ingest incidents and review reports.
- `service_owner`: can escalate, suppress, and resolve incidents for owned services.
- `admin`: can perform all operational actions.
