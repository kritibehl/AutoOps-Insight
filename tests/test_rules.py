from classifiers.rules import detect_failure_family, extract_evidence_lines


def test_detect_timeout():
    text = "ERROR: request timed out while contacting registry"
    family, match = detect_failure_family(text)
    assert family == "timeout"
    assert match is not None


def test_detect_connection_refused():
    text = "dial tcp 10.0.0.8:443: connection refused"
    family, match = detect_failure_family(text)
    assert family == "connection_refused"
    assert "connection refused" in match.lower()


def test_detect_retry_exhausted():
    text = "build failed because max retries exceeded"
    family, match = detect_failure_family(text)
    assert family == "retry_exhausted"
    assert match is not None


def test_extract_evidence_lines():
    text = "\n".join([
        "INFO: starting pipeline",
        "ERROR: failed to fetch dependency",
        "WARN: retrying",
        "fatal: timeout while waiting for response",
    ])
    evidence = extract_evidence_lines(text)
    assert len(evidence) >= 2
    assert evidence[0][0] == 2
    assert "failed" in evidence[0][1].lower()
