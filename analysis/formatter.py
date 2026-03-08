from typing import List, Tuple


def build_summary(failure_family: str, evidence_lines: List[Tuple[int, str]]) -> str:
    if not evidence_lines:
        return f"Detected failure family: {failure_family}. No strong evidence lines were extracted."

    top_lines = "; ".join([f"line {line_no}: {text[:160]}" for line_no, text in evidence_lines[:3]])
    return f"Detected failure family: {failure_family}. Key evidence: {top_lines}"
