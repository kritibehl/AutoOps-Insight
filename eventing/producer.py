import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
import sys
from kafka import KafkaProducer

def main():
    if len(sys.argv) != 5:
        print("usage: python kafka/producer.py <repo> <workflow> <run_id> <log_file>")
        sys.exit(1)

    repo, workflow, run_id, log_file = sys.argv[1:]
    with open(log_file, "r", encoding="utf-8") as f:
        log_text = f.read()

    event = {
        "repo": repo,
        "workflow": workflow,
        "run_id": run_id,
        "log_text": log_text,
    }

    producer = KafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    producer.send("ci.failures", event)
    producer.flush()
    print("sent:", event)

if __name__ == "__main__":
    main()
