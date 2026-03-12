from __future__ import annotations

import re
from typing import Optional, Tuple, List, Dict, Any

from classifiers.config_loader import load_rules_config

CompiledRule = Tuple[Dict[str, Any], re.Pattern[str]]


def compile_rules() -> List[CompiledRule]:
    compiled: List[CompiledRule] = []
    for rule in load_rules_config():
        pattern = rule.get("pattern")
        if not pattern:
            continue
        compiled.append((rule, re.compile(pattern, re.I)))
    return compiled


def detect_failure_family(log_text: str) -> Tuple[Optional[str], Optional[str], Optional[Dict[str, Any]]]:
    for rule, pattern in compile_rules():
        match = pattern.search(log_text)
        if match:
            return rule["failure_family"], match.group(0), rule
    return None, None, None


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
