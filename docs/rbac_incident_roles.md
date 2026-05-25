# AutoOps RBAC Roles

| Role | Permissions |
|---|---|
| admin | all actions |
| incident_manager | create, assign, transition, close |
| support_agent | create, triage, comment |
| engineer | assign, mitigate, resolve |
| viewer | read-only |

## Protected Actions

- ingest event
- process event
- view DLQ
- assign incident
- transition incident
- close incident
- view RCA analytics

## Scope

This is a role-design artifact for incident automation workflows, not production identity infrastructure.
