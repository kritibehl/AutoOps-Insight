from __future__ import annotations

RUNBOOKS = {
    "dns_failure": (
        "Verify resolver output, check service hostname configuration, inspect recent DNS or service-discovery changes, "
        "and validate environment-specific overrides.",
        0.91,
    ),
    "timeout": (
        "Inspect the timed-out operation, compare recent latency trends, check downstream service health, retries, "
        "resource saturation, and deploy-path connectivity.",
        0.89,
    ),
    "dependency_latency": (
        "Check downstream latency percentiles, recent deploys, retry amplification, and resource contention.",
        0.86,
    ),
    "service_unreachable": (
        "Confirm service endpoints are healthy, verify network reachability, and inspect listener or ingress status.",
        0.88,
    ),
}

def get_runbook(failure_family: str) -> tuple[str, float]:
    return RUNBOOKS.get(
        failure_family,
        ("Start with the first failing step, validate the dependency path, inspect recent changes, and compare against the last known good run.", 0.62),
    )
