import os
import pickle

from analysis.formatter import build_summary
from analysis.signatures import compute_signature
from classifiers.rules import detect_failure_family, extract_evidence_lines
from classifiers.taxonomy import resolve_taxonomy
from schemas.incident import IncidentAnalysis, EvidenceLine

MODEL_PATH = os.getenv("MODEL_PATH", "ml_model/log_model.pkl")

_vectorizer = None
_model = None
_load_error = None


def _load():
    global _vectorizer, _model, _load_error
    if _model is not None and _vectorizer is not None:
        return True
    if _load_error is not None:
        return False

    try:
        with open(MODEL_PATH, "rb") as f:
            _vectorizer, _model = pickle.load(f)
        return True
    except Exception as e:
        _load_error = str(e)
        return False


def _predict_with_ml(log_text: str):
    ok = _load()
    if not ok:
        return "unknown", 0.0, False

    X = _vectorizer.transform([log_text])
    prediction = _model.predict(X)[0]
    proba = float(_model.predict_proba(X).max())
    return str(prediction), round(proba, 2), True


def analyze_log_text(log_text: str) -> dict:
    rule_family, _, matched_rule = detect_failure_family(log_text)
    ml_label, ml_confidence, ml_used = _predict_with_ml(log_text)

    if rule_family:
        final_family = rule_family
        confidence = 0.95
        used_rule_based_detection = True
    else:
        final_family = ml_label
        confidence = ml_confidence
        used_rule_based_detection = False
        matched_rule = None

    taxonomy = resolve_taxonomy(final_family, matched_rule)
    evidence_pairs = extract_evidence_lines(log_text)
    summary = build_summary(final_family, evidence_pairs)
    signature = compute_signature(log_text, final_family)

    result = IncidentAnalysis(
        predicted_issue=final_family,
        confidence=confidence,
        failure_family=final_family,
        severity=taxonomy["severity"],
        signature=signature,
        summary=summary,
        likely_cause=taxonomy["likely_cause"],
        first_remediation_step=taxonomy["first_remediation_step"],
        next_debugging_action=taxonomy["next_debugging_action"],
        probable_owner=taxonomy["probable_owner"],
        release_blocking=taxonomy["release_blocking"],
        evidence=[EvidenceLine(line_number=n, text=t) for n, t in evidence_pairs],
        used_rule_based_detection=used_rule_based_detection,
        used_ml_prediction=ml_used,
    )
    return result.model_dump()


def predict_log_issue(log_text: str):
    result = analyze_log_text(log_text)
    return {
        "predicted_issue": result["predicted_issue"],
        "confidence": result["confidence"],
    }
