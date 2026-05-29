import json
from pathlib import Path

MODEL_RUNS = [
    {
        "model": "support-priority-classifier",
        "baseline_accuracy": 0.91,
        "current_accuracy": 0.84,
        "baseline_latency_ms": 180,
        "current_latency_ms": 260,
        "feature_shift": {
            "ticket_length": 0.21,
            "customer_region": 0.18,
            "issue_type": 0.09
        }
    },
    {
        "model": "incident-routing-model",
        "baseline_accuracy": 0.88,
        "current_accuracy": 0.87,
        "baseline_latency_ms": 140,
        "current_latency_ms": 155,
        "feature_shift": {
            "severity": 0.04,
            "service": 0.06
        }
    },
    {
        "model": "runbook-recommendation-model",
        "baseline_accuracy": 0.86,
        "current_accuracy": 0.79,
        "baseline_latency_ms": 210,
        "current_latency_ms": 390,
        "feature_shift": {
            "incident_family": 0.24,
            "service_owner": 0.13
        }
    }
]

DRIFT_THRESHOLD = 0.15
QUALITY_DROP_THRESHOLD = 0.05
LATENCY_INCREASE_THRESHOLD = 0.35


def evaluate_model_health(run):
    accuracy_drop = round(run["baseline_accuracy"] - run["current_accuracy"], 4)
    latency_increase_pct = round(
        (run["current_latency_ms"] - run["baseline_latency_ms"]) / run["baseline_latency_ms"],
        4
    )

    drifted_features = [
        feature
        for feature, shift in run["feature_shift"].items()
        if shift >= DRIFT_THRESHOLD
    ]

    feature_drift_detected = len(drifted_features) > 0
    quality_regression = accuracy_drop >= QUALITY_DROP_THRESHOLD
    latency_regression = latency_increase_pct >= LATENCY_INCREASE_THRESHOLD

    model_health = (
        "degraded"
        if feature_drift_detected or quality_regression or latency_regression
        else "healthy"
    )

    return {
        "model": run["model"],
        "model_health": model_health,
        "baseline_accuracy": run["baseline_accuracy"],
        "current_accuracy": run["current_accuracy"],
        "accuracy_drop": accuracy_drop,
        "feature_drift_detected": feature_drift_detected,
        "drifted_features": drifted_features,
        "quality_regression": quality_regression,
        "latency_regression": latency_regression,
        "latency_increase_pct": latency_increase_pct,
        "recommended_action": (
            "review training data and recent production traffic distribution"
            if model_health == "degraded"
            else "continue monitoring"
        )
    }


def summarize_model_health(model_runs):
    evaluations = [evaluate_model_health(run) for run in model_runs]

    degraded = [e for e in evaluations if e["model_health"] == "degraded"]

    dashboard = {
        "models_monitored": len(evaluations),
        "healthy_models": len(evaluations) - len(degraded),
        "degraded_models": len(degraded),
        "feature_drift_alerts": sum(1 for e in evaluations if e["feature_drift_detected"]),
        "quality_regressions": sum(1 for e in evaluations if e["quality_regression"]),
        "latency_regressions": sum(1 for e in evaluations if e["latency_regression"]),
        "model_evaluations": evaluations,
        "monitoring_status": "REVIEW" if degraded else "PASS"
    }

    return dashboard


def main():
    dashboard = summarize_model_health(MODEL_RUNS)

    Path("ml_monitoring/model_health_dashboard.json").write_text(
        json.dumps(dashboard, indent=2)
    )

    quality_metrics = {
        "models_monitored": dashboard["models_monitored"],
        "healthy_models": dashboard["healthy_models"],
        "degraded_models": dashboard["degraded_models"],
        "quality_regressions": dashboard["quality_regressions"],
        "latency_regressions": dashboard["latency_regressions"],
        "feature_drift_alerts": dashboard["feature_drift_alerts"],
    }

    Path("ml_monitoring/prediction_quality_metrics.json").write_text(
        json.dumps(quality_metrics, indent=2)
    )

    drift_lines = []
    for model in dashboard["model_evaluations"]:
        drift_lines.append(
            f"- {model['model']}: health={model['model_health']}, "
            f"drifted_features={model['drifted_features']}, "
            f"accuracy_drop={model['accuracy_drop']}"
        )

    report = f"""# ML Feature Drift Report

## Summary

- Models monitored: {dashboard["models_monitored"]}
- Healthy models: {dashboard["healthy_models"]}
- Degraded models: {dashboard["degraded_models"]}
- Feature drift alerts: {dashboard["feature_drift_alerts"]}
- Quality regressions: {dashboard["quality_regressions"]}
- Latency regressions: {dashboard["latency_regressions"]}

## Model-level drift review

{chr(10).join(drift_lines)}

## Operational interpretation

AutoOps tracks model-health signals for support and incident workflows, including feature drift, prediction-quality regression, latency regression, and dashboard-ready model status summaries.
"""

    Path("ml_monitoring/feature_drift_report.md").write_text(report)

    print(json.dumps(dashboard, indent=2))


if __name__ == "__main__":
    main()
