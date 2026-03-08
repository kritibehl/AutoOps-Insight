from analysis.signatures import compute_signature, normalize_log_text


def test_signature_is_stable_for_same_input():
    log_text = "ERROR: timeout connecting to 10.0.0.1 after 30 seconds"
    sig1 = compute_signature(log_text, "timeout")
    sig2 = compute_signature(log_text, "timeout")
    assert sig1 == sig2


def test_signature_changes_with_family():
    log_text = "ERROR: timeout connecting to service"
    sig1 = compute_signature(log_text, "timeout")
    sig2 = compute_signature(log_text, "dependency_unavailable")
    assert sig1 != sig2


def test_normalization_reduces_volatile_values():
    log_text = "ERROR 2026-03-08T01:45:06Z request to 10.0.0.1 failed after 30 seconds"
    normalized = normalize_log_text(log_text)
    assert "<timestamp>" in normalized or "2026-03-08" not in normalized
