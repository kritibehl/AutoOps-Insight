import json
from pathlib import Path

from postmortem.timeline_builder import INCIDENT, build_postmortem
from alert_correlation.correlate_alerts import correlate_alerts
from runbook_quality.runbook_success_rate import analyze_runbook_quality

def test_postmortem_contains_blameless_review_fields():
    report = build_postmortem(INCIDENT)

    assert report["incident_id"] == "INC-PROD-901"
    assert report["rollback_candidate"] is True
    assert "blameless_note" in report
    assert len(report["corrective_actions"]) >= 3

def test_alert_correlation_groups_families():
    alerts = json.loads(Path("alert_correlation/alert_families.json").read_text())
    result = correlate_alerts(alerts)

    assert result["alerts_received"] == 4
    assert result["incident_families_detected"] >= 2
    assert result["correlation_status"] == "PASS"

def test_runbook_quality_detects_gaps():
    steps = json.loads(Path("runbook_quality/unresolved_steps.json").read_text())
    summary = analyze_runbook_quality(steps)

    assert summary["total_steps_reviewed"] == 4
    assert summary["unresolved_steps"] == 2
    assert summary["escalation_triggers"] == 2
