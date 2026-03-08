import hashlib
import re


VOLATILE_PATTERNS = [
    (re.compile(r"\b[0-9a-f]{7,64}\b", re.I), "<hex>"),
    (re.compile(r"\b\d+\b"), "<num>"),
    (re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b"), "<ip>"),
    (re.compile(r"\b[0-9]{4}-[0-9]{2}-[0-9]{2}[tT ][0-9:\.\-+zZ]+\b"), "<timestamp>"),
]


def normalize_log_text(log_text: str) -> str:
    normalized_lines = []
    for raw in log_text.splitlines():
        line = raw.strip().lower()
        if not line:
            continue
        for pattern, replacement in VOLATILE_PATTERNS:
            line = pattern.sub(replacement, line)
        if any(token in line for token in [
            "error", "exception", "failed", "fatal", "timeout", "timed out",
            "refused", "oom", "retry", "unavailable", "traceback", "tls", "certificate"
        ]):
            normalized_lines.append(line)
        if len(normalized_lines) >= 8:
            break
    return "\n".join(normalized_lines) if normalized_lines else log_text[:500].lower()


def compute_signature(log_text: str, failure_family: str) -> str:
    normalized = normalize_log_text(log_text)
    digest = hashlib.sha256(f"{failure_family}::{normalized}".encode("utf-8")).hexdigest()[:16]
    return f"{failure_family}:{digest}"
