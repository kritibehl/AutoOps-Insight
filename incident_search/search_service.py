INCIDENTS = [
    {
        "incident_id": "INC-1001",
        "service": "reporting-api",
        "owner": "reporting_platform_team",
        "severity": "medium",
        "issue_family": "latency_or_timeout",
        "status": "triaged",
        "created_at": "2026-05-10T10:00:00Z",
        "action": "monitor dependency latency and update customer",
        "timeline": [
            {"state": "new", "timestamp": "2026-05-10T10:00:00Z"},
            {"state": "triaged", "timestamp": "2026-05-10T10:42:00Z"}
        ]
    },
    {
        "incident_id": "INC-1002",
        "service": "agentgrid",
        "owner": "platform_runtime_team",
        "severity": "high",
        "issue_family": "tool_failure",
        "status": "escalated",
        "created_at": "2026-05-10T08:30:00Z",
        "action": "engineering escalation for tool dependency failure",
        "timeline": [
            {"state": "new", "timestamp": "2026-05-10T08:30:00Z"},
            {"state": "triaged", "timestamp": "2026-05-10T08:55:00Z"},
            {"state": "escalated", "timestamp": "2026-05-10T09:20:00Z"}
        ]
    },
    {
        "incident_id": "INC-1003",
        "service": "agentgrid",
        "owner": "safety_review_team",
        "severity": "critical",
        "issue_family": "unsafe_response",
        "status": "escalated",
        "created_at": "2026-05-10T07:00:00Z",
        "action": "safety owner review before release",
        "timeline": [
            {"state": "new", "timestamp": "2026-05-10T07:00:00Z"},
            {"state": "triaged", "timestamp": "2026-05-10T07:10:00Z"},
            {"state": "escalated", "timestamp": "2026-05-10T07:25:00Z"}
        ]
    },
    {
        "incident_id": "INC-1004",
        "service": "faireval",
        "owner": "evaluation_platform_team",
        "severity": "medium",
        "issue_family": "retrieval_failure",
        "status": "resolved",
        "created_at": "2026-05-10T09:15:00Z",
        "action": "document regression pattern and close",
        "timeline": [
            {"state": "new", "timestamp": "2026-05-10T09:15:00Z"},
            {"state": "triaged", "timestamp": "2026-05-10T10:05:00Z"},
            {"state": "resolved", "timestamp": "2026-05-10T14:15:00Z"}
        ]
    }
]

def search_incidents(
    service: str | None = None,
    owner: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    issue_family: str | None = None,
):
    results = INCIDENTS

    filters = {
        "service": service,
        "owner": owner,
        "severity": severity,
        "status": status,
        "issue_family": issue_family,
    }

    for key, value in filters.items():
        if value:
            results = [item for item in results if item.get(key) == value]

    return {
        "count": len(results),
        "filters": {k: v for k, v in filters.items() if v},
        "items": results,
    }

def service_owner_summary():
    summary = {}
    for incident in INCIDENTS:
        owner = incident["owner"]
        summary.setdefault(owner, {
            "owner": owner,
            "incident_count": 0,
            "open_count": 0,
            "critical_or_high": 0,
            "services": set(),
        })
        summary[owner]["incident_count"] += 1
        summary[owner]["services"].add(incident["service"])
        if incident["status"] != "resolved":
            summary[owner]["open_count"] += 1
        if incident["severity"] in {"high", "critical"}:
            summary[owner]["critical_or_high"] += 1

    return [
        {
            **v,
            "services": sorted(v["services"]),
        }
        for v in summary.values()
    ]
