import re
from typing import Optional, Tuple, List

RULES: List[Tuple[str, re.Pattern[str]]] = [
    ("oom", re.compile(r"(out of memory|oomkilled|oom killed|killed process .* out of memory)", re.I)),
    ("dns_failure", re.compile(r"(temporary failure in name resolution|getaddrinfo|no such host|dns)", re.I)),
    ("connection_refused", re.compile(r"(connection refused|actively refused)", re.I)),
    ("tls_failure", re.compile(r"(tls handshake|certificate verify failed|x509|ssl: certificate)", re.I)),
    ("retry_exhausted", re.compile(r"(retry exhausted|max retries exceeded|too many retries)", re.I)),
    ("timeout", re.compile(r"(timed out|timeout|deadline exceeded)", re.I)),
    ("dependency_unavailable", re.compile(r"(service unavailable|503|dependency unavailable|upstream unavailable)", re.I)),
    ("crash_loop", re.compile(r"(crashloopbackoff|back-off restarting failed container|segmentation fault|fatal signal)", re.I)),
    ("flaky_test_signature", re.compile(r"(flaky|intermittent|non-deterministic|passed on retry|rerun passed)", re.I)),
    ("latency_spike", re.compile(r"(latency spike|p95|p99|slow request|response time)", re.I)),
    ("dependency_error", re.compile(r"(dependency error|module not found|package .* not found|artifact .* not found|failed to resolve)", re.I)),
]


def detect_failure_family(log_text: str) -> Tuple[Optional[str], Optional[str]]:
    for family, pattern in RULES:
        match = pattern.search(log_text)
        if match:
            return family, match.group(0)
    return None, None


def extract_evidence_lines(log_text: str, max_lines: int = 5):
    evidence = []
    for idx, line in enumerate(log_text.splitlines(), start=1):
        lowered = line.lower()
        if any(token in lowered for token in [
            "error", "exception", "failed", "fatal", "denied", "timeout",
            "timed out", "oom", "refused", "tls", "retry", "unavailable", "traceback"
        ]):
            evidence.append((idx, line.strip()))
        if len(evidence) >= max_lines:
            break
    return evidence
