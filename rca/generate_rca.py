import json
from pathlib import Path

def generate_markdown(data: dict) -> str:
    timeline_rows = "\n".join(
        f"| {item['timestamp']} | {item['event']} |"
        for item in data["timeline"]
    )

    impacted = "\n".join(f"- {svc}" for svc in data["impacted_services"])
    actions = "\n".join(f"{idx}. {action}" for idx, action in enumerate(data["next_actions"], 1))

    deployment = data["linked_deployment"]

    return f"""# Incident RCA — {deployment['service']} Release Risk

## Incident ID

{data['incident_id']}

## Summary

AutoOps correlated deployment `{deployment['deployment_id']}` for `{deployment['service']}` with a post-release incident spike. The release was marked as `{data['release_risk']}` risk and rollback_candidate={str(data['rollback_candidate']).lower()}.

## Probable cause

{data['probable_cause']}

## Impacted services

{impacted}

## Timeline

| Timestamp | Event |
|---|---|
{timeline_rows}

## Rollback candidate

{data['rollback_candidate']}

## Release risk

{data['release_risk']}

## Next actions

{actions}
"""

def main():
    path = Path("rca/escalation_chain.json")
    data = json.loads(path.read_text())
    output = generate_markdown(data)

    out = Path("rca/generated_rca_example.md")
    out.write_text(output)
    print(output)

if __name__ == "__main__":
    main()
