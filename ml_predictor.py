import hashlib

def detect_failure_family(text: str) -> str:
    t = text.lower()
    if "dns" in t or "no such host" in t:
        return "dns_failure"
    if "timeout" in t:
        return "timeout"
    if "latency" in t:
        return "latency_spike"
    if "connection refused" in t or "service unreachable" in t:
        return "service_unreachable"
    if "tls" in t or "certificate" in t:
        return "tls_handshake"
    return "unknown"

def extract_evidence_lines(text: str):
    lines = [line.strip() for line in text.splitlines()]
    hits = [line for line in lines if "error" in line.lower() or "warn" in line.lower()]
    return hits if hits else lines[:2]

def analyze_log_text(text: str):
    failure_family = detect_failure_family(text)
    evidence = extract_evidence_lines(text)
    signature = f"{failure_family}:{hashlib.md5(text.encode()).hexdigest()[:16]}"
    severity = "high" if "error" in text.lower() else "medium"

    return {
        "predicted_issue": failure_family,
        "incident_type": failure_family,
        "signature": signature,
        "failure_family": failure_family,
        "severity": severity,
        "summary": f"Detected failure family: {failure_family}. Key evidence: " + "; ".join(evidence[:2]),
        "confidence": 0.91 if failure_family != "unknown" else 0.55,
    }
