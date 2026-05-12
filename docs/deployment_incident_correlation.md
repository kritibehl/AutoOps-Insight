# Deployment-to-Incident Correlation

AutoOps correlates deployment events with post-release incident spikes.

## Inputs

- deployment event
- service name
- deployment timestamp
- change type
- service owner
- incident timestamp
- severity
- customer impact

## Outputs

- affected service
- incident spike count
- severity score
- rollback candidate
- release-risk attribution
- related incidents
- recommended actions

## Why this matters

This workflow helps operators identify whether a deployment likely triggered a spike in incidents and whether the release should be held, reviewed, or rolled back.

## Example

Deployment `DEP-1002` for AgentGrid is followed by tool-failure and unsafe-response incidents within the correlation window. AutoOps marks the deployment as a rollback candidate and attributes risk to the affected service.
