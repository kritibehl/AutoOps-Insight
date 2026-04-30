import requests
import json

API = "http://127.0.0.1:8001/incidents"

def fetch():
    res = requests.get(API)
    data = res.json()["items"]
    return data

def normalize(data):
    normalized = []
    for row in data:
        normalized.append({
            "repo": row["repo_name"],
            "failure_family": row["failure_family"],
            "incident_type": row["incident_type"],
            "action": row["action"],
            "confidence": row["confidence"],
            "recurrence": row["recurrence_total"]
        })
    return normalized

if __name__ == "__main__":
    data = fetch()
    norm = normalize(data)

    with open("normalized_incidents.json", "w") as f:
        json.dump(norm, f, indent=2)

    print("Normalized incidents written")
