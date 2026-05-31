import json
from pathlib import Path

from incident_trends.analyze_incident_trends import analyze_trends

def test_incident_trend_detects_top_growth_family():
    history = json.loads(Path("incident_trends/incident_history.json").read_text())
    summary = analyze_trends(history)

    assert summary["top_incident"] == "retry_storm"
    assert summary["increase"] == "+33.3%"
    assert summary["trend_status"] == "investigate"
    assert len(summary["family_trends"]) == 3
