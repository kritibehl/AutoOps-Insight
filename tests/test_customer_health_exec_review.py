from customer_health.build_customer_health import CUSTOMERS, build_customer_health
from operational_intelligence_graph.build_ops_graph import GRAPH, summarize_graph
from executive_review.generate_exec_review import build_exec_review

def test_customer_health_center_flags_risk():
    summary = build_customer_health(CUSTOMERS)

    assert summary["customers_at_risk"] == 4
    assert summary["escalation_growth"] == "+33.3%"
    assert summary["customer_health_status"] == "review_required"

def test_operational_graph_connects_entities():
    summary = summarize_graph(GRAPH)

    assert summary["node_count"] == 5
    assert summary["edge_count"] == 4
    assert "customer_impact" in summary["relationships"]

def test_executive_review_contains_risks_and_actions():
    review = build_exec_review()

    assert review["review_status"] == "executive_review_required"
    assert len(review["top_risks"]) >= 3
    assert len(review["recommended_actions"]) >= 3
