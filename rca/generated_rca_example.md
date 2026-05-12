# Incident RCA — agentgrid Release Risk

## Incident ID

RCA-DEP-1002

## Summary

AutoOps correlated deployment `DEP-1002` for `agentgrid` with a post-release incident spike. The release was marked as `high` risk and rollback_candidate=true.

## Probable cause

tool routing change introduced failures in AgentGrid support workflow and increased unsafe-response risk shortly after deployment

## Impacted services

- agentgrid
- support_workflow
- tool_routing

## Timeline

| Timestamp | Event |
|---|---|
| 2026-05-10T07:45:00Z | Deployment DEP-1002 completed for agentgrid v1.8.0 |
| 2026-05-10T08:05:00Z | Tool-failure incident INC-2003 detected 20 minutes after deployment |
| 2026-05-10T08:20:00Z | Unsafe-response incident INC-2004 detected 35 minutes after deployment |
| 2026-05-10T08:25:00Z | AutoOps marked release as high risk and rollback candidate |
| 2026-05-10T08:30:00Z | Service owner escalation routed to platform_runtime_team |

## Rollback candidate

True

## Release risk

high

## Next actions

1. review DEP-1002 tool routing diff
2. hold release until tool-failure and unsafe-response patterns are resolved
3. route to platform_runtime_team for service-owner review
4. add regression coverage for tool routing and unsafe-response paths
5. update support runbook with rollback criteria
