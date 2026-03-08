from collections import Counter
from typing import Any, Dict, List


def compute_failure_family_distribution(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    counts = Counter(item["failure_family"] for item in items)
    total = sum(counts.values()) or 1

    result = []
    for family, count in counts.most_common():
        result.append({
            "failure_family": family,
            "count": count,
            "percentage": round((count / total) * 100.0, 2),
        })
    return result


def compute_signature_concentration(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    signatures = [item["signature"] for item in items]
    counts = Counter(signatures)
    total = len(signatures)

    if total == 0:
        return {
            "total_items": 0,
            "unique_signatures": 0,
            "top_signature": None,
            "top_signature_count": 0,
            "top_signature_share_pct": 0.0,
        }

    top_signature, top_count = counts.most_common(1)[0]
    return {
        "total_items": total,
        "unique_signatures": len(counts),
        "top_signature": top_signature,
        "top_signature_count": top_count,
        "top_signature_share_pct": round((top_count / total) * 100.0, 2),
    }


def compute_window_comparison(
    items: List[Dict[str, Any]],
    recent_window_size: int = 5,
    baseline_window_size: int = 10,
) -> Dict[str, Any]:
    if not items:
        return {
            "recent_window_size": 0,
            "baseline_window_size": 0,
            "recent_release_blocker_rate": 0.0,
            "baseline_release_blocker_rate": 0.0,
            "release_blocker_delta_pct_points": 0.0,
        }

    recent = items[:recent_window_size]
    baseline = items[recent_window_size:recent_window_size + baseline_window_size]

    def blocker_rate(window: List[Dict[str, Any]]) -> float:
        if not window:
            return 0.0
        blockers = sum(1 for item in window if item.get("release_blocking"))
        return round((blockers / len(window)) * 100.0, 2)

    recent_rate = blocker_rate(recent)
    baseline_rate = blocker_rate(baseline)

    return {
        "recent_window_size": len(recent),
        "baseline_window_size": len(baseline),
        "recent_release_blocker_rate": recent_rate,
        "baseline_release_blocker_rate": baseline_rate,
        "release_blocker_delta_pct_points": round(recent_rate - baseline_rate, 2),
    }


def compute_failure_family_window_trend(
    items: List[Dict[str, Any]],
    recent_window_size: int = 5,
    baseline_window_size: int = 10,
) -> List[Dict[str, Any]]:
    recent = items[:recent_window_size]
    baseline = items[recent_window_size:recent_window_size + baseline_window_size]

    recent_counts = Counter(item["failure_family"] for item in recent)
    baseline_counts = Counter(item["failure_family"] for item in baseline)

    families = sorted(set(recent_counts) | set(baseline_counts))
    trend = []

    for family in families:
        recent_count = recent_counts.get(family, 0)
        baseline_count = baseline_counts.get(family, 0)
        trend.append({
            "failure_family": family,
            "recent_count": recent_count,
            "baseline_count": baseline_count,
            "delta": recent_count - baseline_count,
        })

    trend.sort(key=lambda x: (x["delta"], x["recent_count"]), reverse=True)
    return trend
