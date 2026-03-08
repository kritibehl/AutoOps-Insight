from reports.renderer import render_markdown_report


def test_render_markdown_report_contains_expected_sections():
    summary = {
        "total_analyses": 4,
        "release_blockers": 3,
        "release_risk": "high",
        "top_failure_families": [
            {"failure_family": "timeout", "total_count": 3}
        ],
        "top_recurring_signatures": [
            {
                "signature": "timeout:abc123",
                "failure_family": "timeout",
                "severity": "high",
                "total_count": 3,
                "first_seen": "t1",
                "last_seen": "t2",
            }
        ],
        "recent_analyses": [
            {
                "id": 1,
                "created_at": "t1",
                "failure_family": "timeout",
                "severity": "high",
                "signature": "timeout:abc123",
                "release_blocking": True,
            }
        ],
        "recent_failure_family_distribution": [
            {"failure_family": "timeout", "count": 3, "percentage": 100.0}
        ],
        "recent_signature_concentration": {
            "total_items": 3,
            "unique_signatures": 1,
            "top_signature": "timeout:abc123",
            "top_signature_count": 3,
            "top_signature_share_pct": 100.0,
        },
        "window_comparison": {
            "recent_window_size": 3,
            "baseline_window_size": 2,
            "recent_release_blocker_rate": 100.0,
            "baseline_release_blocker_rate": 50.0,
            "release_blocker_delta_pct_points": 50.0,
        },
        "recent_family_trend": [
            {"failure_family": "timeout", "recent_count": 3, "baseline_count": 1, "delta": 2}
        ],
        "anomalies": [
            {"type": "repeated_signature", "severity": "high", "message": "Repeated issue"}
        ],
    }

    markdown = render_markdown_report(summary)
    assert "## Release Risk Summary" in markdown
    assert "## Top Recurring Signatures" in markdown
    assert "## Detected Anomalies" in markdown
    assert "timeout:abc123" in markdown
