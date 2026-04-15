from __future__ import annotations

def calibrate_confidence(rule_confidence: float, ml_confidence: float | None = None) -> dict:
    ml_value = 0.0 if ml_confidence is None else float(ml_confidence)
    rule_value = float(rule_confidence)

    ambiguous = False
    if ml_confidence is not None and abs(rule_value - ml_value) >= 0.25:
        ambiguous = True
    if max(rule_value, ml_value) < 0.70:
        ambiguous = True

    final_conf = rule_value if ml_confidence is None else max(rule_value, ml_value)

    return {
        "rule_based_confidence": round(rule_value, 4),
        "ml_fallback_confidence": round(ml_value, 4),
        "ambiguous_classification": ambiguous,
        "final_confidence": round(final_conf, 4),
    }
