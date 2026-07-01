import json
from pathlib import Path

from bug_triage.bug_triage_pipeline import triage_bugs


def test_bug_triage_pipeline_classifies_and_prioritizes():
    bugs = json.loads(Path("examples/bug_queue_sample.json").read_text())
    summary = triage_bugs(bugs)

    assert summary["bugs_reviewed"] == 3
    assert summary["p0_review_count"] == 1
    assert summary["pipeline_status"] == "PASS"
    assert any(b["priority"] == "p0_review" for b in summary["triaged_bugs"])
    assert any(b["regression_risk"] == "medium" for b in summary["triaged_bugs"])
