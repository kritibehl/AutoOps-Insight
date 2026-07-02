import json
from pathlib import Path

from network_triage.network_failure_triage import triage_network_incidents


def test_network_failure_triage_outputs_commands_and_severity():
    incidents = json.loads(Path("examples/network_failure_queue.json").read_text())
    summary = triage_network_incidents(incidents)

    assert summary["network_incidents_reviewed"] == 3
    assert summary["triage_status"] == "PASS"

    tcp = next(i for i in summary["triaged_incidents"] if i["failure_family"] == "tcp_timeout")
    assert tcp["severity"] == "sev1"
    assert "nc -vz <host> <port>" in tcp["recommended_first_commands"]
    assert "network_production_engineering" in tcp["escalation_path"]
