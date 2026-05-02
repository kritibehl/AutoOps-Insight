import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("autoops.db")

ROOT_CAUSES = {
    "wrong_answer": "model_reasoning_or_prompt_issue",
    "missing_context": "retrieval_or_context_pipeline_failure",
    "tool_failure": "external_tool_or_api_error",
    "retrieval_failure": "vector_search_or_embedding_issue",
    "latency_spike": "latency_or_infrastructure_bottleneck",
    "unsafe_response": "safety_policy_or_guardrail_gap",
}

ACTIONS = {
    "wrong_answer": "support_review",
    "missing_context": "fix_retrieval_pipeline",
    "tool_failure": "check_tool_dependency",
    "retrieval_failure": "tune_search_and_embeddings",
    "latency_spike": "hold_release",
    "unsafe_response": "escalate_to_safety_review",
}

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS support_incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT,
                source TEXT,
                customer_id TEXT,
                issue_family TEXT,
                signature TEXT,
                recurrence_total INTEGER,
                confidence REAL,
                root_cause TEXT,
                action TEXT,
                escalation_required INTEGER,
                pm_summary TEXT,
                engineering_bug_report TEXT,
                support_action_plan TEXT,
                agent_decision TEXT,
                trace_id TEXT,
                workflow TEXT,
                severity TEXT
            )
            """
        )

        existing_cols = {
            row[1] for row in conn.execute("PRAGMA table_info(support_incidents)").fetchall()
        }
        for col, typ in {
            "agent_decision": "TEXT",
            "trace_id": "TEXT",
            "workflow": "TEXT",
            "severity": "TEXT",
        }.items():
            if col not in existing_cols:
                conn.execute(f"ALTER TABLE support_incidents ADD COLUMN {col} {typ}")
        conn.commit()

def recurrence(conn, signature):
    prior = conn.execute(
        "SELECT COUNT(*) FROM support_incidents WHERE signature = ?",
        (signature,),
    ).fetchone()[0]
    return prior + 1

def stakeholder_outputs(event, root_cause, action, recurrence_total):
    issue = event["issue_family"]
    trace = event.get("trace_id", "unknown_trace")

    pm = (
        f"AgentGrid reported {issue} in workflow {event.get('workflow')}; "
        f"recurrence={recurrence_total}. Product risk: customer answer quality or completion may be degraded."
    )
    eng = (
        f"Bug report: AgentGrid trace {trace} classified as {issue}. "
        f"Likely cause: {root_cause}. Investigate retrieval/tool path and recent changes."
    )
    support = (
        f"Support action: {action}. Reference trace {trace}, acknowledge the issue, "
        "and provide workaround or escalation path if customer is blocked."
    )
    return pm, eng, support

def ingest_event(path: Path):
    event = json.loads(path.read_text())
    init_db()

    issue = event["issue_family"]
    customer_id = event["customer_id"]
    signature = f"agentgrid:{issue}:{customer_id}"
    root_cause = ROOT_CAUSES.get(issue, "unknown")
    action = ACTIONS.get(issue, "investigate")
    if event.get("agent_decision") == "escalate":
        escalation_required = 1
    else:
        escalation_required = 1 if issue in {"unsafe_response", "tool_failure"} else 0

    with sqlite3.connect(DB_PATH) as conn:
        rec = recurrence(conn, signature)
        pm, eng, support = stakeholder_outputs(event, root_cause, action, rec)

        conn.execute(
            """
            INSERT INTO support_incidents (
                created_at, source, customer_id, issue_family, signature,
                recurrence_total, confidence, root_cause, action, escalation_required,
                pm_summary, engineering_bug_report, support_action_plan,
                agent_decision, trace_id, workflow, severity
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.utcnow().isoformat(),
                event.get("source", "agentgrid"),
                customer_id,
                issue,
                signature,
                rec,
                0.93 if event.get("agent_decision") == "escalate" else 0.88,
                root_cause,
                action,
                escalation_required,
                pm,
                eng,
                support,
                event.get("agent_decision"),
                event.get("trace_id"),
                event.get("workflow"),
                event.get("severity"),
            ),
        )
        conn.commit()

    return {
        "source": event.get("source", "agentgrid"),
        "issue_family": issue,
        "agent_decision": event.get("agent_decision"),
        "signature": signature,
        "recurrence_total": rec,
        "action": action,
        "escalation_required": bool(escalation_required),
        "pm_summary": pm,
        "engineering_bug_report": eng,
        "support_action_plan": support,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()

    results = [ingest_event(Path(p)) for p in args.paths]
    print(json.dumps({"ingested": len(results), "items": results}, indent=2))

if __name__ == "__main__":
    main()
