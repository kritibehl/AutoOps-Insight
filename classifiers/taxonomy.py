FAILURE_TAXONOMY = {
    "timeout": {
        "severity": "high",
        "likely_cause": "operation exceeded timeout threshold or a dependency responded too slowly",
        "first_remediation_step": "inspect the exact timed-out operation and compare recent latency trends",
        "next_debugging_action": "check downstream service latency, retries, and resource saturation",
        "probable_owner": "service-owner",
        "release_blocking": True,
    },
    "dns_failure": {
        "severity": "high",
        "likely_cause": "DNS resolution failed for an upstream dependency or service endpoint",
        "first_remediation_step": "verify resolver output and service hostname configuration",
        "next_debugging_action": "check network policy, DNS records, and environment-specific overrides",
        "probable_owner": "platform-networking",
        "release_blocking": True,
    },
    "connection_refused": {
        "severity": "high",
        "likely_cause": "target service was unavailable or not accepting connections",
        "first_remediation_step": "verify target service health and listening port availability",
        "next_debugging_action": "check rollout state, startup logs, readiness, and dependency startup order",
        "probable_owner": "service-owner",
        "release_blocking": True,
    },
    "tls_failure": {
        "severity": "high",
        "likely_cause": "TLS handshake or certificate validation failed",
        "first_remediation_step": "inspect certificate validity, trust chain, and hostname matching",
        "next_debugging_action": "compare recent certificate or endpoint changes",
        "probable_owner": "platform-security",
        "release_blocking": True,
    },
    "retry_exhausted": {
        "severity": "medium",
        "likely_cause": "operation kept failing until retry budget was exhausted",
        "first_remediation_step": "identify the first failing dependency or request in the retry chain",
        "next_debugging_action": "inspect retry policy, backoff behavior, and downstream error rates",
        "probable_owner": "service-owner",
        "release_blocking": True,
    },
    "oom": {
        "severity": "critical",
        "likely_cause": "process or container exceeded memory limits",
        "first_remediation_step": "inspect memory usage and container/resource limits",
        "next_debugging_action": "compare heap growth, object retention, and workload spikes",
        "probable_owner": "service-owner",
        "release_blocking": True,
    },
    "flaky_test_signature": {
        "severity": "medium",
        "likely_cause": "intermittent or nondeterministic test failure pattern detected",
        "first_remediation_step": "rerun the failing test with environment and timing details captured",
        "next_debugging_action": "look for race conditions, order dependence, and shared state leakage",
        "probable_owner": "qa-or-test-infra",
        "release_blocking": False,
    },
    "dependency_unavailable": {
        "severity": "high",
        "likely_cause": "required dependency or upstream service was unavailable",
        "first_remediation_step": "verify dependency health and deployment state",
        "next_debugging_action": "check service discovery, health checks, and recent infrastructure changes",
        "probable_owner": "platform-or-service-owner",
        "release_blocking": True,
    },
    "crash_loop": {
        "severity": "critical",
        "likely_cause": "service repeatedly crashed and restarted",
        "first_remediation_step": "inspect earliest crash stack trace and startup configuration",
        "next_debugging_action": "check readiness, dependency initialization, and bad startup inputs",
        "probable_owner": "service-owner",
        "release_blocking": True,
    },
    "latency_spike": {
        "severity": "medium",
        "likely_cause": "latency rose significantly above expected baseline",
        "first_remediation_step": "compare recent latency distributions against normal workload periods",
        "next_debugging_action": "inspect dependency latency, contention, and saturation signals",
        "probable_owner": "service-owner",
        "release_blocking": False,
    },
    "dependency_error": {
        "severity": "high",
        "likely_cause": "build or runtime dependency resolution failed",
        "first_remediation_step": "inspect package, artifact, or service dependency failures in the log",
        "next_debugging_action": "compare dependency versions, registry access, and environment drift",
        "probable_owner": "build-or-service-owner",
        "release_blocking": True,
    },
    "unknown": {
        "severity": "low",
        "likely_cause": "no strong known failure signature was detected",
        "first_remediation_step": "inspect the most error-dense log lines manually",
        "next_debugging_action": "capture a broader sample and add a new detection rule if this repeats",
        "probable_owner": "triage-needed",
        "release_blocking": False,
    },
}


def resolve_taxonomy(failure_family: str, rule_override: dict | None = None) -> dict:
    base = dict(FAILURE_TAXONOMY.get(failure_family, FAILURE_TAXONOMY["unknown"]))
    if rule_override:
        for key in [
            "severity",
            "likely_cause",
            "first_remediation_step",
            "next_debugging_action",
            "probable_owner",
            "release_blocking",
        ]:
            if key in rule_override:
                base[key] = rule_override[key]
    return base
