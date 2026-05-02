# Case Study: AgentGrid → AutoOps Incident Flow

## Scenario

AgentGrid detected a missing-context failure while answering a customer query.

## Flow

AgentGrid detects missing context  
→ emits support event  
→ AutoOps ingests event  
→ AutoOps classifies issue: missing_context  
→ AutoOps infers root cause: retrieval_or_context_pipeline_failure  
→ AutoOps generates outputs  

## Outputs

### PM Summary
Customer response quality degraded due to missing context.

### Engineering Bug Report
Investigate retrieval pipeline and context assembly for this workflow.

### Support Action Plan
Fix retrieval pipeline and provide workaround or escalation path to affected users.

## Why this matters

Converts runtime AI failures into structured product, engineering, and support actions instead of isolated logs.
