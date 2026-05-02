def infer_likely_trigger(text: str, failure_family: str):
    t = text.lower()

    if "config" in t or "override" in t or "env" in t:
        return {"likely_trigger": "config_change", "confidence": 0.70}
    if failure_family in {"dns_failure", "service_unreachable"}:
        return {"likely_trigger": "dependency_change", "confidence": 0.68}
    if failure_family in {"timeout", "dependency_latency"}:
        return {"likely_trigger": "latency_regression", "confidence": 0.66}

    return {"likely_trigger": "unknown", "confidence": 0.40}
