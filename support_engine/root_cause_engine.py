from support_engine.issue_taxonomy import ISSUE_TYPES, ROOT_CAUSES

def classify_issue(text: str):
    t = text.lower()

    if "wrong answer" in t or "incorrect" in t:
        return "wrong_answer"
    if "slow" in t or "timeout" in t:
        return "slow_response"
    if "missing context" in t:
        return "missing_context"
    if "tool failed" in t:
        return "tool_failure"
    if "retrieval" in t:
        return "bad_retrieval"
    if "escalate" in t or "complaint" in t:
        return "user_escalation"

    return "unknown"

def infer_root_cause(issue_type):
    return ROOT_CAUSES.get(issue_type, "unknown")

def recommend_action(issue_type):
    mapping = {
        "wrong_answer": "review_prompt_and_model_behavior",
        "slow_response": "optimize_latency_and_infra",
        "missing_context": "fix_retrieval_pipeline",
        "tool_failure": "check_tool_dependencies",
        "bad_retrieval": "tune_embeddings_and_search",
        "user_escalation": "escalate_to_support_and_engineering"
    }
    return mapping.get(issue_type, "investigate")

def generate_summary(issue_type, root_cause):
    return f"Issue detected: {issue_type}. Likely cause: {root_cause}."
