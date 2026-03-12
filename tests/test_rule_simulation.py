from classifiers.simulation import build_rule_diff, simulate_rule_update


def test_build_rule_diff():
    before = {"id": "timeout_rule", "probable_owner": "service-owner", "severity": "high"}
    after = {"id": "timeout_rule", "probable_owner": "platform-networking", "severity": "high"}

    diff = build_rule_diff(before, after)
    assert "probable_owner" in diff
    assert diff["probable_owner"]["before"] == "service-owner"
    assert diff["probable_owner"]["after"] == "platform-networking"


def test_simulate_rule_update_owner_change():
    incidents = [
        {
            "id": 1,
            "failure_family": "timeout",
            "severity": "high",
            "release_blocking": True,
            "probable_owner": "service-owner",
            "signature": "timeout:abc",
            "evidence": [
                {"line_number": 1, "text": "ERROR: request timeout while contacting registry"}
            ],
            "raw_log_text": "ERROR: request timeout while contacting registry",
        }
    ]

    result = simulate_rule_update(
        "timeout_rule",
        {"probable_owner": "platform-networking"},
        incidents,
    )

    assert result["incidents_evaluated"] == 1
    assert result["incidents_impacted"] == 1
    assert result["probable_owner_changed"] == 1
    assert result["sample_impacted_incidents"][0]["simulated"]["probable_owner"] == "platform-networking"
