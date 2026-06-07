import json
from pathlib import Path

GRAPH = {
    "nodes": [
        {"id": "INC-204", "type": "incident", "label": "latency spike after release"},
        {"id": "checkout-api", "type": "service", "label": "checkout-api"},
        {"id": "release-204", "type": "release", "label": "release-204"},
        {"id": "enterprise_alpha", "type": "customer", "label": "enterprise_alpha"},
        {"id": "payment-api", "type": "dependency", "label": "payment-api"}
    ],
    "edges": [
        {"from": "INC-204", "to": "checkout-api", "relationship": "affected_service"},
        {"from": "INC-204", "to": "release-204", "relationship": "correlated_release"},
        {"from": "INC-204", "to": "enterprise_alpha", "relationship": "customer_impact"},
        {"from": "checkout-api", "to": "payment-api", "relationship": "upstream_dependency"}
    ]
}

def summarize_graph(graph):
    type_counts = {}
    for node in graph["nodes"]:
        type_counts[node["type"]] = type_counts.get(node["type"], 0) + 1

    relationships = [edge["relationship"] for edge in graph["edges"]]

    return {
        "node_count": len(graph["nodes"]),
        "edge_count": len(graph["edges"]),
        "node_types": type_counts,
        "relationships": relationships,
        "graph_status": "ready_for_incident_review"
    }

def main():
    summary = summarize_graph(GRAPH)
    Path("operational_intelligence_graph/ops_graph.json").write_text(json.dumps(GRAPH, indent=2))
    Path("operational_intelligence_graph/ops_graph_summary.json").write_text(json.dumps(summary, indent=2))

    report = f"""# Operational Intelligence Graph

## Connected entities

- incident
- service
- release
- customer
- dependency

## Summary

- Nodes: {summary["node_count"]}
- Edges: {summary["edge_count"]}
- Status: {summary["graph_status"]}

## Operational value

This graph connects incidents, services, releases, customers, and dependencies so support and SRE teams can reason about blast radius, customer impact, and release correlation.
"""
    Path("operational_intelligence_graph/ops_graph_report.md").write_text(report)
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
