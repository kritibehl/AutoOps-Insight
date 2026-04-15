from __future__ import annotations

from collections import Counter, defaultdict

def service_level_recurrence_heatmap(rows: list[dict]) -> list[dict]:
    heat = defaultdict(int)
    for row in rows:
        service = row.get("repo_name") or "unknown"
        family = row.get("failure_family") or "unknown"
        heat[(service, family)] += 1

    return [
        {"service": service, "failure_family": family, "count": count}
        for (service, family), count in sorted(heat.items(), key=lambda x: (-x[1], x[0][0], x[0][1]))
    ]

def top_noisy_components(rows: list[dict], limit: int = 10) -> list[dict]:
    counts = Counter((row.get("repo_name") or "unknown") for row in rows)
    return [{"component": name, "count": count} for name, count in counts.most_common(limit)]

def release_window_blast_radius(rows: list[dict]) -> dict:
    affected_components = sorted({row.get("repo_name") for row in rows if row.get("repo_name")})
    affected_families = Counter((row.get("failure_family") or "unknown") for row in rows)
    return {
        "affected_component_count": len(affected_components),
        "affected_components": affected_components,
        "failure_family_counts": dict(affected_families),
    }
