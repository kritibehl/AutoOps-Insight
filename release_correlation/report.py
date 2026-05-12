import json
from pathlib import Path

from release_correlation.deployment_correlation import (
    correlate_deployments_to_incidents,
    summarize_release_risk,
)

def main():
    deployments = json.loads(Path("samples/release_correlation/deployments.json").read_text())
    incidents = json.loads(Path("samples/release_correlation/incidents_after_deploy.json").read_text())

    correlations = correlate_deployments_to_incidents(deployments, incidents)
    summary = summarize_release_risk(correlations)

    report = {
        "summary": summary,
        "correlations": correlations,
    }

    out = Path("artifacts/analytics/deployment_incident_correlation.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
