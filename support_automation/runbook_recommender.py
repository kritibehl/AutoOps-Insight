ISSUE_FAMILIES = {
    "api_timeout": "latency_or_timeout",
    "slow_query": "database_performance",
    "missing_report": "reporting_pipeline_failure",
    "auth_error": "authentication_or_permissions",
    "data_mismatch": "data_quality_or_sync",
    "deployment_regression": "release_regression",
}

RUNBOOK_ACTIONS = {
    "latency_or_timeout": "Check recent deploys, upstream latency, timeout budgets, and dependency health.",
    "database_performance": "Inspect slow queries, indexes, locks, and recent schema/query changes.",
    "reporting_pipeline_failure": "Verify ingestion jobs, report generation workflow, and upstream data availability.",
    "authentication_or_permissions": "Validate credentials, IAM/role permissions, token expiry, and auth-service health.",
    "data_quality_or_sync": "Compare source-of-truth records, sync lag, validation failures, and schema drift.",
    "release_regression": "Review deployment diff, recent config changes, rollback criteria, and error-rate deltas.",
}

def classify_issue_family(issue_type: str) -> str:
    return ISSUE_FAMILIES.get(issue_type, "general_operational_issue")

def recommend_runbook_action(issue_family: str) -> str:
    return RUNBOOK_ACTIONS.get(
        issue_family,
        "Collect logs, confirm customer impact, check recent changes, and route to service owner."
    )
