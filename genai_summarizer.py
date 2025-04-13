import re

KEYWORDS = [
    "error", "exception", "failed", "fatal", "undefined", "cannot", "denied", "traceback"
]

def summarize_log(log_text: str) -> str:
    lines = log_text.strip().splitlines()
    important_lines = []

    for line in lines:
        if any(keyword in line.lower() for keyword in KEYWORDS):
            important_lines.append(line.strip())

    if not important_lines:
        return "No obvious errors found in the log."

    summary = f"Top issue(s) detected:\n- " + "\n- ".join(important_lines[:3])
    return summary
