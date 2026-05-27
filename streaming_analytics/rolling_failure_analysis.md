# Rolling Failure Analysis

## Summary

- Events processed: 8
- Window size: 3
- Spike windows detected: 6
- Escalation bursts detected: 6

## Top services

{
  "checkout-api": 5,
  "payment-api": 2,
  "search-api": 1
}

## Top issue families

{
  "latency_spike": 5,
  "dependency_timeout": 2,
  "tool_failure": 1
}

## Operational interpretation

The stream processor detects rolling failure spikes, recurring issue-family surges, escalation bursts, and moving-average escalation trends from structured incident telemetry.
