from __future__ import annotations

from typing import Any
from analysis.incident_taxonomy import RUNBOOKS

def get_runbook(failure_family: str) -> dict[str, Any]:
    family = failure_family.strip().lower()
    if family in RUNBOOKS:
        return {"failure_family": family, **RUNBOOKS[family]}
    return {
        "failure_family": family,
        "first_checks": [
            "confirm exact failing dependency or endpoint",
            "check error-rate and latency trend around the incident",
            "look for a nearby deploy, config, or traffic shift",
        ],
        "likely_cause": "unknown; requires correlated timeline review",
        "rollback_guidance": "rollback only if timing strongly aligns with a recent change",
        "escalation_route": "service-owner -> relevant platform owner",
        "mitigation_sequence": [
            "contain impact",
            "identify correlated changes",
            "engage owner with timestamps and affected scope",
        ],
    }
