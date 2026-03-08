from analysis.trends import (
    compute_failure_family_distribution,
    compute_signature_concentration,
    compute_window_comparison,
    compute_failure_family_window_trend,
)
from analysis.anomalies import detect_anomalies


def make_item(idx, family, signature, release_blocking=True):
    return {
        "id": idx,
        "failure_family": family,
        "signature": signature,
        "release_blocking": release_blocking,
    }


def test_failure_family_distribution():
    items = [
        make_item(1, "timeout", "sig-a"),
        make_item(2, "timeout", "sig-a"),
        make_item(3, "retry_exhausted", "sig-b"),
    ]
    result = compute_failure_family_distribution(items)
    assert result[0]["failure_family"] == "timeout"
    assert result[0]["count"] == 2


def test_signature_concentration():
    items = [
        make_item(1, "timeout", "sig-a"),
        make_item(2, "timeout", "sig-a"),
        make_item(3, "retry_exhausted", "sig-b"),
        make_item(4, "timeout", "sig-a"),
    ]
    result = compute_signature_concentration(items)
    assert result["top_signature"] == "sig-a"
    assert result["top_signature_count"] == 3


def test_window_comparison():
    items = [
        make_item(1, "timeout", "sig-a", True),
        make_item(2, "timeout", "sig-a", True),
        make_item(3, "timeout", "sig-a", True),
        make_item(4, "retry_exhausted", "sig-b", False),
        make_item(5, "retry_exhausted", "sig-b", False),
    ]
    result = compute_window_comparison(items, recent_window_size=2, baseline_window_size=3)
    assert result["recent_window_size"] == 2
    assert result["baseline_window_size"] == 3


def test_family_window_trend():
    items = [
        make_item(1, "timeout", "sig-a"),
        make_item(2, "timeout", "sig-a"),
        make_item(3, "timeout", "sig-a"),
        make_item(4, "retry_exhausted", "sig-b"),
        make_item(5, "dns_failure", "sig-c"),
    ]
    trend = compute_failure_family_window_trend(items, recent_window_size=2, baseline_window_size=3)
    assert isinstance(trend, list)
    assert any(item["failure_family"] == "timeout" for item in trend)


def test_detect_anomalies():
    recent = [
        make_item(1, "timeout", "sig-a", True),
        make_item(2, "timeout", "sig-a", True),
        make_item(3, "timeout", "sig-a", True),
        make_item(4, "timeout", "sig-a", True),
        make_item(5, "retry_exhausted", "sig-b", True),
    ]
    recurring = [
        {
            "signature": "sig-a",
            "failure_family": "timeout",
            "severity": "high",
            "total_count": 5,
        }
    ]
    concentration = {
        "total_items": 5,
        "unique_signatures": 2,
        "top_signature": "sig-a",
        "top_signature_count": 4,
        "top_signature_share_pct": 80.0,
    }
    trend = [
        {"failure_family": "timeout", "recent_count": 4, "baseline_count": 1, "delta": 3}
    ]

    anomalies = detect_anomalies(recent, recurring, concentration, trend)
    assert len(anomalies) >= 2
    assert any(item["type"] == "repeated_signature" for item in anomalies)
