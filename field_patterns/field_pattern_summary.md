# Field Pattern Summary

## Total incidents reviewed

4

## Top recurring failure family

rag_missing_context

## Failure family distribution

{
  "rag_missing_context": 2,
  "tool_call_failure": 1,
  "unsafe_response": 1
}

## Customer blocker distribution

{
  "partner could not complete analytics export validation": 1,
  "support case required manual escalation": 1,
  "release blocked pending safety review": 1,
  "partner support could not identify workaround": 1
}

## Reusable incident patterns

[
  {
    "failure_family": "rag_missing_context",
    "count": 2,
    "common_symptoms": [
      "answer omitted partner-specific reporting constraint",
      "retrieval missed deployment-specific troubleshooting note"
    ],
    "customer_blockers": [
      "partner could not complete analytics export validation",
      "partner support could not identify workaround"
    ],
    "recommended_operational_actions": [
      "expand retrieval context and add missing-context eval case",
      "index deployment correlation docs and add retrieval-hit monitoring"
    ]
  },
  {
    "failure_family": "tool_call_failure",
    "count": 1,
    "common_symptoms": [
      "support workflow failed after external tool timeout"
    ],
    "customer_blockers": [
      "support case required manual escalation"
    ],
    "recommended_operational_actions": [
      "add retry/backoff handling and tool health checks"
    ]
  },
  {
    "failure_family": "unsafe_response",
    "count": 1,
    "common_symptoms": [
      "candidate answer bypassed safety gate"
    ],
    "customer_blockers": [
      "release blocked pending safety review"
    ],
    "recommended_operational_actions": [
      "tighten safety regression gate and require human review"
    ]
  }
]

## Operational interpretation

AutoOps converts recurring GenAI field incidents into reusable issue patterns, customer blocker summaries, and engineering-facing recommendations.
