from __future__ import annotations

from analysis.incident_taxonomy import INCIDENT_TAXONOMY

def infer_network_family(text: str) -> str | None:
    haystack = text.lower()
    for family, meta in INCIDENT_TAXONOMY.items():
        for symptom in meta["symptoms"]:
            if symptom in haystack:
                return family
    return None
