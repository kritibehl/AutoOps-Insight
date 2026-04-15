from __future__ import annotations

from collections import defaultdict

def cluster_by_signature(rows: list[dict]) -> list[dict]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[row.get("signature", "unknown")].append(row)

    items = []
    for signature, members in groups.items():
        items.append(
            {
                "signature": signature,
                "count": len(members),
                "failure_family": members[0].get("failure_family"),
                "severity": members[0].get("severity"),
                "repo_names": sorted({m.get("repo_name") for m in members if m.get("repo_name")}),
            }
        )
    return sorted(items, key=lambda x: x["count"], reverse=True)
