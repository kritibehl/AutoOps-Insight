from __future__ import annotations

INCIDENT_TAXONOMY = {
    "dns": {
        "display_name": "DNS resolution failure",
        "symptoms": ["no such host", "dns lookup failed", "name resolution", "servfail", "nxdomain"],
        "escalation_route": "service-owner -> platform-networking -> dns/platform team",
    },
    "tcp_connect_timeout": {
        "display_name": "TCP connect timeout",
        "symptoms": ["connect timeout", "connection timed out", "dial tcp", "i/o timeout"],
        "escalation_route": "service-owner -> platform-networking",
    },
    "tls_handshake": {
        "display_name": "TLS handshake failure",
        "symptoms": ["tls handshake timeout", "x509", "certificate verify failed", "ssl handshake failed"],
        "escalation_route": "service-owner -> platform-security/networking",
    },
    "packet_loss_suspected": {
        "display_name": "Packet loss suspected",
        "symptoms": ["connection reset by peer", "broken pipe", "eof during transfer", "read: connection reset"],
        "escalation_route": "service-owner -> platform-networking",
    },
    "service_unreachable": {
        "display_name": "Service unreachable",
        "symptoms": ["connection refused", "no route to host", "host unreachable", "service unavailable"],
        "escalation_route": "service-owner -> platform-networking -> owning service",
    },
    "dependency_latency_spike": {
        "display_name": "Dependency latency spike",
        "symptoms": ["deadline exceeded", "upstream timeout", "latency spike", "slow dependency"],
        "escalation_route": "service-owner -> owning dependency team",
    },
    "route_path_change_suspected": {
        "display_name": "Route/path change suspicion",
        "symptoms": ["asymmetric route", "reroute suspected", "path change", "increased hop count"],
        "escalation_route": "platform-networking",
    },
    "intermittent_network_flap": {
        "display_name": "Intermittent network flap",
        "symptoms": ["intermittent timeout", "sporadic connect failure", "flapping", "temporary network failure"],
        "escalation_route": "service-owner -> platform-networking",
    },
    "timeout": {
        "display_name": "Generic timeout",
        "symptoms": ["timeout", "timed out", "deadline exceeded"],
        "escalation_route": "service-owner",
    },
}

RUNBOOKS = {
    "dns": {
        "first_checks": [
            "verify resolver health and recent DNS changes",
            "check whether only one hostname/zone is affected",
            "compare failures across regions or nodes",
        ],
        "likely_cause": "resolver issue, bad record, expired/incorrect DNS config, or propagation problem",
        "rollback_guidance": "rollback only if correlated with a recent config/deploy change touching service discovery or DNS config",
        "escalation_route": "service-owner -> platform-networking -> dns/platform team",
        "mitigation_sequence": [
            "retry resolution from multiple hosts/regions",
            "switch to known-good endpoint if available",
            "rollback recent DNS/service-discovery change if correlation is strong",
            "escalate with affected hostnames, regions, and timestamps",
        ],
    },
    "tcp_connect_timeout": {
        "first_checks": [
            "check destination host/port reachability",
            "compare error rate before/after deploy",
            "inspect SYN timeout/connectivity metrics",
        ],
        "likely_cause": "target saturation, firewall/security group issue, or network path problem",
        "rollback_guidance": "rollback if tightly correlated with a new deploy or config change increasing connection attempts",
        "escalation_route": "service-owner -> platform-networking",
        "mitigation_sequence": [
            "verify service endpoints and port bindings",
            "reduce concurrency or fail over",
            "rollback recent deploy if correlation engine flags it",
            "escalate with endpoint list and timestamps",
        ],
    },
    "tls_handshake": {
        "first_checks": [
            "check cert validity and chain",
            "verify cipher/protocol compatibility",
            "inspect mTLS or secret rotation timing",
        ],
        "likely_cause": "expired cert, secret rotation issue, trust-store mismatch, or TLS policy drift",
        "rollback_guidance": "rollback when a release changed certs, secret mounts, or TLS config",
        "escalation_route": "service-owner -> platform-security/networking",
        "mitigation_sequence": [
            "compare cert fingerprint and expiry",
            "revert recent TLS/secret config changes",
            "fail over to known-good endpoint",
            "escalate with exact handshake error and impacted hosts",
        ],
    },
    "packet_loss_suspected": {
        "first_checks": [
            "look for resets/retries/retransmissions",
            "compare failure concentration by host or AZ",
            "check dependency saturation and connection churn",
        ],
        "likely_cause": "transient network instability, saturation, or overloaded upstream",
        "rollback_guidance": "avoid rollback unless clearly deployment-induced; first confirm concentration and timing",
        "escalation_route": "service-owner -> platform-networking",
        "mitigation_sequence": [
            "reduce traffic or retry aggressively with backoff",
            "shift traffic away from hot hosts/AZs",
            "escalate with impacted nodes and time window",
        ],
    },
    "service_unreachable": {
        "first_checks": [
            "verify instance health and endpoint registration",
            "check routing, firewall, and service mesh state",
            "confirm the target is actually running",
        ],
        "likely_cause": "service down, endpoint deregistration, routing issue, or blocking policy",
        "rollback_guidance": "rollback if a recent deploy changed service registration, ports, or traffic policy",
        "escalation_route": "service-owner -> platform-networking -> owning service",
        "mitigation_sequence": [
            "check health checks and endpoint registration",
            "restart/fail over target if appropriate",
            "rollback bad service config or traffic policy",
            "escalate with impacted service names and instances",
        ],
    },
    "dependency_latency_spike": {
        "first_checks": [
            "compare dependency latency before/after deploy",
            "check saturation, retries, and queue depth",
            "inspect 5xx and timeout bursts for the same window",
        ],
        "likely_cause": "upstream saturation, regression, or overloaded dependency",
        "rollback_guidance": "rollback if a release directly increased request volume, concurrency, or expensive calls",
        "escalation_route": "service-owner -> owning dependency team",
        "mitigation_sequence": [
            "de-rate traffic or enable fallback/cache",
            "rollback recent release if correlated",
            "engage dependency owner with latency timeline",
        ],
    },
    "route_path_change_suspected": {
        "first_checks": [
            "compare traceroute/path telemetry before and after incident",
            "check region/AZ concentration",
            "look for simultaneous latency and timeout changes",
        ],
        "likely_cause": "network path change or asymmetric routing issue",
        "rollback_guidance": "no rollback unless a deploy changed egress/routing policy",
        "escalation_route": "platform-networking",
        "mitigation_sequence": [
            "validate affected paths and regions",
            "drain or reroute traffic where possible",
            "escalate with timestamps and affected paths",
        ],
    },
    "intermittent_network_flap": {
        "first_checks": [
            "measure recurrence by host/region",
            "check whether errors cluster around deploys or restarts",
            "look for alternating success/failure patterns",
        ],
        "likely_cause": "unstable network path, dependency instability, or intermittent host health",
        "rollback_guidance": "rollback only with strong timing correlation to recent changes",
        "escalation_route": "service-owner -> platform-networking",
        "mitigation_sequence": [
            "identify hot hosts/regions",
            "shift traffic away from unstable segments",
            "escalate with recurrence timeline and impacted services",
        ],
    },
    "timeout": {
        "first_checks": [
            "find the exact operation timing out",
            "compare latency and retries before/after changes",
            "check for correlated upstream errors",
        ],
        "likely_cause": "slow dependency, saturation, or network path issue",
        "rollback_guidance": "rollback if correlation to a recent deploy is strong",
        "escalation_route": "service-owner",
        "mitigation_sequence": [
            "identify the slow dependency",
            "reduce concurrency or fail over",
            "rollback recent changes if needed",
        ],
    },
}
