from __future__ import annotations

def detect_change_point(recent_count: int, baseline_count: int) -> bool:
    if baseline_count <= 0:
        return recent_count >= 2
    return recent_count >= max(2, baseline_count * 2)
