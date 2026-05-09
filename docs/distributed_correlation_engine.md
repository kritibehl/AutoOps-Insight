# Distributed Incident Correlation Engine

AutoOps correlates incident signals across AgentGrid, AutoOps, FairEval, and CI-style systems by trace ID.

## What it does

- groups events by trace ID
- summarizes affected sources
- detects escalation / release-hold actions
- ranks likely root causes using issue severity, recurrence, and escalation signals
- produces correlation reports for incident review

## Example

AgentGrid emits a missing-context event.  
AutoOps links it with retrieval failure and wrong-answer signals.  
The correlation engine ranks `retrieval_or_context_pipeline_failure` as the top root cause.

## Why this matters

This turns isolated support/CI events into a cross-system incident timeline, which is closer to real production debugging and incident reconstruction workflows.
