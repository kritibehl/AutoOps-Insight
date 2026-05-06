# AgentGrid → AutoOps Integration

AgentGrid acts as the GenAI support decision layer.

AutoOps acts as the incident intelligence and release-risk layer.

## Flow

```text
AgentGrid detects unsafe or uncertain GenAI behavior
  ↓
Decision is hold or escalate
  ↓
AgentGrid emits structured event
  ↓
AutoOps ingests incident
  ↓
AutoOps generates:
  - root cause
  - PM summary
  - engineering bug report
  - support action
  - recurrence signal
  - release-risk summary
Example event
{
  "source": "agentgrid",
  "scenario": "conflicting_evidence",
  "decision": "escalate",
  "reason": "retrieved evidence conflicts across sources",
  "support_action": "route to product/support reviewer",
  "engineering_bug_report": "retrieval ranking returned inconsistent evidence"
}
Why this matters

The combined system demonstrates a production-style GenAI support workflow:

AgentGrid decides when AI should not answer directly.
AutoOps turns that decision into support and engineering follow-up.
The dashboard exposes support metrics and escalation behavior.
