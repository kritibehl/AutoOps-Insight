from __future__ import annotations

import copy
import re
from typing import Any, Dict, List, Optional, Tuple

from classifiers.config_loader import load_rules_config
from classifiers.taxonomy import resolve_taxonomy


def _compile_rules(rules: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], re.Pattern[str]]]:
    compiled = []
    for rule in rules:
        pattern = rule.get("pattern")
        if not pattern:
            continue
        compiled.append((rule, re.compile(pattern, re.I)))
    return compiled


def detect_with_rules(log_text: str, rules: List[Dict[str, Any]]) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    for rule, pattern in _compile_rules(rules):
        if pattern.search(log_text):
            return rule["failure_family"], rule
    return None, None


def simulate_rule_update(rule_id: str, updates: Dict[str, Any], incidents: List[Dict[str, Any]]) -> Dict[str, Any]:
    rules = copy.deepcopy(load_rules_config())

    target_rule = None
    for idx, rule in enumerate(rules):
        if rule.get("id") == rule_id:
            target_rule = copy.deepcopy(rule)
            rules[idx].update(updates)
            break

    if target_rule is None:
        raise ValueError(f"rule_id not found: {rule_id}")

    simulated_rule = None
    for rule in rules:
        if rule.get("id") == rule_id:
            simulated_rule = copy.deepcopy(rule)
            break

    impacted: List[Dict[str, Any]] = []
    evaluated = 0
    reclassified = 0
    severity_changed = 0
    release_blocking_changed = 0
    owner_changed = 0

    for incident in incidents:
        log_text = incident.get("raw_log_text") or "\n".join(
            item.get("text", "") for item in incident.get("evidence", [])
        )
        if not log_text:
            continue

        evaluated += 1

        original_family = incident.get("failure_family")
        original_severity = incident.get("severity")
        original_release_blocking = incident.get("release_blocking")
        original_owner = incident.get("probable_owner")

        new_family, matched_rule = detect_with_rules(log_text, rules)
        if not new_family:
            new_family = original_family

        taxonomy = resolve_taxonomy(new_family, matched_rule)
        new_severity = taxonomy["severity"]
        new_release_blocking = taxonomy["release_blocking"]
        new_owner = taxonomy["probable_owner"]

        changed_fields = []
        if new_family != original_family:
            reclassified += 1
            changed_fields.append("failure_family")
        if new_severity != original_severity:
            severity_changed += 1
            changed_fields.append("severity")
        if bool(new_release_blocking) != bool(original_release_blocking):
            release_blocking_changed += 1
            changed_fields.append("release_blocking")
        if new_owner != original_owner:
            owner_changed += 1
            changed_fields.append("probable_owner")

        if changed_fields:
            impacted.append({
                "id": incident.get("id"),
                "signature": incident.get("signature"),
                "original": {
                    "failure_family": original_family,
                    "severity": original_severity,
                    "release_blocking": original_release_blocking,
                    "probable_owner": original_owner,
                },
                "simulated": {
                    "failure_family": new_family,
                    "severity": new_severity,
                    "release_blocking": new_release_blocking,
                    "probable_owner": new_owner,
                },
                "changed_fields": changed_fields,
            })

    return {
        "rule_id": rule_id,
        "before": target_rule,
        "after": simulated_rule,
        "incidents_evaluated": evaluated,
        "incidents_impacted": len(impacted),
        "reclassified_incidents": reclassified,
        "severity_changed": severity_changed,
        "release_blocking_changed": release_blocking_changed,
        "probable_owner_changed": owner_changed,
        "sample_impacted_incidents": impacted[:10],
    }


def build_rule_diff(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    keys = sorted(set(before.keys()) | set(after.keys()))
    diff = {}
    for key in keys:
        if before.get(key) != after.get(key):
            diff[key] = {
                "before": before.get(key),
                "after": after.get(key),
            }
    return diff
