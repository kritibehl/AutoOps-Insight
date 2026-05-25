from event_ingestion.stream_ingestion import EVENTS, STREAM, DLQ, ingest_event, process_until_idle, list_dlq
from incident_lifecycle.lifecycle import INCIDENTS, create_incident, transition_incident, assign_incident, search_incidents


def setup_function():
    EVENTS.clear()
    STREAM.clear()
    DLQ.clear()
    INCIDENTS.clear()


def test_event_ingestion_processes_success():
    event = ingest_event("agentgrid", "eval_gate_hold", {"trace_id": "trace_1"})
    result = process_until_idle()

    assert result["dlq_depth"] == 0
    assert EVENTS[event["event_id"]].status == "processed"


def test_failed_event_dead_letters():
    event = ingest_event("agentgrid", "tool_failure", {"force_failure": True}, max_attempts=2)
    process_until_idle(limit=5)

    assert EVENTS[event["event_id"]].status == "dead_lettered"
    assert len(list_dlq()) == 1


def test_incident_lifecycle_transition():
    incident = create_incident("Unsupported GenAI answer", "high")
    assign_incident(incident["incident_id"], "ai_support_engineering", "incident_manager")
    transitioned = transition_incident(incident["incident_id"], "triaged", "support_agent", "validated eval-gate hold")

    assert transitioned["status"] == "triaged"
    assert search_incidents("GenAI")
