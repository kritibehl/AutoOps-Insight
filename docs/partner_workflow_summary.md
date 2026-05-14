# Partner Workflow Summary

## Workflow

Partner integrations use reporting-api endpoints to export operational analytics into downstream dashboards and reporting pipelines.

## Operational flow

1. Partner submits analytics export request.
2. reporting-api validates request metadata.
3. AutoOps monitors service health and deployment state.
4. Export job is processed and tracked.
5. Support escalation workflows trigger if failures or SLA breaches occur.

## Common support scenarios

| Scenario | Operational response |
|---|---|
| API timeout | review deployment correlation and retry behavior |
| delayed reporting | inspect queue latency and retry backlog |
| unsafe response | escalate to safety review |
| repeated failures | trigger recurrence analysis and rollback review |

## Teams involved

- support_l1
- service_owner
- platform_runtime_team
- analytics_partner_support

## Operational review artifacts

- SLA summaries
- escalation reports
- deployment-risk dashboards
- RCA workflows
- service-owner dashboards
