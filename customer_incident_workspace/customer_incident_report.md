# Customer Incident Workspace

## Customer

enterprise_account

## Service

checkout-api

## Issue

latency spike after release

## Severity

sev2

## Suspected cause

deployment_regression

## Evidence

- p95 +240%
- error_rate +3.2%
- release_id matched
- retry spike detected

## Recommended action

rollback_candidate

## Customer-safe summary

checkout-api is showing elevated latency after release-204. The incident is under engineering review and rollback readiness is being evaluated.

## Engineering follow-up

- compare release-204 diff against latency spike window
- review retry budget and dependency saturation
- prepare rollback review if customer impact persists

## Operational value

This workspace converts customer-facing incident symptoms into support-ready severity, evidence, suspected cause, recommended action, customer-safe language, and engineering follow-up.
