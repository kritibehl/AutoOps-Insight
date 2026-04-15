from __future__ import annotations

def classify_root_cause(text: str, failure_family: str) -> str:
    t = text.lower()

    if failure_family == "dns_failure":
        return "service_discovery_or_dns_misconfiguration"
    if failure_family == "timeout":
        if "registry" in t:
            return "artifact_registry_connectivity_or_latency"
        if "deploy" in t:
            return "deployment_path_latency_or_dependency_timeout"
        return "dependency_latency_or_unresponsive_service"
    if "certificate" in t or "tls" in t:
        return "tls_or_certificate_failure"
    if "connection refused" in t:
        return "service_unreachable_or_listener_down"
    if "oom" in t or "out of memory" in t:
        return "resource_exhaustion"
    return "unknown_or_mixed_failure"
