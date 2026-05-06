from __future__ import annotations

def recurrence_prediction(total_count: int) -> float:
    if total_count <= 1:
        return 0.22
    if total_count == 2:
        return 0.58
    if total_count == 3:
        return 0.74
    return 0.87
