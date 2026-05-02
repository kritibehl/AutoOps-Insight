import argparse
import json
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path("autoops.db")

REPOS = ["kubepulse", "faultline", "faireval", "dettrace", "agentgrid"]
ISSUE_FAMILIES = [
    "wrong_answer",
    "missing_context",
    "tool_failure",
    "retrieval_failure",
    "latency_spike",
    "unsafe_response",
]

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
                support_action_plan TEXT
            )
            """
        )
        conn.commit()

def signature(issue_family, customer_id):
    return f"{issue_family}:{customer_id[-2:]}"

def stakeholder_outputs(issue_family, root_cause, action, recurrence):
    pm = f"{issue_family} appeared {recurrence} time(s); potential customer-impact risk if repeated."
    eng = f"Investigate {issue_family}; likely cause: {root_cause}. Check recent changes and related telemetry."
    support = f"Recommended support action: {action}. Provide workaround if available and attach incident signature."
    return pm, eng, support

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=100)
    args = parser.parse_args()

    init_db()

    now = datetime.utcnow()
    inserted = []

    with sqlite3.connect(DB_PATH) as conn:
        for i in range(args.count):
            source = random.choice(REPOS)
            issue = random.choice(ISSUE_FAMILIES)
            customer_id = f"cust_{random.randint(1000, 1025)}"
            sig = signature(issue, customer_id)

            prior = conn.execute(
                "SELECT COUNT(*) FROM support_incidents WHERE signature = ?",
                (sig,),
            ).fetchone()[0]
            recurrence = prior + 1

            root_cause = ROOT_CAUSES[issue]
            action = ACTIONS[issue]
            confidence = round(random.uniform(0.72, 0.96), 2)
            escalation = 1 if issue in {"unsafe_response", "tool_failure"} or recurrence >= 3 else 0
            created_at = (now - timedelta(minutes=random.randint(0, 1440))).isoformat()

            pm, eng, support = stakeholder_outputs(issue, root_cause, action, recurrence)

            conn.execute(
                """
                INSERT INTO support_incidents (
                    created_at, source, customer_id, issue_family, signature,
                    recurrence_total, confidence, root_cause, action,
                    escalation_required, pm_summary, engineering_bug_report,
                    support_action_plan
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    created_at, source, customer_id, issue, sig, recurrence,
                    confidence, root_cause, action, escalation, pm, eng, support
                ),
            )

            inserted.append({
                "source": source,
                "issue_family": issue,
                "signature": sig,
                "recurrence_total": recurrence,
                "action": action,
                "escalation_required": bool(escalation),
            })

        conn.commit()

    print(json.dumps({
        "generated": len(inserted),
        "sources": sorted(set(x["source"] for x in inserted)),
        "issue_families": sorted(set(x["issue_family"] for x in inserted)),
        "escalations": sum(1 for x in inserted if x["escalation_required"]),
        "sample": inserted[:5],
    }, indent=2))

if __name__ == "__main__":
    main()
