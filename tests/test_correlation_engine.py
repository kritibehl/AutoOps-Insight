from correlation_engine.incident_graph import build_incident_graph, summarize_graph
from correlation_engine.root_cause_ranker import rank_root_causes

def test_correlation_groups_events_by_trace_id():
    events = [
        {"trace_id": "t1", "source": "agentgrid", "issue_family": "missing_context", "action": "support_review"},
        {"trace_id": "t1", "source": "autoops", "issue_family": "retrieval_failure", "action": "fix_retrieval_pipeline"},
    ]

    graph = build_incident_graph(events)
    summary = summarize_graph(graph)

    assert len(graph) == 1
    assert summary[0]["event_count"] == 2
    assert "agentgrid" in summary[0]["sources"]
    assert "autoops" in summary[0]["sources"]

def test_root_cause_ranker_prioritizes_recurrent_escalated_causes():
    events = [
        {
            "issue_family": "retrieval_failure",
            "root_cause": "retrieval_or_context_pipeline_failure",
            "recurrence_total": 3,
            "escalation_required": True,
        },
        {
            "issue_family": "wrong_answer",
            "root_cause": "model_reasoning_or_prompt_issue",
            "recurrence_total": 1,
            "escalation_required": False,
        },
    ]

    ranked = rank_root_causes(events)

    assert ranked[0]["root_cause"] == "retrieval_or_context_pipeline_failure"
