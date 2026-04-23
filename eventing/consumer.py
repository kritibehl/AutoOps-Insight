import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
from kafka import KafkaConsumer

from ml_predictor import analyze_log_text
from storage.history import record_analysis

def main():
    consumer = KafkaConsumer(
        "ci.failures",
        bootstrap_servers="localhost:9092",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="autoops-consumer",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

    print("listening on topic ci.failures...")

    for message in consumer:
        event = message.value
        result = analyze_log_text(event["log_text"])
        enriched = record_analysis(
            result,
            filename="kafka_event.log",
            repo_name=event.get("repo"),
            workflow_name=event.get("workflow"),
            run_id=event.get("run_id"),
            raw_text=event.get("log_text"),
        )
        print("processed:", {
            "repo": event.get("repo"),
            "workflow": event.get("workflow"),
            "run_id": event.get("run_id"),
            "incident_type": enriched["incident_type"],
            "signature": enriched["signature"],
            "release_decision": enriched["release_decision"],
            "decision_confidence": enriched["decision_confidence"],
        })

if __name__ == "__main__":
    main()
