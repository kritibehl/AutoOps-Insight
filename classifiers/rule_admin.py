from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

from classifiers.config_loader import RULES_CONFIG_PATH, reload_rules_config
from storage.audit import record_audit_event


def update_rule(rule_id: str, updates: Dict[str, Any], actor: str = "local-admin") -> Dict[str, Any]:
    path = Path(RULES_CONFIG_PATH)
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rules = data.get("rules", [])

    for idx, rule in enumerate(rules):
        if rule.get("id") == rule_id:
            before = dict(rule)
            rule.update(updates)
            rules[idx] = rule
            data["rules"] = rules
            path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
            reload_rules_config()
            record_audit_event(
                event_type="rule_update",
                actor=actor,
                rule_id=rule_id,
                change_summary=f"updated fields: {', '.join(sorted(updates.keys()))}",
                before=before,
                after=rule,
            )
            return rule

    raise ValueError(f"rule_id not found: {rule_id}")
