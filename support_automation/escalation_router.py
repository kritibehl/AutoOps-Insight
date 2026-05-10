OWNER_MAP = {
    "reporting-api": "reporting_platform_team",
    "ads-billing": "ads_billing_services",
    "auth-service": "identity_platform_team",
    "data-sync": "data_platform_team",
    "workflow-engine": "platform_runtime_team",
}

def probable_owner(service: str, issue_family: str) -> str:
    if service in OWNER_MAP:
        return OWNER_MAP[service]
    if issue_family == "database_performance":
        return "database_platform_team"
    if issue_family == "release_regression":
        return "release_engineering_team"
    return "support_operations_team"

def escalation_path(severity: str, issue_family: str) -> list[str]:
    severity = severity.lower()
    path = ["support_l1_triage"]

    if severity in {"medium", "high", "critical"}:
        path.append("service_owner_review")

    if severity in {"high", "critical"} or issue_family in {"release_regression", "latency_or_timeout"}:
        path.append("engineering_escalation")

    if severity == "critical":
        path.append("incident_commander")

    return path
