import json
from pathlib import Path

COMMANDS = {
    "dns_resolution_failure": ["dig <host>", "nslookup <host>", "cat /etc/resolv.conf"],
    "tcp_timeout": ["nc -vz <host> <port>", "curl -v <url>", "traceroute <host>"],
    "connection_refused": ["nc -vz <host> <port>", "ss -tulpn", "lsof -i :<port>"],
    "tls_handshake_failure": ["curl -v https://<host>", "openssl s_client -connect <host>:443"],
    "packet_loss": ["ping -c 5 <host>", "traceroute <host>", "tcpdump -i any host <host>"],
    "http_5xx_spike": ["curl -v <url>", "grep 5xx service logs", "check upstream health"],
    "routing_or_reachability_issue": ["ping <host>", "traceroute <host>", "iptables -L -n", "ip route"]
}

ESCALATION = {
    "dns_resolution_failure": ["support_l1", "sre_oncall", "platform_networking"],
    "tcp_timeout": ["support_l1", "sre_oncall", "network_production_engineering"],
    "connection_refused": ["support_l1", "service_owner", "sre_oncall"],
    "tls_handshake_failure": ["support_l1", "security_platform", "service_owner"],
    "packet_loss": ["support_l1", "sre_oncall", "network_production_engineering"],
    "http_5xx_spike": ["support_l1", "backend_owner", "sre_oncall"],
    "routing_or_reachability_issue": ["support_l1", "sre_oncall", "network_production_engineering"]
}


def severity_from_slo(slo_impact):
    if slo_impact == "high":
        return "sev1"
    if slo_impact == "medium":
        return "sev2"
    return "sev3"


def triage_network_incidents(incidents):
    triaged = []

    for incident in incidents:
        family = incident["failure_family"]
        triaged.append({
            "incident_id": incident["incident_id"],
            "failure_family": family,
            "severity": severity_from_slo(incident["slo_impact"]),
            "affected_service": incident["affected_service"],
            "symptom": incident["symptom"],
            "recommended_first_commands": COMMANDS.get(family, ["curl -v <url>", "check service logs"]),
            "escalation_path": ESCALATION.get(family, ["support_l1", "sre_oncall"]),
            "slo_impact": incident["slo_impact"],
            "customer_impact": incident["customer_impact"]
        })

    return {
        "network_incidents_reviewed": len(incidents),
        "triaged_incidents": triaged,
        "supported_failure_families": sorted(COMMANDS.keys()),
        "triage_status": "PASS"
    }


def main():
    incidents = json.loads(Path("examples/network_failure_queue.json").read_text())
    summary = triage_network_incidents(incidents)

    Path("reports/network_failure_triage_summary.json").write_text(
        json.dumps(summary, indent=2)
    )

    rows = "\n".join(
        f"| {i['incident_id']} | {i['failure_family']} | {i['severity']} | {i['affected_service']} | {i['slo_impact']} |"
        for i in summary["triaged_incidents"]
    )

    report = f"""# Network Incident Triage Report

## Summary

- Network incidents reviewed: {summary["network_incidents_reviewed"]}
- Triage status: {summary["triage_status"]}

## Triage table

| Incident | Failure family | Severity | Affected service | SLO impact |
|---|---|---|---|---|
{rows}

## Supported failure families

{chr(10).join(f"- {family}" for family in summary["supported_failure_families"])}

## Operational value

This report classifies network-style incidents, estimates severity from SLO impact, recommends first diagnostic commands, and routes incidents through support/SRE/NPE escalation paths.
"""

    Path("reports/network_incident_triage_report.md").write_text(report)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
