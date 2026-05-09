import json
from pathlib import Path

from correlation_engine.incident_graph import build_incident_graph, summarize_graph
from correlation_engine.root_cause_ranker import rank_root_causes

def main():
    path = Path("samples/correlation/agentgrid_autoops_trace.json")
    events = json.loads(path.read_text())

    graph = build_incident_graph(events)
    graph_summary = summarize_graph(graph)
    ranked_causes = rank_root_causes(events)

    report = {
        "correlated_traces": len(graph),
        "events_analyzed": len(events),
        "graph_summary": graph_summary,
        "ranked_root_causes": ranked_causes,
        "top_root_cause": ranked_causes[0] if ranked_causes else None,
    }

    out = Path("artifacts/analytics/correlation_report.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
